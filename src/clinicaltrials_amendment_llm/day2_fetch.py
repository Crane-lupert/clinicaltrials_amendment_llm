"""Day 2 first amendment fetch.

Run: `python -m clinicaltrials_amendment_llm.day2_fetch`

Strategy:
1. Search CT.gov v2 for industry-sponsored Phase 2/3 studies updated
   in FY2024 (lastUpdatePostDate 2024-01-01 .. 2024-12-31).
2. Page through up to N records; persist sponsor metadata to
   manifest_amendment_fetch.jsonl.
3. Filter by biotech_universe.lookup_ticker - keep only seeds that map
   to a known ticker (Day 2 placeholder; Day 11 replaces with
   filer_ontology + parent rollup).
4. Report per-stage yield.

This is the *fetch yield* probe - the first concrete measure of Phase 0
trigger #1 (fetched amendments >= 3000 by Day 5 EOD). Day 2 EOD goal is
just to confirm the pipeline works on a sample (>= 100 records) and
that the sponsor->ticker indirection has measurable yield.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from clinicaltrials_amendment_llm.biotech_universe import lookup_ticker
from clinicaltrials_amendment_llm.ctgov_client import extract_sponsor, search_studies
from clinicaltrials_amendment_llm.manifest import (
    MANIFEST_AMENDMENT_FETCH,
    append_manifest,
    ensure_data_dir,
)


# Industry-sponsored Phase 2/3 with FY2024 updates - Day 2 sample.
# Day 5 expands to all biotech R1000 + 1y window.
QUERY_FY2024_INDUSTRY_PHASE23 = (
    "AREA[LeadSponsorClass]INDUSTRY "
    "AND AREA[Phase](PHASE2 OR PHASE3) "
    "AND AREA[LastUpdatePostDate]RANGE[2024-01-01,2024-12-31]"
)


async def fetch_first_n(target_n: int = 200, page_size: int = 100) -> dict[str, int]:
    """Fetch up to target_n studies; persist + report yield."""
    ensure_data_dir()
    max_pages = max(1, (target_n + page_size - 1) // page_size)
    studies = await search_studies(
        QUERY_FY2024_INDUSTRY_PHASE23,
        page_size=page_size,
        max_pages=max_pages,
    )

    counts = {
        "fetched_total": 0,
        "industry_sponsored": 0,
        "phase23": 0,
        "biotech_r1000_match": 0,
        "academic_or_unknown": 0,
        "ticker_unmapped": 0,
    }
    seen_sponsors: dict[str, int] = {}

    for s in studies:
        meta = extract_sponsor(s)
        if not meta.get("nct_id"):
            continue
        counts["fetched_total"] += 1

        cls = meta.get("sponsor_class") or ""
        if cls == "INDUSTRY":
            counts["industry_sponsored"] += 1
        else:
            counts["academic_or_unknown"] += 1

        phases = meta.get("phase") or []
        if any(p in ("PHASE2", "PHASE3") for p in phases):
            counts["phase23"] += 1

        sponsor = meta.get("sponsor_name") or ""
        seen_sponsors[sponsor] = seen_sponsors.get(sponsor, 0) + 1

        ticker = lookup_ticker(sponsor)
        if ticker:
            counts["biotech_r1000_match"] += 1
        else:
            counts["ticker_unmapped"] += 1

        record = {
            **meta,
            "ticker": ticker,
            "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        append_manifest(MANIFEST_AMENDMENT_FETCH, record)

    return {
        **counts,
        "n_unique_sponsors": len(seen_sponsors),
        "n_unique_industry_sponsors": sum(1 for k, v in seen_sponsors.items() if v > 0),
    }


def print_summary(counts: dict[str, int]) -> None:
    print("=== Day 2 first amendment fetch ===")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print()
    n = max(counts.get("fetched_total", 1), 1)
    print(f"  industry_sponsored_rate: {counts.get('industry_sponsored', 0) / n:.1%}")
    print(f"  biotech_r1000_match_rate: {counts.get('biotech_r1000_match', 0) / n:.1%}")
    print(f"  ticker_unmapped_rate: {counts.get('ticker_unmapped', 0) / n:.1%}")


if __name__ == "__main__":
    counts = asyncio.run(fetch_first_n(target_n=200, page_size=100))
    print_summary(counts)
