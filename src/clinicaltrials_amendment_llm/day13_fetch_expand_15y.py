"""Day 13 (post-pivot) - extend fetch window to FY2010-FY2024 (15y).

User-directive 2026-04-28: "CT.gov로 과거 더 가져올 것".

Day 8 had FY2020-FY2024 (5y) → 8,700 records. Adding FY2010-FY2019 brings
the window to 15y. Industry-sponsored Phase 2/3 over 15y of biotech R&D
is the F6 reference-validation §4.5.1 spec target (~5K-30K records).

Phase transition outcome labels are cleaner with older trials (have time
to actually transition or fail) — supports trigger #1 ROC-AUC measurement.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

from clinicaltrials_amendment_llm.biotech_universe import lookup_ticker
from clinicaltrials_amendment_llm.ctgov_client import extract_sponsor, search_studies
from clinicaltrials_amendment_llm.manifest import (
    MANIFEST_AMENDMENT_FETCH,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)


# Earlier window: FY2010-FY2019 (10y backward extension)
QUERY_FY2010_2019 = (
    "AREA[LeadSponsorClass]INDUSTRY "
    "AND AREA[Phase](PHASE2 OR PHASE3) "
    "AND AREA[LastUpdatePostDate]RANGE[2010-01-01,2019-12-31]"
)


def _existing_nct_ids() -> set[str]:
    return {r.get("nct_id") for r in read_manifest(MANIFEST_AMENDMENT_FETCH) if r.get("nct_id")}


async def expand_fetch_15y(target_total: int = 25000, page_size: int = 100) -> dict:
    ensure_data_dir()
    seen = _existing_nct_ids()
    print(f"Pre-fetch manifest: {len(seen)}", flush=True)
    needed = max(0, target_total - len(seen))
    print(f"Need ~{needed} more records to reach target {target_total}.", flush=True)

    over_fetch = int(needed * 1.4)
    max_pages = max(1, (over_fetch + page_size - 1) // page_size)
    print(f"Fetching {QUERY_FY2010_2019[:80]}... up to {max_pages} pages.", flush=True)

    studies = await search_studies(QUERY_FY2010_2019, page_size=page_size, max_pages=max_pages)
    print(f"  API returned {len(studies)} studies.", flush=True)

    counts = {"added": 0, "skipped_dupe": 0}
    new_seen: set[str] = set()
    for s in studies:
        meta = extract_sponsor(s)
        nct = meta.get("nct_id")
        if not nct or nct in seen or nct in new_seen:
            counts["skipped_dupe"] += 1
            continue
        new_seen.add(nct)
        sponsor = meta.get("sponsor_name") or ""
        ticker = lookup_ticker(sponsor)
        record = {
            **meta,
            "ticker": ticker,
            "fetched_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        append_manifest(MANIFEST_AMENDMENT_FETCH, record)
        counts["added"] += 1
        if len(seen) + counts["added"] >= target_total:
            break

    return {
        "pre_existing": len(seen),
        "studies_returned_by_api": len(studies),
        "added": counts["added"],
        "skipped_dupe": counts["skipped_dupe"],
        "final_total": len(seen) + counts["added"],
    }


if __name__ == "__main__":
    counts = asyncio.run(expand_fetch_15y(target_total=25000, page_size=100))
    print(json.dumps(counts, indent=2), flush=True)
