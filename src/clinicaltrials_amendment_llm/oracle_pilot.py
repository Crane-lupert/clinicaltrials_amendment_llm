"""n=20 oracle pilot - 3-vendor LLM ensemble Fleiss kappa measurement.

Phase 0 trigger #3 (Day 6 EOD): Fleiss kappa < 0.6 -> 3-axis -> 2-axis fallback
1회만, 미달 시 중단.

Pipeline:
1. Pick 20 NCT IDs from data/cache/pdf/ (already-downloaded protocol PDFs).
2. For each: load PDF text via pdf_parser, fetch CT.gov v2 metadata (sponsor / phase).
3. Build prompt per analysis/llm_prompt_3axis.md.
4. Call 3 vendors via OpenRouter (vendor diversity for Gate E):
   - anthropic/claude-3.5-sonnet
   - meta-llama/llama-3.3-70b-instruct
   - google/gemma-2-9b-it
5. Parse JSON responses into 3 axis values per (NCT, vendor).
6. Persist to data/manifest_axis_classify.jsonl.
7. Compute Fleiss kappa per axis + aggregate.
8. Threshold: kappa >= 0.6.

Idempotent: skips (NCT, vendor) pairs already in manifest_axis_classify.jsonl.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("D:/vscode/portfolio-coordination/.env")

from clinicaltrials_amendment_llm.ctgov_client import extract_sponsor, fetch_study
from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    MANIFEST_AXIS_CLASSIFY,
    MANIFEST_ORACLE_KAPPA,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)
from clinicaltrials_amendment_llm.pdf_parser import parse_pdf
from clinicaltrials_amendment_llm.protocol_excerpt import extract as extract_excerpt
from shared_utils.atomic_io import atomic_write_json
from shared_utils.openrouter_client import OpenRouterClient


# 2026-04-27 Day 6: anthropic/claude-3.5-sonnet and google/gemma-2-9b-it
# returned 404 "No endpoints found" - retired from OpenRouter. Switched to
# 3 vendor families that respond 200 OK on this key:
#   - Anthropic: claude-haiku-4.5 (cheap, fast - appropriate for n=20 pilot)
#   - Meta: llama-3.3-70b-instruct (already validated)
#   - OpenAI: gpt-4o-mini (cheap, third vendor family for Gate E diversity)
VENDORS: list[str] = [
    "anthropic/claude-haiku-4.5",
    "meta-llama/llama-3.3-70b-instruct",
    "openai/gpt-4o-mini",
]

# Day 7 (2026-04-27) revision: replaced fixed first-4000-chars excerpt with the
# amendment-aware extractor in protocol_excerpt.py. The extractor searches for
# Document/Amendment/Revision History headers and returns surrounding ~8000 chars.
# Falls back to first 8000 chars (still 2x the Day 6 budget) when no header found.

SYSTEM_PROMPT = (
    "You are a clinical-trial protocol-amendment analyst. Your task is to classify "
    "each amendment along three axes per the F6 schema. You rely on the protocol "
    "text + amendment narrative (when present). You answer in strict JSON; no prose "
    "outside the JSON object. If the text is insufficient for an axis, you mark "
    "that axis 'unknown' - never guess."
)


def _build_user_prompt(meta: dict, protocol_excerpt: str, excerpt_source: str) -> str:
    return f"""[NCT_ID]: {meta.get('nct_id')}
[SPONSOR]: {meta.get('sponsor_name')}  (class: {meta.get('sponsor_class')})
[PHASE]: {meta.get('phase')}
[FIRST_SUBMITTED]: {meta.get('study_first_submit_date')}
[LAST_UPDATE_POST]: {meta.get('last_update_post_date')}
[EXCERPT_SOURCE]: {excerpt_source}  (history_section = found Document/Amendment History header; prefix = first chars of protocol)

[PROTOCOL_EXCERPT]:
{protocol_excerpt}

Classify the most recent amendment on three axes per the F6 schema:

