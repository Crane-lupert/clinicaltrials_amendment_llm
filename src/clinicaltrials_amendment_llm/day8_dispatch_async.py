"""Day 8-10 dispatch (async / threaded variant for speed).

Same stratification + sample logic as day8_dispatch but with:
- Parallel PDF download (asyncio.gather + curl_cffi)
- Parallel vendor calls within each NCT (ThreadPoolExecutor, 3 workers)
- Per-batch progress logging

For n=100 strategic sample, expected wall-clock ~10-15 min vs ~75 min sync.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("D:/vscode/portfolio-coordination/.env")

from curl_cffi import requests as cr

from clinicaltrials_amendment_llm.day3_pdf_dryrun import _pdf_url
from clinicaltrials_amendment_llm.day8_dispatch import (
    _existing_dispatch_keys,
    stratified_sample,
)
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
    _parse_axis_response,
    _request_id,
)
from clinicaltrials_amendment_llm.pdf_parser import parse_pdf
from clinicaltrials_amendment_llm.protocol_excerpt import extract as extract_excerpt
from shared_utils.openrouter_client import OpenRouterClient


def _download_pdfs_parallel(ncts: list[str], filename: str = "Prot_000.pdf") -> dict[str, Path]:
    """Download missing PDFs concurrently. Returns {nct: path}."""
    PDF_CACHE_DIR = DATA_DIR / "cache" / "pdf"
    PDF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, Path] = {}

    def download_one(nct: str) -> tuple[str, Path | None]:
        # Check cache first (any Prot_*.pdf)
        cached = list(PDF_CACHE_DIR.glob(f"{nct}_Prot_*.pdf"))
        if cached:
            return nct, cached[0]
        url = _pdf_url(nct, filename)
        out = PDF_CACHE_DIR / f"{nct}_{filename}"
        try:
            r = cr.get(url, impersonate="chrome", timeout=60.0)
            if r.status_code != 200:
                return nct, None
            out.write_bytes(r.content)
            return nct, out
        except Exception:
            return nct, None

    with ThreadPoolExecutor(max_workers=8) as ex:
        for fut in as_completed(ex.submit(download_one, n) for n in ncts):
            nct, path = fut.result()
            if path:
                results[nct] = path
    return results


def dispatch_one_record(client: OpenRouterClient, nct: str, meta: dict, full_prompt: str,
                        prompt_hash: str, ticker: str, stratum: tuple) -> list[dict]:
    """Call all 3 vendors for one NCT (parallel via ThreadPoolExecutor)."""
    out_records: list[dict] = []

    def call_one(vendor: str) -> dict | None:
        try:
            resp = client.complete(model=vendor, prompt=full_prompt, max_tokens=400, temperature=0.0)
            choices = resp.get("choices", [])
            text = choices[0].get("message", {}).get("content", "") if choices else ""
            parsed = _parse_axis_response(text)
            cost = float(resp.get("usage", {}).get("cost", 0.0))
            return {
                "request_id": _request_id(nct, vendor, prompt_hash),
                "nct_id": nct,
                "vendor": vendor,
                "prompt_hash": prompt_hash,
                "phase_dispatch": "phase1_strategic_async",
                "stratum": list(stratum),
                "ticker": ticker,
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
        except Exception as e:
            return {"nct_id": nct, "vendor": vendor, "error": repr(e)[:200]}

    with ThreadPoolExecutor(max_workers=3) as ex:
        for fut in as_completed(ex.submit(call_one, v) for v in VENDORS):
            rec = fut.result()
            if rec and "error" not in rec:
                out_records.append(rec)
                append_manifest(MANIFEST_AXIS_CLASSIFY, rec)

    return out_records


def dispatch(target_n: int = 100) -> dict:
    ensure_data_dir()
    sample = stratified_sample(target_n)
    print(f"Stratified sample: {len(sample)} (target {target_n})", flush=True)
    if not sample:
        return {"error": "empty pool"}

    ncts = [r["nct_id"] for r in sample]
    print(f"Pre-downloading PDFs (parallel) ...", flush=True)
    pdf_paths = _download_pdfs_parallel(ncts)
    print(f"  PDFs ready: {len(pdf_paths)} / {len(ncts)}", flush=True)

    seen_keys = _existing_dispatch_keys()
    client = OpenRouterClient(project="F6")
    n_calls = 0
    n_skipped = 0
    total_cost = 0.0

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

        # Check which vendors already exist
        already = {v for v in VENDORS if (nct, v, prompt_hash) in seen_keys}
        n_skipped += len(already)
        to_call = [v for v in VENDORS if v not in already]

        if to_call:
            # Filter VENDORS in dispatch_one_record? Easier: temporarily monkey-patch
            recs = dispatch_one_record(client, nct, meta, full_prompt, prompt_hash, r.get("ticker"), r.get("stratum", ()))
            for rec in recs:
                if rec.get("vendor") in to_call:
                    n_calls += 1
                    total_cost += float(rec.get("cost_usd", 0.0) or 0.0)

        if (i + 1) % 10 == 0:
            print(f"  progress: {i+1}/{len(sample)} NCTs, calls={n_calls}, cost=${total_cost:.4f}", flush=True)

    return {
        "n_sample": len(sample),
        "n_pdfs": len(pdf_paths),
        "n_calls": n_calls,
        "n_skipped_existing": n_skipped,
        "total_cost_usd": round(total_cost, 4),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=100)
    args = p.parse_args()
    summary = dispatch(target_n=args.n)
    print(json.dumps(summary, indent=2), flush=True)
