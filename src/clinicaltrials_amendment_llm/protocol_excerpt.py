"""Protocol text excerpt extractor - amendment-aware.

Day 6 oracle pilot showed 75% "unknown" rate because the input was first 4000
chars of initial protocol text. Industry protocol PDFs often contain a
'Document History' or 'Amendment History' or 'Summary of Changes' section
near the start that lists amendments with dates and scope summaries. This
module finds and extracts that section preferentially.

Strategy:
1. Search for known section headers ('document history', 'amendment history',
   'summary of changes', 'protocol amendments', 'revision history',
   'version history', 'list of amendments').
2. If found -> return surrounding window (header_pos - 200 .. header_pos + 5000).
3. If not found -> return first 8000 chars (expanded from 4000).

Fixed budget: max 8000 chars in either path -> ~2000 tokens, well within
LLM context budget.
"""

from __future__ import annotations

import re

HISTORY_HEADERS_RE = re.compile(
    r"(document\s+history"
    r"|amendment\s+history"
    r"|summary\s+of\s+(?:changes|amendments|revisions)"
    r"|protocol\s+(?:amendments|amendment\s+history|history|revisions)"
    r"|revision\s+history"
    r"|version\s+history"
    r"|list\s+of\s+amendments"
    r"|history\s+of\s+(?:changes|amendments|revisions))",
    re.IGNORECASE,
)

DEFAULT_PREFIX_CHARS = 8000
MAX_EXCERPT_CHARS = 8000
PRE_HEADER_PAD = 200


def extract(protocol_text: str) -> tuple[str, str]:
    """Return (excerpt, source_marker).

    source_marker:
      - 'history_section'  - found a Document/Amendment History header
      - 'prefix'           - no header found; returned first 8000 chars
      - 'empty'            - protocol text was empty/whitespace
    """
    if not protocol_text or not protocol_text.strip():
        return "", "empty"

    m = HISTORY_HEADERS_RE.search(protocol_text)
    if m:
        start = max(0, m.start() - PRE_HEADER_PAD)
        end = min(len(protocol_text), m.start() + MAX_EXCERPT_CHARS)
        return protocol_text[start:end], "history_section"

    return protocol_text[:DEFAULT_PREFIX_CHARS], "prefix"


if __name__ == "__main__":
    from pathlib import Path

    from clinicaltrials_amendment_llm.pdf_parser import parse_pdf

    pdfs = sorted((Path("data/cache/pdf")).glob("*_Prot_*.pdf"))[:5]
    for p in pdfs:
        r = parse_pdf(p)
        excerpt, src = extract(r.text)
        print(f"{p.name[:35]:35s} src={src:18s} len={len(excerpt)}")
        if src == "history_section":
            # Show first 200 chars of the history section
            print(f"  preview: {excerpt[:300].replace(chr(10), ' / ')!r}")
