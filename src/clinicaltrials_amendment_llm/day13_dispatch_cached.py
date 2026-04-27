"""Day 13 dispatch on cached-only NCTs (skip slow PDF download).

After full n=1500 dispatch hit PDF-download throttling (~12 PDFs/min),
763 PDFs were cached. This script:
1. Filters the mapped pool to NCTs that already have a cached protocol PDF.
2. Stratified-samples up to N from that subset.
3. Dispatches LLM 3-vendor calls (no new PDF download).

Result: fast LLM dispatch using already-on-disk data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("D:/vscode/portfolio-coordination/.env")

from clinicaltrials_amendment_llm.day8_dispatch import (
    _existing_dispatch_keys,
    stratified_sample,
)
from clinicaltrials_amendment_llm.day8_dispatch_async import dispatch_one_record
from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    MANIFEST_AXIS_CLASSIFY,
    append_manifest,
    ensure_data_dir,
)
from clinicaltrials_amendment_llm.oracle_pilot import (
    SYSTEM_PROMPT,
    VENDORS,
    _build_user_prompt,
)
from clinicaltrials_amendment_llm.pdf_parser import parse_pdf
from clinicaltrials_amendment_llm.protocol_excerpt import extract as extract_excerpt
from shared_utils.openrouter_client import OpenRouterClient


def _cached_nct_ids() -> set[str]:
    pdf_dir = DATA_DIR / "cache" / "pdf"
    if not pdf_dir.exists():
        return set()
    out = set()
    for p in pdf_dir.glob("*_Prot_*.pdf"):
        nct = p.name.split("_")[0]
        out.add(nct)
    return out


def dispatch_cached(target_n: int = 250) -> dict:
    """Pick NCTs from intersection of (mapped pool, cached PDFs) and dispatch."""
    ensure_data_dir()
    cached = _cached_nct_ids()
    print(f"Cached PDFs: {len(cached)} NCTs", flush=True)

    # Pull a generous stratified pool (much larger than target_n) and intersect.
    pool = stratified_sample(target_n * 4)
    cached_pool = [r for r in pool if r["nct_id"] in cached]
    print(f"Cached & mapped pool: {len(cached_pool)} (target {target_n})", flush=True)

    sample = cached_pool[:target_n]
    if not sample:
        return {"error": "empty sample"}

    seen_keys = _existing_dispatch_keys()
    client = OpenRouterClient(project="F6")
    n_calls = 0
    n_skipped = 0
    total_cost = 0.0

    for i, r in enumerate(sample):
        nct = r["nct_id"]
        cached_pdfs = list((DATA_DIR / "cache" / "pdf").glob(f"{nct}_Prot_*.pdf"))
        if not cached_pdfs:
            continue
        pr = parse_pdf(cached_pdfs[0])
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

        already = {v for v in VENDORS if (nct, v, prompt_hash) in seen_keys}
        n_skipped += len(already)

        if len(already) < len(VENDORS):
            recs = dispatch_one_record(client, nct, meta, full_prompt, prompt_hash, r.get("ticker"), r.get("stratum", ()))
            for rec in recs:
                if rec.get("vendor") not in already:
                    n_calls += 1
                    total_cost += float(rec.get("cost_usd", 0.0) or 0.0)

        if (i + 1) % 25 == 0:
            print(f"  progress: {i+1}/{len(sample)}, calls={n_calls}, cost=${total_cost:.4f}", flush=True)

    return {
        "n_sample": len(sample),
        "n_calls": n_calls,
        "n_skipped_existing": n_skipped,
        "total_cost_usd": round(total_cost, 4),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=250)
    args = p.parse_args()
    summary = dispatch_cached(target_n=args.n)
    print(json.dumps(summary, indent=2), flush=True)
