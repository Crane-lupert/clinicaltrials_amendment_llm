"""Day 3 PDF parser dry-run (n=20 sub-sample).

Phase 0 trigger #6 prerequisite: among studies that have a protocol PDF,
parsing yield (success + partial) >= 80% (n=20 sub-sample).

Pipeline:
1. Sample 20 NCT IDs from manifest_amendment_fetch.jsonl.
2. For each: fetch_study to get documentSection.largeDocs.
3. If hasProtocol: download Prot_*.pdf via cdn.clinicaltrials.gov URL.
4. Run pdf_parser.parse_pdf on each downloaded PDF.
5. Persist 5-bin yield record to manifest_pdf_parse_audit.jsonl.
6. Print summary; return trigger6_pass.

URL pattern (verified Day 3):
  https://cdn.clinicaltrials.gov/large-docs/{NCT_LAST2}/{NCT}/{filename}
where NCT_LAST2 = last 2 digits of the NCT number (e.g. NCT04368728 -> "28").
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as cr

from clinicaltrials_amendment_llm.ctgov_client import (
    PROTOCOL_DOC_BASE,
    _assert_allowed_url,
    fetch_study,
)
from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    MANIFEST_AMENDMENT_FETCH,
    MANIFEST_PDF_PARSE_AUDIT,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)
from clinicaltrials_amendment_llm.pdf_parser import parse_pdf, yield_bins_summary

PDF_CACHE_DIR = DATA_DIR / "cache" / "pdf"


def _nct_last2(nct: str) -> str:
    """Extract last 2 digits used in CT.gov CDN URL path."""
    digits = "".join(c for c in nct if c.isdigit())
    return digits[-2:] if len(digits) >= 2 else digits


def _pdf_url(nct: str, filename: str) -> str:
    return f"{PROTOCOL_DOC_BASE}/{_nct_last2(nct)}/{nct}/{filename}"


def _download_pdf(nct: str, filename: str) -> Path | None:
    """Download a CT.gov protocol PDF to data/cache/pdf/{NCT}_{filename}."""
    url = _pdf_url(nct, filename)
    _assert_allowed_url(url)
    PDF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    out = PDF_CACHE_DIR / f"{nct}_{filename}"
    if out.exists() and out.stat().st_size > 0:
        return out  # cache hit
    try:
        r = cr.get(url, impersonate="chrome", timeout=60.0)
        if r.status_code != 200:
            return None
        out.write_bytes(r.content)
        return out
    except Exception:
        return None


async def select_protocol_sample(target_n: int = 20) -> list[tuple[str, str]]:
    """Pick first target_n NCTs (from manifest) that have a Prot_*.pdf doc.

    Returns: list of (nct_id, protocol_filename).
    """
    selected: list[tuple[str, str]] = []
    seen_ncts: set[str] = set()
    # Iterate manifest in order; fetch each to inspect documentSection
    records = list(read_manifest(MANIFEST_AMENDMENT_FETCH))
    # Probe in small concurrent batches to keep wall-clock reasonable
    batch = 8
    i = 0
    while i < len(records) and len(selected) < target_n:
        batch_recs = records[i : i + batch]
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


def run_dryrun(target_n: int = 20) -> dict:
    ensure_data_dir()
    pairs = asyncio.run(select_protocol_sample(target_n))
    print(f"Selected {len(pairs)} NCTs with protocol PDFs.")

    results = []
    n_downloaded = 0
    n_no_pdf_url = 0
    for nct, filename in pairs:
        path = _download_pdf(nct, filename)
        if path is None:
            n_no_pdf_url += 1
            # Treat as no_pdf bin since download failed (CDN-side issue).
            from clinicaltrials_amendment_llm.pdf_parser import ParseResult
            r = ParseResult(
                bin="no_pdf",
                text="",
                n_pages=0,
                n_chars=0,
                parser_used="none",
                text_hash=None,
                error="cdn download returned non-200",
            )
        else:
            n_downloaded += 1
            r = parse_pdf(path)
        results.append((nct, filename, r))

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
        }
        append_manifest(MANIFEST_PDF_PARSE_AUDIT, record)

    summary = yield_bins_summary([r for _, _, r in results])
    summary["n_pdfs_downloaded"] = n_downloaded
    summary["n_download_failed"] = n_no_pdf_url
    print(json.dumps(summary, indent=2, default=str))
    return summary


if __name__ == "__main__":
    s = run_dryrun(target_n=20)
    print(f"\nTrigger #6 (success+partial >= 80%): {s.get('trigger6_pass')!r}")