Axis 1 - pivotal_shift in {{ "positive", "neutral", "negative", "unknown" }}
  * positive: expands trial reach toward registration (dose up, arm added, enrollment up, endpoint upgrade, geography expansion).
  * neutral: design-correction / clarification / housekeeping with no directional regulatory impact.
  * negative: shrinks reach OR signals weakness (endpoint changed post-hoc, sample size down, population narrowed, arm dropped, hold, unblinding for safety).

Axis 2 - admin_vs_substantive in {{ "admin", "substantive", "unknown" }}
  * admin: typo / IRB list / contact-info / formatting only.
  * substantive: changes endpoint / sample size / dose / eligibility / randomization / duration / SAP.

Axis 3 - driver in {{ "dsmb", "regulator", "sponsor", "unknown" }}
  * dsmb: DSMB / DMC / IDMC triggered.
  * regulator: FDA / EMA / regulatory authority required.
  * sponsor: sponsor-initiated, no DSMB / regulator cue.

Decision rules when ambiguous:
- Lean axis_1 to "neutral" if mechanically design-corrective without directional bias.
- Lean axis_1 to "negative" if change reduces statistical power for the original primary endpoint, even when framed as "interim safety review".
- Vaccine cohort caveat: 2020-2022 COVID/RSV/influenza vaccine trial amendments often "positive substantive sponsor" (scope expansion as EUA path opens). Score per the actual change, but flag is_vaccine_cohort=true if applicable.

