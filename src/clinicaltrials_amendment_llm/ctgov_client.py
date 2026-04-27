"""ClinicalTrials.gov v2 API client (PURE daemon-free, Gate F).

Endpoint: https://clinicaltrials.gov/api/v2
Docs: https://clinicaltrials.gov/data-api/api

NEVER calls SEC EDGAR daemon. .claude/settings.json deny rules enforce this
at the harness layer; this module also asserts the URL host at request time
as a defense-in-depth check (Day 1 self-audit prerequisite).

Rate-limit: ClinicalTrials.gov has no published quota but documents
recommended ~10 concurrent requests. We bound concurrency via a semaphore
in async batch helpers. Single-request retry/backoff via tenacity.

This is a SKELETON for Day 1. Day 2-5 expand:
- studies query with sponsor filter
- version-history endpoint per NCT
- amendment text JSON extraction
- biotech R1000 sponsoring firm filter (industry-sponsored only)
"""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

API_V2_BASE = "https://clinicaltrials.gov/api/v2"
ALLOWED_HOSTS = {"clinicaltrials.gov", "www.clinicaltrials.gov"}
USER_AGENT = "clinicaltrials_amendment_llm/0.0.1 (research; F6; daemon-free)"
DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
DEFAULT_CONCURRENCY = 8  # below CT.gov's ~10 recommendation


class DaemonViolationError(RuntimeError):
    """Raised if a non-allowed host is requested - SEC daemon spillover guard."""


def _assert_allowed_url(url: str) -> None:
    host = urlparse(url).hostname or ""
    if host not in ALLOWED_HOSTS:
        raise DaemonViolationError(
            f"Disallowed host {host!r} - F6 is daemon-free (Gate F). "
            f"Only {ALLOWED_HOSTS} permitted."
        )


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
async def _get_json(client: httpx.AsyncClient, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    _assert_allowed_url(url)
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


async def fetch_study(nct_id: str, *, fields: list[str] | None = None) -> dict[str, Any]:
    """Fetch a single study record.

    Returns the raw JSON. Caller decides what to extract (sponsor, phase,
    enrollment, etc.). Version history is a separate endpoint.
    """
    url = f"{API_V2_BASE}/studies/{nct_id}"
    params: dict[str, Any] = {"format": "json"}
    if fields:
        params["fields"] = ",".join(fields)
    async with httpx.AsyncClient(
        timeout=DEFAULT_TIMEOUT,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        http2=True,
    ) as client:
        return await _get_json(client, url, params=params)


async def search_studies(
    query: str,
    *,
    page_size: int = 100,
    max_pages: int = 10,
) -> list[dict[str, Any]]:
    """Paginate /studies search. Returns flat list of study records."""
    url = f"{API_V2_BASE}/studies"
    studies: list[dict[str, Any]] = []
    next_token: str | None = None
    async with httpx.AsyncClient(
        timeout=DEFAULT_TIMEOUT,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        http2=True,
    ) as client:
        for _ in range(max_pages):
            params: dict[str, Any] = {
                "format": "json",
                "query.term": query,
                "pageSize": page_size,
            }
            if next_token:
                params["pageToken"] = next_token
            payload = await _get_json(client, url, params=params)
            studies.extend(payload.get("studies", []))
            next_token = payload.get("nextPageToken")
            if not next_token:
                break
    return studies


async def fetch_version_history(nct_id: str) -> dict[str, Any]:
    """Study record version history (amendment timeline).

    CT.gov v2 exposes this via /studies/{nct}/history. Returns raw JSON.
    """
    url = f"{API_V2_BASE}/studies/{nct_id}/history"
    async with httpx.AsyncClient(
        timeout=DEFAULT_TIMEOUT,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        http2=True,
    ) as client:
        return await _get_json(client, url, params={"format": "json"})


async def batch_fetch_studies(
    nct_ids: list[str],
    *,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> list[tuple[str, dict[str, Any] | Exception]]:
    """Concurrent fetch with bounded semaphore.

    Returns list of (nct_id, result_or_exception). Caller handles failures
    per-record so a bad NCT does not abort the batch (failure-granularity
    requirement, see manifest.py + Phase 0 plan §7).
    """
    sem = asyncio.Semaphore(concurrency)

    async def _one(nct: str) -> tuple[str, dict[str, Any] | Exception]:
        async with sem:
            try:
                return nct, await fetch_study(nct)
            except Exception as exc:  # noqa: BLE001
                return nct, exc

    return await asyncio.gather(*(_one(n) for n in nct_ids))


if __name__ == "__main__":
    # Sanity check: assert SEC URLs raise DaemonViolationError
    try:
        _assert_allowed_url("https://www.sec.gov/cgi-bin/browse-edgar?")
    except DaemonViolationError as e:
        print(f"OK daemon-free guard fires on SEC URL: {e}")
    else:
        raise SystemExit("FAIL: SEC URL was not blocked")

    # Sanity check: CT.gov URL passes
    _assert_allowed_url(f"{API_V2_BASE}/studies/NCT00000000")
    print("OK daemon-free guard passes CT.gov URL")
