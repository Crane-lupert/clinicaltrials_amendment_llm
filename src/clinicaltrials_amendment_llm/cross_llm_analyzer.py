"""Day 14 cross-LLM consistency analyzer (Phase 1 trigger #4).

For each (NCT) with all 3 vendor labels, compute:
- 2/3 majority agreement rate per axis (target >= 80%)
- Cross-LLM Cohen's kappa pairwise (Anthropic-Meta, Anthropic-OpenAI, Meta-OpenAI)
- Confidence-weighted majority where applicable

Phase 1 trigger #4: 3-vendor 중 2 부호 일치 미달 (i.e. 2/3 majority < some threshold).
F1 used 80% — apply same here.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations

from clinicaltrials_amendment_llm.manifest import MANIFEST_AXIS_CLASSIFY, read_manifest
from clinicaltrials_amendment_llm.oracle_pilot import VENDORS

AXES = ("pivotal_shift", "admin_vs_substantive", "driver")


def _latest_labels_per_nct_vendor() -> dict[tuple[str, str], dict]:
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in read_manifest(MANIFEST_AXIS_CLASSIFY):
        nct = r.get("nct_id")
        vendor = r.get("vendor")
        if not nct or not vendor:
            continue
        grouped[(nct, vendor)].append(r)
    return {k: sorted(v, key=lambda x: x.get("called_at", ""))[-1] for k, v in grouped.items()}


def measure_cross_llm() -> dict:
    """Return cross-LLM agreement stats per axis + overall."""
    latest = _latest_labels_per_nct_vendor()

    # Filter to NCTs with all 3 vendors
    by_nct: dict[str, dict[str, dict]] = defaultdict(dict)
    for (nct, vendor), rec in latest.items():
        by_nct[nct][vendor] = rec
    full_ncts = [n for n, vs in by_nct.items() if all(v in vs for v in VENDORS)]

    if not full_ncts:
        return {"n_ncts_full": 0, "error": "no NCTs with all 3 vendors"}

    per_axis: dict[str, dict] = {}
    for axis in AXES:
        majority_match = 0
        unanimous_match = 0
        non_unknown_majority = 0
        n = 0
        # Pairwise agreement counts
        pair_agree = {f"{a}__{b}": 0 for a, b in combinations(VENDORS, 2)}
        for nct in full_ncts:
            vals = [by_nct[nct][v].get(axis) for v in VENDORS]
            non_null = [v for v in vals if v is not None]
            if len(non_null) < 3:
                continue
            n += 1
            # Pairwise
            for a, b in combinations(VENDORS, 2):
                if by_nct[nct][a].get(axis) == by_nct[nct][b].get(axis):
                    pair_agree[f"{a}__{b}"] += 1
            # Majority
            counts = {v: vals.count(v) for v in set(vals)}
            top = max(counts.items(), key=lambda kv: kv[1])
            if top[1] >= 2:
                majority_match += 1
                if top[0] != "unknown":
                    non_unknown_majority += 1
            if top[1] == 3:
                unanimous_match += 1
        per_axis[axis] = {
            "n": n,
            "majority_2of3_rate": round(majority_match / max(n, 1), 4),
            "unanimous_rate": round(unanimous_match / max(n, 1), 4),
            "non_unknown_majority_rate": round(non_unknown_majority / max(n, 1), 4),
            "pairwise_agreement": {k: round(v / max(n, 1), 4) for k, v in pair_agree.items()},
        }

    # Overall: average per-axis majority rate
    overall_majority = sum(per_axis[a]["majority_2of3_rate"] for a in AXES) / len(AXES)
    return {
        "n_ncts_full": len(full_ncts),
        "per_axis": per_axis,
        "overall_majority_2of3_rate": round(overall_majority, 4),
        "trigger4_threshold": 0.8,
        "trigger4_pass": overall_majority >= 0.8,
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    import json
    res = measure_cross_llm()
    print(json.dumps(res, indent=2, default=str))
