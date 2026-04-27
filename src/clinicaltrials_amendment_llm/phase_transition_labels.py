"""Day 12-13 phase transition label generator.

Builds binary labels: did a (drug, sponsor) cluster advance from Phase X to
Phase X+1 within an observation window? Used as the outcome label for
CTP-LLM phase-transition baseline replication (Day 13) + Phase 1 trigger #1
(ROC-AUC).

Approach (without paid Citeline/CSDD):
1. Group CT.gov records by (sponsor_name_norm, drug_name_norm).
2. For each cluster, check if Phase X and Phase X+1 trials both exist.
3. Label Phase X trial: transitioned_to_X+1 = True if next-phase trial found
   with study_first_submit_date later by 6-60 months; False otherwise.

Limitations:
- Drug names can vary across phases (codenames -> trade names). We use
  fuzzy match on the first interventionName.
- Some drugs go Phase 1 -> Phase 3 directly. We treat as transition still.
- Open-label extensions may confound. We require Phase number to strictly
  increase.

This is the *approximate* outcome label, NOT a definitive ground truth like
Citeline. Day 14 mid-checkpoint will report it as such.
"""

from __future__ import annotations

import asyncio
import re
from collections import defaultdict
from datetime import datetime, timezone

from clinicaltrials_amendment_llm.biotech_universe import normalize_sponsor_name
from clinicaltrials_amendment_llm.ctgov_client import fetch_study
from clinicaltrials_amendment_llm.manifest import (
    MANIFEST_AMENDMENT_FETCH,
    MANIFEST_PHASE_TRANSITION,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)


_DRUG_SUFFIX_RE = re.compile(
    r"\b(injection|tablet|capsule|solution|suspension|oral|iv|sc|im|infusion|"
    r"hcl|hydrochloride|sodium|sulphate|sulfate|phosphate|fumarate|maleate|"
    r"mesylate|tosylate|monohydrate|dihydrate)\b",
    re.IGNORECASE,
)


def _normalize_drug_name(name: str) -> str:
    if not name:
        return ""
    n = name.lower().strip()
    n = _DRUG_SUFFIX_RE.sub(" ", n)
    n = re.sub(r"[^a-z0-9 ]+", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def _phase_to_int(phase: str) -> int | None:
    if not phase:
        return None
    if phase in ("PHASE1", "EARLY_PHASE1"):
        return 1
    if phase == "PHASE2":
        return 2
    if phase == "PHASE3":
        return 3
    if phase == "PHASE4":
        return 4
    return None


def _months_between(d1: str, d2: str) -> float | None:
    try:
        a = datetime.fromisoformat(d1)
        b = datetime.fromisoformat(d2)
        return (b - a).days / 30.4375
    except Exception:
        return None


async def _fetch_intervention(nct: str) -> str | None:
    """Fetch intervention name (first one) for a given NCT."""
    try:
        rec = await fetch_study(nct)
        ints = rec.get("protocolSection", {}).get("armsInterventionsModule", {}).get("interventions", [])
        if ints and isinstance(ints, list):
            return ints[0].get("name")
    except Exception:
        return None
    return None


async def enrich_with_interventions(ncts: list[str], concurrency: int = 8) -> dict[str, str]:
    """Concurrently fetch intervention names. Returns {nct: drug_name}."""
    sem = asyncio.Semaphore(concurrency)

    async def one(nct: str) -> tuple[str, str | None]:
        async with sem:
            return nct, await _fetch_intervention(nct)

    results = await asyncio.gather(*(one(n) for n in ncts))
    return {n: d for n, d in results if d}


def build_labels(max_window_months: int = 60) -> dict:
    """Compute phase transition labels.

    For each Phase X trial, look for a Phase X+1 trial with same (sponsor, drug)
    submitted within max_window_months months *after* the Phase X submission.
    If found -> transitioned_to_x_plus_1 = True.
    """
    ensure_data_dir()
    records = list(read_manifest(MANIFEST_AMENDMENT_FETCH))
    print(f"Records: {len(records)}")

    # Need intervention names. Fetch for all unique NCTs (concurrent).
    ncts = list({r["nct_id"] for r in records if r.get("nct_id")})
    print(f"Fetching intervention names for {len(ncts)} unique NCTs (this is daemon-free CT.gov v2) ...")
    drug_map = asyncio.run(enrich_with_interventions(ncts))
    print(f"  intervention names fetched: {len(drug_map)} / {len(ncts)}")

    # Group by (sponsor, drug)
    clusters: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in records:
        nct = r.get("nct_id")
        sponsor = normalize_sponsor_name(r.get("sponsor_name", ""))
        drug = _normalize_drug_name(drug_map.get(nct, ""))
        if not sponsor or not drug or len(drug) < 3:
            continue
        clusters[(sponsor, drug)].append(r)

    print(f"Clusters: {len(clusters)}")

    # Build labels
    n_labeled = 0
    n_transitioned = 0
    by_phase: dict[int, dict] = defaultdict(lambda: {"total": 0, "transitioned": 0})
    for (sponsor, drug), trials in clusters.items():
        # Sort by phase + first_submit_date
        for trial in trials:
            phase_int = None
            phases = trial.get("phase") or []
            for p in phases:
                pi = _phase_to_int(p)
                if pi is not None:
                    phase_int = max(phase_int or 0, pi)
            if phase_int is None or phase_int >= 4:
                continue
            sd = trial.get("study_first_submit_date")
            if not sd:
                continue
            # Look for next-phase trial in same cluster, submitted later
            target_phase = phase_int + 1
            transitioned = False
            for other in trials:
                if other is trial:
                    continue
                op = other.get("phase") or []
                op_int = max((_phase_to_int(p) or 0) for p in op) if op else 0
                if op_int != target_phase:
                    continue
                osd = other.get("study_first_submit_date")
                if not osd:
                    continue
                m = _months_between(sd, osd)
                if m is not None and 0 < m <= max_window_months:
                    transitioned = True
                    break

            n_labeled += 1
            by_phase[phase_int]["total"] += 1
            if transitioned:
                n_transitioned += 1
                by_phase[phase_int]["transitioned"] += 1

            append_manifest(MANIFEST_PHASE_TRANSITION, {
                "nct_id": trial["nct_id"],
                "sponsor_norm": sponsor,
                "drug_norm": drug,
                "phase": phase_int,
                "target_phase": target_phase,
                "transitioned": transitioned,
                "study_first_submit_date": sd,
                "labeled_at": datetime.now(tz=timezone.utc).isoformat(),
            })

    return {
        "n_records": len(records),
        "n_unique_ncts": len(ncts),
        "n_clusters": len(clusters),
        "n_labeled": n_labeled,
        "n_transitioned": n_transitioned,
        "transition_rate": round(n_transitioned / max(n_labeled, 1), 4),
        "by_phase": {
            f"phase_{p}_to_{p+1}": {
                "total": v["total"],
                "transitioned": v["transitioned"],
                "rate": round(v["transitioned"] / max(v["total"], 1), 4),
            }
            for p, v in sorted(by_phase.items())
        },
    }


if __name__ == "__main__":
    import json
    res = build_labels()
    print(json.dumps(res, indent=2))
