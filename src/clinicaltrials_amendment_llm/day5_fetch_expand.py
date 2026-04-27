"""Day 5 fetch expansion - push manifest_amendment_fetch.jsonl toward 3000+ records.

Phase 0 trigger #1: Day 5 EOD fetched < 3000 -> 1회 retry (universe / period 보강).
Day 2 first fetch: 200 records (FY2024). Day 5 expansion adds FY2022 + FY2023.

Strategy: expand period FY2022..FY2024 (3 years), keep industry-sponsored Phase 2/3.
Skip NCT IDs already in manifest (resumable / idempotent).

Run: `python -m clinicaltrials_amendment_llm.day5_fetch_expand`
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


# 3-year window: FY2022-FY2024. Industry-sponsored Phase 2/3.
QUERY_FY2022_2024 = (
    "AREA[LeadSponsorClass]INDUSTRY "
    "AND AREA[Phase](PHASE2 OR PHASE3) "
    "AND AREA[LastUpdatePostDate]RANGE[2022-01-01,2024-12-31]"
)


def _existing_nct_ids() -> set[str]:
    return {r.get("nct_id") for r in read_manifest(MANIFEST_AMENDMENT_FETCH) if r.get("nct_id")}


async def expand_fetch(target_total: int = 3500, page_size: int = 100) -> dict[str, int]:
    """Pull additional records to push manifest count to target_total.

    target_total = goal for total records in manifest_amendment_fetch.jsonl.
    """
    ensure_data_dir()
    seen = _existing_nct_ids()
    print(f"Pre-fetch manifest count: {len(seen)}")

    needed = max(0, target_total - len(seen))
    if needed == 0:
        print(f"Already at/above target {target_total}.")
        return {"existed": len(seen), "added": 0, "total": len(seen)}

    # Estimate pages: a fraction of returned records will be duplicates from FY2024
    # (we already fetched 200). Over-fetch by 1.5x to be safe.
    over_fetch_target = int(needed * 1.5)
    max_pages = max(1, (over_fetch_target + page_size - 1) // page_size)
    print(f"Need {needed} new records; fetching up to {max_pages} pages.")

    studies = await search_studies(
        QUERY_FY2022_2024,
        page_size=page_size,
        max_pages=max_pages,
    )
    print(f"Search returned {len(studies)} studies.")

    counts = {
        "added": 0,
        "skipped_dupe": 0,
        "industry_sponsored": 0,
        "phase23": 0,
        "biotech_r1000_match": 0,
    }
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

        cls = meta.get("sponsor_class") or ""
        if cls == "INDUSTRY":
            counts["industry_sponsored"] += 1

        phases = meta.get("phase") or []
        if any(p in ("PHASE2", "PHASE3") for p in phases):
            counts["phase23"] += 1

        sponsor = meta.get("sponsor_name") or ""
        ticker = lookup_ticker(sponsor)
        if ticker:
            counts["biotech_r1000_match"] += 1

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
        **counts,
        "final_total": final_total,
        "trigger1_pass": final_total >= 3000,
    }


def print_summary(c: dict[str, int]) -> None:
    print("=== Day 5 fetch expansion ===")
    for k, v in c.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    counts = asyncio.run(expand_fetch(target_total=3500, page_size=100))
    print_summary(counts)
