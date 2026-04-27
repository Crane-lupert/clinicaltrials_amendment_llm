"""Day 5 PDF parser dry-run sample 2 (n=20 from a *different* sub-sample).

Phase 0 trigger #6 confirmation: re-measure on different NCTs to confirm yield
stays >=80% across the broader fetch (not just the first 20 with hasProtocol).

Strategy:
- Re-use day3_pdf_dryrun's machinery, but skip NCTs already in
  manifest_pdf_parse_audit. Pick the next 20 with hasProtocol from the now-3500-record
  manifest.

Run: `python -m clinicaltrials_amendment_llm.day5_pdf_dryrun2`
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from clinicaltrials_amendment_llm.ctgov_client import fetch_study
from clinicaltrials_amendment_llm.day3_pdf_dryrun import _download_pdf
from clinicaltrials_amendment_llm.manifest import (
    MANIFEST_AMENDMENT_FETCH,
    MANIFEST_PDF_PARSE_AUDIT,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)
from clinicaltrials_amendment_llm.pdf_parser import ParseResult, parse_pdf, yield_bins_summary


def _seen_audit_nct_ids() -> set[str]:
    return {r.get("nct_id") for r in read_manifest(MANIFEST_PDF_PARSE_AUDIT) if r.get("nct_id")}


async def select_protocol_sample_v2(target_n: int = 20) -> list[tuple[str, str]]:
    """Pick target_n NCTs not already in pdf_parse_audit, with hasProtocol=true."""
    seen_audit = _seen_audit_nct_ids()
    selected: list[tuple[str, str]] = []
    seen_ncts: set[str] = set()

    # Skip first 200 (Day 2 sample) - go to records 200+ to ensure variety
    records = list(read_manifest(MANIFEST_AMENDMENT_FETCH))
    candidates = [r for r in records if r.get("nct_id") and r["nct_id"] not in seen_audit]
    # Start from index 200 (Day 2's NCT IDs are records 0-199; Day 5 expansion is 200+)
    candidates = candidates[200:] if len(candidates) > 200 else candidates

    batch = 8
    i = 0
    while i < len(candidates) and len(selected) < target_n:
        batch_recs = candidates[i : i + batch]
        i += batch
        results = await asyncio.gather(
            *(fetch_study(r["nct_id"]) for r in batch_recs if r["nct_id"] not in seen_ncts),
            return_exceptions=True,
        )
        for rec, full in zip(batch_recs, results):
            nct = rec["nct_id"]
            seen_ncts.add(nct)
            if isinstance(full, Exception):
                continue
            docs = full.get("documentSection", {}).get("largeDocumentModule", {}).get("largeDocs", [])
            for d in docs:
                if d.get("hasProtocol") and d.get("filename", "").startswith("Prot"):
                    selected.append((nct, d["filename"]))
                    if len(selected) >= target_n:
                        break
            if len(selected) >= target_n:
                break
    return selected


def run_dryrun_v2(target_n: int = 20) -> dict:
    ensure_data_dir()
    pairs = asyncio.run(select_protocol_sample_v2(target_n))
    print(f"Sample 2: selected {len(pairs)} new NCTs with protocol PDFs (excludes Day 3 sub-sample).")

    results: list[ParseResult] = []
    n_downloaded = 0
    n_no_pdf_url = 0
    for nct, filename in pairs:
        path = _download_pdf(nct, filename)
        if path is None:
            n_no_pdf_url += 1
            r = ParseResult(
                bin="no_pdf", text="", n_pages=0, n_chars=0,
                parser_used="none", text_hash=None, error="cdn download returned non-200",
            )
        else:
            n_downloaded += 1
            r = parse_pdf(path)
        results.append(r)

        record = {
            "nct_id": nct,
            "filename": filename,
            "bin": r.bin,
            "parser_used": r.parser_used,
            "n_pages": r.n_pages,
            "n_chars": r.n_chars,
            "text_hash": r.text_hash,
            "error": r.error,
            "audited_at": datetime.now(tz=timezone.utc).isoformat(),
            "sample": "day5_v2",
        }
        append_manifest(MANIFEST_PDF_PARSE_AUDIT, record)

    summary = yield_bins_summary(results)
    summary["n_pdfs_downloaded"] = n_downloaded
    summary["n_download_failed"] = n_no_pdf_url
    print(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    s = run_dryrun_v2(target_n=20)
    print(f"\nDay 5 trigger #6 (sample 2, success+partial >= 80%): {s.get('trigger6_pass')!r}")
