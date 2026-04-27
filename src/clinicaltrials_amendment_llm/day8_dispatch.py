"""Day 8-10 Phase 1 strategic sample dispatch.

Strategic sample n=N stratified by:
- year (last_update_post_date year, 2020-2024 quintile)
- sponsor_size_bucket (top-20 / 21-200 / tail)
- phase (PHASE2 / PHASE3 / both)

The 300-record proof-of-concept variant. Full 1500 dispatch follows the same
pattern but with a 5x larger sample.

Pipeline:
  1. Read manifest_amendment_fetch + sponsor_map
  2. Filter to records with ticker (mapped via sponsor_mapper expansion)
  3. Stratify by (year, sponsor_top20, phase) into ~30 cells
  4. Sample N records proportional to cell size
  5. Download protocol PDFs (Prot_000.pdf via cached path)
  6. Parse PDFs + extract amendment-aware excerpt
  7. Call 3 vendors per record (claude-haiku-4.5, llama-3.3-70b, gpt-4o-mini)
  8. Persist to manifest_axis_classify.jsonl with prompt_hash dedup

Resumable: skip (nct_id, vendor, prompt_hash) already in manifest.

Run: `python -m clinicaltrials_amendment_llm.day8_dispatch [--n N]`
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("D:/vscode/portfolio-coordination/.env")

from clinicaltrials_amendment_llm.day3_pdf_dryrun import _download_pdf
from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    MANIFEST_AMENDMENT_FETCH,
    MANIFEST_AXIS_CLASSIFY,
    MANIFEST_SPONSOR_MAP,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)
from clinicaltrials_amendment_llm.oracle_pilot import (
    SYSTEM_PROMPT,
    VENDORS,
    _build_user_prompt,
    _parse_axis_response,
    _request_id,
)
from clinicaltrials_amendment_llm.pdf_parser import parse_pdf
from clinicaltrials_amendment_llm.protocol_excerpt import extract as extract_excerpt
from shared_utils.openrouter_client import OpenRouterClient


# Top-20 biotech tickers (XBI/IBB heavy weights) for stratum bucket.
TOP20_TICKERS = {
    "PFE", "MRK", "JNJ", "BMY", "LLY", "GILD", "AMGN", "REGN", "VRTX",
    "BIIB", "MRNA", "BNTX", "ABBV", "AZN", "GSK", "SNY", "NVS", "ROG.SW",
    "INCY", "ALNY",
}


def _expanded_ticker_map() -> dict[str, dict]:
    """Latest sponsor_map.jsonl entries indexed by nct_id (latest by source)."""
    out: dict[str, dict] = {}
    for r in read_manifest(MANIFEST_SPONSOR_MAP):
        nct = r.get("nct_id")
        if not nct:
            continue
        out[nct] = r  # later entries overwrite
    return out


def _existing_dispatch_keys() -> set[tuple[str, str, str]]:
    seen: set[tuple[str, str, str]] = set()
    for r in read_manifest(MANIFEST_AXIS_CLASSIFY):
        nct = r.get("nct_id")
        vendor = r.get("vendor")
        ph = r.get("prompt_hash") or ""
        if nct and vendor:
            seen.add((nct, vendor, ph))
    return seen


def _classify_year(date_str: str | None) -> str:
    if not date_str:
        return "unknown"
    try:
        y = int(date_str.split("-")[0])
        return str(y)
    except Exception:
        return "unknown"


def _classify_sponsor_size(ticker: str) -> str:
    if ticker in TOP20_TICKERS:
        return "top20"
    return "mid_or_long_tail"


def _classify_phase(phases: list[str] | None) -> str:
    if not phases:
        return "unknown"
    if "PHASE3" in phases and "PHASE2" not in phases:
        return "phase3"
    if "PHASE2" in phases and "PHASE3" not in phases:
        return "phase2"
    return "phase23_mixed"


def stratified_sample(target_n: int, *, seed: int = 42) -> list[dict]:
    """Stratified sample by (year, sponsor_size, phase)."""
    rng = random.Random(seed)
    sponsor_map = _expanded_ticker_map()

    # Build full pool: records with new_ticker
    pool: list[dict] = []
    for r in read_manifest(MANIFEST_AMENDMENT_FETCH):
        nct = r.get("nct_id")
        if not nct:
            continue
        sm = sponsor_map.get(nct)
        ticker = (sm or {}).get("new_ticker") or r.get("ticker")
        if not ticker:
            continue
        # Skip non-US tickers for yfinance reliability in Phase 1 dispatch.
        if "." in ticker or ":" in ticker:
            continue

        year = _classify_year(r.get("last_update_post_date"))
        size = _classify_sponsor_size(ticker)
        phase = _classify_phase(r.get("phase"))

        pool.append({
            **r,
            "ticker": ticker,
            "stratum": (year, size, phase),
        })

    if not pool:
        return []

    # Bucket
    buckets: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for r in pool:
        buckets[r["stratum"]].append(r)

    n_buckets = len(buckets)
    n_per_bucket = max(1, target_n // n_buckets)

    # Sample proportionally; if a bucket is smaller than n_per_bucket, take all.
    selected: list[dict] = []
    for stratum, records in sorted(buckets.items()):
        rng.shuffle(records)
        selected.extend(records[: min(n_per_bucket, len(records))])

    # Fill remainder via random draw from unsampled
    if len(selected) < target_n:
        remaining_pool = [r for r in pool if r not in selected]
        rng.shuffle(remaining_pool)
        selected.extend(remaining_pool[: target_n - len(selected)])

    return selected[:target_n]


def dispatch(target_n: int = 300) -> dict:
    """Run 3-vendor dispatch on a stratified sample of size target_n."""
    ensure_data_dir()
    sample = stratified_sample(target_n)
    print(f"Stratified sample size: {len(sample)} (target {target_n})")

    if not sample:
        return {"error": "empty pool - no mapped records"}

    # Pre-download PDFs in serial (cache check is cheap)
    pdf_paths: dict[str, Path] = {}
    n_no_pdf = 0
    for r in sample:
        nct = r["nct_id"]
        cached = list((DATA_DIR / "cache" / "pdf").glob(f"{nct}_Prot_*.pdf"))
        if cached:
            pdf_paths[nct] = cached[0]
            continue
        path = _download_pdf(nct, "Prot_000.pdf")
        if path:
            pdf_paths[nct] = path
        else:
            n_no_pdf += 1

    print(f"PDFs available: {len(pdf_paths)} / {len(sample)} (no_pdf: {n_no_pdf})")

    # Dispatch
    seen_keys = _existing_dispatch_keys()
    client = OpenRouterClient(project="F6")
    n_calls = 0
    n_skipped = 0
    n_errors = 0
    total_cost = 0.0
    progress_every = 25

    for i, r in enumerate(sample):
        nct = r["nct_id"]
        path = pdf_paths.get(nct)
        if not path:
            continue
        pr = parse_pdf(path)
        if not pr.text:
            continue
        excerpt, source = extract_excerpt(pr.text)
        meta = {
            "nct_id": nct,
            "sponsor_name": r.get("sponsor_name"),
            "sponsor_class": r.get("sponsor_class"),
            "phase": r.get("phase"),
            "study_first_submit_date": r.get("study_first_submit_date"),
            "last_update_post_date": r.get("last_update_post_date"),
        }
        user_prompt = _build_user_prompt(meta, excerpt, source)
        prompt_hash = hashlib.sha256(user_prompt.encode()).hexdigest()[:12]
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

        for vendor in VENDORS:
            if (nct, vendor, prompt_hash) in seen_keys:
                n_skipped += 1
                continue
            try:
                resp = client.complete(model=vendor, prompt=full_prompt, max_tokens=400, temperature=0.0)
                choices = resp.get("choices", [])
                text = choices[0].get("message", {}).get("content", "") if choices else ""
                parsed = _parse_axis_response(text)
                cost = float(resp.get("usage", {}).get("cost", 0.0))
                total_cost += cost
                n_calls += 1
                record = {
                    "request_id": _request_id(nct, vendor, prompt_hash),
                    "nct_id": nct,
                    "vendor": vendor,
                    "prompt_hash": prompt_hash,
                    "phase_dispatch": "phase1_strategic",
                    "stratum": list(r.get("stratum", ())),
                    "ticker": r.get("ticker"),
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
                print(f"  {nct} x {vendor[:20]}: ERR {type(e).__name__}: {str(e)[:80]}")

        if (i + 1) % progress_every == 0:
            print(f"  progress: {i+1}/{len(sample)} NCTs, calls={n_calls}, cost=${total_cost:.4f}")

    return {
        "n_sample": len(sample),
        "n_pdfs": len(pdf_paths),
        "n_no_pdf": n_no_pdf,
        "n_calls": n_calls,
        "n_skipped_existing": n_skipped,
        "n_errors": n_errors,
        "total_cost_usd": round(total_cost, 4),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=300)
    args = p.parse_args()
    summary = dispatch(target_n=args.n)
    print(json.dumps(summary, indent=2))
