"""Protocol PDF text extraction with fallback chain (F6 special - Phase 0 trigger #6).

Yield bins (manifest_pdf_parse_audit):
- success    - clean text extract via pdfplumber (primary)
- partial    - text extracted but suspected gaps (low char/page ratio)
- ocr_required - image PDF, no text layer (would need vision-LLM OCR)
- failed     - both pdfplumber and pypdf raised
- no_pdf     - study record JSON only, no protocol PDF available

Phase 0 trigger #6: success+partial >= 80% (n=20 sub-sample) -> Phase 1 entry.
< 80% -> immediate ABANDONED.md (no boost attempt - prerequisite for the
amendment-text LLM pipeline itself).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

YieldBin = Literal["success", "partial", "ocr_required", "failed", "no_pdf"]

# Heuristic: <100 chars per page implies image PDF or heavy OCR loss.
PARTIAL_CHARS_PER_PAGE_FLOOR = 100


@dataclass(frozen=True)
class ParseResult:
    bin: YieldBin
    text: str
    n_pages: int
    n_chars: int
    parser_used: str  # "pdfplumber" | "pypdf" | "none"
    text_hash: str | None
    error: str | None = None


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _try_pdfplumber(pdf_path: Path) -> tuple[str, int, str | None]:
    import pdfplumber

    pages_text: list[str] = []
    n_pages = 0
    with pdfplumber.open(pdf_path) as pdf:
        n_pages = len(pdf.pages)
        for page in pdf.pages:
            pages_text.append(page.extract_text() or "")
    return "\n\n".join(pages_text), n_pages, None


def _try_pypdf(pdf_path: Path) -> tuple[str, int, str | None]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    n_pages = len(reader.pages)
    pages_text = [p.extract_text() or "" for p in reader.pages]
    return "\n\n".join(pages_text), n_pages, None


def parse_pdf(pdf_path: Path) -> ParseResult:
    """Run the fallback chain. Returns a ParseResult with yield bin."""
    if not pdf_path.exists():
        return ParseResult(
            bin="no_pdf",
            text="",
            n_pages=0,
            n_chars=0,
            parser_used="none",
            text_hash=None,
            error="path does not exist",
        )

    # Stage 1: pdfplumber
    text = ""
    n_pages = 0
    parser_used = "none"
    error_chain: list[str] = []
    try:
        text, n_pages, _ = _try_pdfplumber(pdf_path)
        parser_used = "pdfplumber"
    except Exception as exc:  # noqa: BLE001
        error_chain.append(f"pdfplumber: {exc!r}")
        # Stage 2: pypdf
        try:
            text, n_pages, _ = _try_pypdf(pdf_path)
            parser_used = "pypdf"
        except Exception as exc2:  # noqa: BLE001
            error_chain.append(f"pypdf: {exc2!r}")
            return ParseResult(
                bin="failed",
                text="",
                n_pages=0,
                n_chars=0,
                parser_used="none",
                text_hash=None,
                error=" | ".join(error_chain),
            )

    n_chars = len(text)

    # Bin classification
    if n_pages == 0:
        # Empty PDF object - treat as failed
        bin_: YieldBin = "failed"
    elif n_chars == 0:
        # Pages exist but no text layer extracted - image PDF
        bin_ = "ocr_required"
    elif n_chars / max(n_pages, 1) < PARTIAL_CHARS_PER_PAGE_FLOOR:
        bin_ = "partial"
    else:
        bin_ = "success"

    return ParseResult(
        bin=bin_,
        text=text,
        n_pages=n_pages,
        n_chars=n_chars,
        parser_used=parser_used,
        text_hash=_hash_text(text) if text else None,
        error=" | ".join(error_chain) if error_chain else None,
    )


def yield_bins_summary(results: list[ParseResult]) -> dict[str, int | float]:
    """5-bin distribution + success+partial rate (Phase 0 trigger #6 metric)."""
    counts = {b: 0 for b in ("success", "partial", "ocr_required", "failed", "no_pdf")}
    for r in results:
        counts[r.bin] += 1
    n = max(len(results), 1)
    success_partial_rate = (counts["success"] + counts["partial"]) / n
    return {
        **counts,
        "n_total": len(results),
        "success_partial_rate": success_partial_rate,
        "trigger6_pass": success_partial_rate >= 0.80,
    }


if __name__ == "__main__":
    # Sanity: classify a non-existent path as no_pdf
    r = parse_pdf(Path("does_not_exist.pdf"))
    assert r.bin == "no_pdf", r
    summary = yield_bins_summary([r])
    print(f"OK pdf_parser sanity: {summary}")
