"""Day 8 (Phase 1 entry) - extend fetch window to FY2020-FY2024 (5y).

Day 5 fetch window was FY2022-FY2024 (3y) - 3,500 records. After Day 11 sponsor
mapping expansion, mapped pool is 904 / 3500 = 25.8%, BELOW the Phase 1 trigger #7
floor of 1500. Period expansion is the cleanest fix per Phase 0 plan §3 trigger #1
fallback ('1회 retry universe / period 보강').

This script extends the fetch to FY2020-FY2024 (5y), maintaining the same
industry-sponsored Phase 2/3 filter. Idempotent against existing manifest entries.

Run: `python -m clinicaltrials_amendment_llm.day8_fetch_expand_5y`
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
    read_manifest,
)


# 5-year window: FY2020-FY2024.
QUERY_FY2020_2024 = (
    "AREA[LeadSponsorClass]INDUSTRY "
    "AND AREA[Phase](PHASE2 OR PHASE3) "
    "AND AREA[LastUpdatePostDate]RANGE[2020-01-01,2024-12-31]"
)


def _existing_nct_ids() -> set[str]:
    return {r.get("nct_id") for r in read_manifest(MANIFEST_AMENDMENT_FETCH) if r.get("nct_id")}


async def expand_fetch_5y(target_total: int = 10000, page_size: int = 100) -> dict[str, int]:
    ensure_data_dir()
    seen = _existing_nct_ids()
    print(f"Pre-fetch manifest count: {len(seen)}")

    needed = max(0, target_total - len(seen))
    print(f"Need {needed} more records to reach target {target_total}.")

    # Over-fetch by 1.3x (5y window has more dupes from prior 3y window)
    over_fetch_target = int(needed * 1.3) + 200
    max_pages = max(1, (over_fetch_target + page_size - 1) // page_size)
    print(f"Fetching up to {max_pages} pages.")

    studies = await search_studies(
        QUERY_FY2020_2024,
        page_size=page_size,
        max_pages=max_pages,
    )
    print(f"Search returned {len(studies)} studies.")

    counts = {"added": 0, "skipped_dupe": 0}
    new_seen: set[str] = set()

    for s in studies:
        meta = extract_sponsor(s)
        nct = meta.get("nct_id")
        if not nct:
            continue
        if nct in seen or nct in new_seen:
            counts["skipped_dupe"] += 1
            continue
        new_seen.add(nct)

        sponsor = meta.get("sponsor_name") or ""
        ticker = lookup_ticker(sponsor)  # Old seed-only mapper (sponsor_mapper updates this later)

        record = {
            **meta,
            "ticker": ticker,
            "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        append_manifest(MANIFEST_AMENDMENT_FETCH, record)
        counts["added"] += 1

        if len(seen) + counts["added"] >= target_total:
            break

    final_total = len(seen) + counts["added"]
    return {
        "pre_existing": len(seen),
        "studies_returned_by_api": len(studies),
        "added": counts["added"],
        "skipped_dupe": counts["skipped_dupe"],
        "final_total": final_total,
    }


if __name__ == "__main__":
    counts = asyncio.run(expand_fetch_5y(target_total=10000, page_size=100))
    import json
    print(json.dumps(counts, indent=2))