Return ONLY this JSON (no markdown fences, no explanation outside the object):
{{
  "nct_id": "<copy from input>",
  "pivotal_shift": "positive|neutral|negative|unknown",
  "admin_vs_substantive": "admin|substantive|unknown",
  "driver": "dsmb|regulator|sponsor|unknown",
  "is_vaccine_cohort": true|false,
  "rationale_short": "<= 200 chars, 1-2 sentences explaining the most diagnostic signal you used",
  "confidence": 0.0
}}
"""


def _pdf_paths_in_cache() -> list[Path]:
    return sorted((DATA_DIR / "cache" / "pdf").glob("*_Prot_*.pdf"))


def _nct_from_pdf_name(p: Path) -> str:
    # Format: {NCT}_{filename}.pdf
    return p.name.split("_")[0]


def _request_id(nct: str, vendor: str, prompt_hash: str) -> str:
    return hashlib.sha256(f"{nct}|{vendor}|{prompt_hash}".encode()).hexdigest()[:16]


def _existing_results() -> set[tuple[str, str, str]]:
    """Return set of (nct_id, vendor, prompt_hash) already in manifest_axis_classify.

    Day 7 fix: dedup by prompt_hash too, so prompt-revision (Day 7
    amendment-aware excerpt) re-calls vendors instead of silently skipping.
    """
    seen: set[tuple[str, str, str]] = set()
    for r in read_manifest(MANIFEST_AXIS_CLASSIFY):
        nct = r.get("nct_id")
        vendor = r.get("vendor")
        ph = r.get("prompt_hash") or ""
        if nct and vendor:
            seen.add((nct, vendor, ph))
    return seen


_JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_axis_response(text: str) -> dict:
    """Best-effort JSON extraction from LLM completion."""
    # Strip markdown fences
    t = text.strip()
    if t.startswith("```"):
        # Drop the first line and the trailing fence
        lines = t.splitlines()
        t = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    # If still has prose, grab the first {...} block
    if not t.startswith("{"):
        m = _JSON_OBJ_RE.search(t)
        if m:
            t = m.group(0)
    try:
        return json.loads(t)
    except Exception as e:
        return {"_parse_error": repr(e), "_raw": text[:500]}


async def _gather_metadata(ncts: list[str]) -> dict[str, dict]:
    """Async fetch sponsor metadata for all NCTs."""
    results = await asyncio.gather(*(fetch_study(n) for n in ncts), return_exceptions=True)
    out = {}
    for nct, rec in zip(ncts, results):
        if isinstance(rec, Exception):
            continue
        out[nct] = extract_sponsor(rec)
    return out


def run_oracle(target_n: int = 20) -> dict:
    """Run 3-vendor oracle pilot on n=20 NCTs."""
    ensure_data_dir()
    pdfs = _pdf_paths_in_cache()
    if len(pdfs) < target_n:
        raise RuntimeError(f"Only {len(pdfs)} cached PDFs; need {target_n}.")
    selected = pdfs[:target_n]
    nct_to_path = {_nct_from_pdf_name(p): p for p in selected}
    ncts = list(nct_to_path.keys())

    print(f"Selected {len(ncts)} NCTs.")
    print(f"Fetching metadata for {len(ncts)} NCTs ...")
    meta_map = asyncio.run(_gather_metadata(ncts))
    print(f"  metadata fetched for {len(meta_map)} / {len(ncts)}")

    seen_pairs = _existing_results()

    client = OpenRouterClient(project="F6")
    n_calls = 0
    n_skipped = 0
    n_errors = 0
    total_cost = 0.0

    for nct in ncts:
        meta = meta_map.get(nct)
        if not meta:
            print(f"  {nct}: SKIP (no metadata)")
            continue

        # Read PDF text once + amendment-aware excerpt
        pr = parse_pdf(nct_to_path[nct])
        excerpt, excerpt_source = extract_excerpt(pr.text or "")
        if not excerpt:
            print(f"  {nct}: SKIP (no protocol text)")
            continue

        user_prompt = _build_user_prompt(meta, excerpt, excerpt_source)
        prompt_hash = hashlib.sha256(user_prompt.encode()).hexdigest()[:12]
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        for vendor in VENDORS:
            if (nct, vendor, prompt_hash) in seen_pairs:
                n_skipped += 1
                continue
            req_id = _request_id(nct, vendor, prompt_hash)
            try:
                resp = client.complete(
                    model=vendor,
                    prompt=full_prompt,
                    max_tokens=400,
                    temperature=0.0,
                )
                choices = resp.get("choices", [])
                text = choices[0].get("message", {}).get("content", "") if choices else ""
                parsed = _parse_axis_response(text)
                cost = float(resp.get("usage", {}).get("cost", 0.0))
                total_cost += cost
                n_calls += 1

                record = {
                    "request_id": req_id,
                    "nct_id": nct,
                    "vendor": vendor,
                    "prompt_hash": prompt_hash,
                    "pivotal_shift": parsed.get("pivotal_shift"),
                    "admin_vs_substantive": parsed.get("admin_vs_substantive"),
                    "driver": parsed.get("driver"),
                    "is_vaccine_cohort": parsed.get("is_vaccine_cohort"),
                    "rationale_short": parsed.get("rationale_short"),
                    "confidence": parsed.get("confidence"),
                    "raw_response": text[:1000],
                    "parse_error": parsed.get("_parse_error"),
                    "cost_usd": cost,
                    "called_at": datetime.now(tz=timezone.utc).isoformat(),
                }
                append_manifest(MANIFEST_AXIS_CLASSIFY, record)
            except Exception as e:
                n_errors += 1
                print(f"  {nct} x {vendor}: ERROR {type(e).__name__}: {str(e)[:150]}")
                continue
        if (nct, VENDORS[0], prompt_hash) not in seen_pairs:
            print(f"  {nct}: 3 vendors done (cost so far ${total_cost:.4f})")

    return {
        "n_ncts": len(ncts),
        "n_calls": n_calls,
        "n_skipped_existing": n_skipped,
        "n_errors": n_errors,
        "total_cost_usd": round(total_cost, 4),
    }


def compute_fleiss_kappa(axis: str, latest_only: bool = True) -> dict:
    """Fleiss kappa for one axis across 3 vendors.

    latest_only: when multiple prompt_hash exist for a (nct, vendor) pair
    (Day 7 amendment-aware excerpt re-run), use only the most recent record.
    """
    # Group by (nct, vendor) -> list of records sorted by called_at
    grouped: dict[tuple[str, str], list[dict]] = {}
    for r in read_manifest(MANIFEST_AXIS_CLASSIFY):
        nct = r.get("nct_id")
        vendor = r.get("vendor")
        if not nct or not vendor:
            continue
        grouped.setdefault((nct, vendor), []).append(r)

    by_nct: dict[str, dict[str, str]] = {}
    for (nct, vendor), records in grouped.items():
        if latest_only:
            records = sorted(records, key=lambda x: x.get("called_at", ""))[-1:]
        for r in records:
            val = r.get(axis)
            if val is None:
                continue
            by_nct.setdefault(nct, {})[vendor] = str(val)

    # Filter to NCTs with all 3 vendors
    ncts_full = [n for n, vs in by_nct.items() if len(vs) >= 3 and all(v in vs for v in VENDORS)]
    if len(ncts_full) < 5:
        return {"axis": axis, "n_ncts_full": len(ncts_full), "kappa": None, "reason": "n<5"}

    # Build category set
    categories = sorted({v for n in ncts_full for v in by_nct[n].values()})
    n_cats = len(categories)
    cat_idx = {c: i for i, c in enumerate(categories)}

    # Subject x category count matrix (each subject = NCT, each rater = vendor)
    n_subjects = len(ncts_full)
    n_raters = 3
    counts = [[0] * n_cats for _ in range(n_subjects)]
    for i, nct in enumerate(ncts_full):
        for v in VENDORS:
            label = by_nct[nct][v]
            counts[i][cat_idx[label]] += 1

    # P_i for each subject
    P_i = []
    for i in range(n_subjects):
        s = sum(counts[i][j] * (counts[i][j] - 1) for j in range(n_cats))
        P_i.append(s / (n_raters * (n_raters - 1)))

    # P_bar (mean of P_i)
    P_bar = sum(P_i) / n_subjects

    # p_j (proportion of all assignments to category j)
    total_assignments = n_subjects * n_raters
    p_j = [sum(counts[i][j] for i in range(n_subjects)) / total_assignments for j in range(n_cats)]

    # P_e
    P_e = sum(p ** 2 for p in p_j)

    # Fleiss kappa
    if abs(1 - P_e) < 1e-12:
        kappa = float("nan")
    else:
        kappa = (P_bar - P_e) / (1 - P_e)

    return {
        "axis": axis,
        "n_ncts_full": n_subjects,
        "categories": categories,
        "p_j": [round(p, 4) for p in p_j],
        "P_bar": round(P_bar, 4),
        "P_e": round(P_e, 4),
        "kappa": round(kappa, 4),
    }


def _collapse_to_pivotal_binary(pivotal_shift: str, admin_vs_substantive: str) -> str:
    """2-axis fallback per analysis/three_axis_schema.md §2-Axis Fallback.

    substantive_design_change: substantive AND pivotal in {positive, negative}
    admin_or_neutral: admin OR (substantive AND pivotal == neutral)
    unknown: any "unknown" input - kept honest for kappa
    """
    if pivotal_shift == "unknown" or admin_vs_substantive == "unknown":
        return "unknown"
    if admin_vs_substantive == "substantive" and pivotal_shift in ("positive", "negative"):
        return "substantive_design_change"
    return "admin_or_neutral"


def compute_pivotal_binary_kappa() -> dict:
    """Fleiss kappa on the collapsed pivotal_binary axis (latest-only)."""
    grouped: dict[tuple[str, str], list[dict]] = {}
    for r in read_manifest(MANIFEST_AXIS_CLASSIFY):
        nct = r.get("nct_id")
        vendor = r.get("vendor")
        if not nct or not vendor:
            continue
        grouped.setdefault((nct, vendor), []).append(r)

    by_nct: dict[str, dict[str, str]] = {}
    for (nct, vendor), records in grouped.items():
        records = sorted(records, key=lambda x: x.get("called_at", ""))[-1:]
        for r in records:
            ps = r.get("pivotal_shift")
            avs = r.get("admin_vs_substantive")
            if ps is None or avs is None:
                continue
            binary = _collapse_to_pivotal_binary(str(ps), str(avs))
            by_nct.setdefault(nct, {})[vendor] = binary

    ncts_full = [n for n, vs in by_nct.items() if len(vs) >= 3 and all(v in vs for v in VENDORS)]
    if len(ncts_full) < 5:
        return {"axis": "pivotal_binary", "n_ncts_full": len(ncts_full), "kappa": None, "reason": "n<5"}

    categories = sorted({v for n in ncts_full for v in by_nct[n].values()})
    n_cats = len(categories)
    cat_idx = {c: i for i, c in enumerate(categories)}
    n_subjects = len(ncts_full)
    n_raters = 3
    counts = [[0] * n_cats for _ in range(n_subjects)]
    for i, nct in enumerate(ncts_full):
        for v in VENDORS:
            counts[i][cat_idx[by_nct[nct][v]]] += 1
    P_i = [
        sum(counts[i][j] * (counts[i][j] - 1) for j in range(n_cats)) / (n_raters * (n_raters - 1))
        for i in range(n_subjects)
    ]
    P_bar = sum(P_i) / n_subjects
    total = n_subjects * n_raters
    p_j = [sum(counts[i][j] for i in range(n_subjects)) / total for j in range(n_cats)]
    P_e = sum(p ** 2 for p in p_j)
    kappa = (P_bar - P_e) / (1 - P_e) if abs(1 - P_e) > 1e-12 else float("nan")

    return {
        "axis": "pivotal_binary",
        "n_ncts_full": n_subjects,
        "categories": categories,
        "p_j": [round(p, 4) for p in p_j],
        "P_bar": round(P_bar, 4),
        "P_e": round(P_e, 4),
        "kappa": round(kappa, 4),
    }


def measure_kappa() -> dict:
    """Compute kappa for all 3 axes + aggregate + pivotal_binary fallback."""
    axes = ["pivotal_shift", "admin_vs_substantive", "driver"]
    per_axis = {a: compute_fleiss_kappa(a) for a in axes}
    valid_kappas = [r["kappa"] for r in per_axis.values() if r.get("kappa") is not None]
    aggregate = sum(valid_kappas) / len(valid_kappas) if valid_kappas else None
    fallback = compute_pivotal_binary_kappa()

    # Per-axis pass: all 3 axes >= 0.6 (strict interpretation)
    per_axis_pass = all(
        r.get("kappa") is not None and r["kappa"] >= 0.6 for r in per_axis.values()
    )
    aggregate_pass = aggregate is not None and aggregate >= 0.6
    fallback_pass = fallback.get("kappa") is not None and fallback["kappa"] >= 0.6

    # Phase 0 plan §3 trigger #3 action: 3-axis κ < 0.6 → 2-axis fallback 1회만
    # Pass condition: per_axis_pass OR (per-axis fail AND fallback_pass)
    trigger3_overall_pass = per_axis_pass or fallback_pass

    # F1-1 partial-dispatch caveat: minority-class n must be >= 20 to lock
    # conclusion. Compute minority-class count for pivotal_shift specifically.
    ps_axis = per_axis.get("pivotal_shift", {})
    ps_p_j = ps_axis.get("p_j", [])
    minority_count_ps = (
        int(min(ps_p_j) * ps_axis.get("n_ncts_full", 0) * 3) if ps_p_j else 0
    )

    result = {
        "per_axis": per_axis,
        "aggregate_mean_kappa": round(aggregate, 4) if aggregate is not None else None,
        "fallback_pivotal_binary": fallback,
        "trigger3_threshold": 0.6,
        "trigger3_per_axis_pass": per_axis_pass,
        "trigger3_aggregate_pass": aggregate_pass,
        "trigger3_fallback_pass": fallback_pass,
        "trigger3_overall_pass": trigger3_overall_pass,
        "f1_1_caveat": {
            "minority_count_pivotal_shift": minority_count_ps,
            "f1_1_minority_floor": 20,
            "f1_1_lock_safe": minority_count_ps >= 20,
        },
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    atomic_write_json(MANIFEST_ORACLE_KAPPA, result)
    return result


if __name__ == "__main__":
    print("=== n=20 oracle pilot ===")
    summary = run_oracle(target_n=20)
    print(json.dumps(summary, indent=2))
    print("\n=== Fleiss kappa (3-axis x 3 vendors) ===")
    kappa_result = measure_kappa()
    print(json.dumps(kappa_result, indent=2, default=str))
    print(f"\nTrigger #3 (kappa >= 0.6 on all 3 axes): {kappa_result['trigger3_pass_3axis']}")
