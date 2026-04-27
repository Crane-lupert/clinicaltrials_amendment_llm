"""Day 14-15 cross-section forward CAR module.

For each (NCT, ticker) with LLM 3-axis labels, compute:
- T-1 to T+5 CAR vs SPY
- T-0 to T+30 CAR vs SPY
- Same horizons XBI-hedged

Aggregate by `pivotal_shift` quintile -> long-low / short-high spread.

Pipeline:
1. Read manifest_axis_classify (latest-only per (nct, vendor)) -> majority vote per axis.
2. Read manifest_amendment_fetch + sponsor_map -> ticker + event_date.
3. yfinance batch download for unique tickers + SPY + XBI.
4. Per-event: compute CAR at multiple horizons.
5. Aggregate: low-pivotal-shift quintile vs high-pivotal-shift quintile,
   compute mean spread + Welch t-stat (per F1 rigor_pass pattern).

This is the Phase 1 trigger #3 measurement (cross-section CAR effect size,
t-stat >= 2.0 OR Sharpe >= 0.4).
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

from clinicaltrials_amendment_llm.manifest import (
    MANIFEST_AMENDMENT_FETCH,
    MANIFEST_AXIS_CLASSIFY,
    MANIFEST_CAR,
    MANIFEST_SPONSOR_MAP,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)


def _majority_label(values: list[str]) -> str:
    """Pick the most common non-null/non-unknown label; fallback to 'unknown'."""
    if not values:
        return "unknown"
    counts: dict[str, int] = {}
    for v in values:
        if v is None or v == "" or v == "unknown":
            continue
        counts[v] = counts.get(v, 0) + 1
    if not counts:
        return "unknown"
    return max(counts.items(), key=lambda kv: kv[1])[0]


def _latest_labels_by_nct() -> dict[str, dict[str, str]]:
    """{nct: {axis: majority_label}} using latest prompt_hash per (nct, vendor)."""
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in read_manifest(MANIFEST_AXIS_CLASSIFY):
        nct = r.get("nct_id")
        vendor = r.get("vendor")
        if not nct or not vendor:
            continue
        grouped[(nct, vendor)].append(r)

    # Per (nct, vendor): latest record only
    latest: dict[str, dict[str, str]] = defaultdict(lambda: defaultdict(list))
    for (nct, vendor), records in grouped.items():
        records = sorted(records, key=lambda x: x.get("called_at", ""))
        rec = records[-1]
        for axis in ("pivotal_shift", "admin_vs_substantive", "driver"):
            v = rec.get(axis)
            if v is not None:
                latest[nct][axis].append(v)

    out: dict[str, dict[str, str]] = {}
    for nct, axes in latest.items():
        out[nct] = {a: _majority_label(vals) for a, vals in axes.items()}
    return out


def _ticker_and_date_by_nct() -> dict[str, dict]:
    """{nct: {ticker, event_date}} from manifest_amendment_fetch (+ sponsor_map override)."""
    sm: dict[str, str] = {}
    for r in read_manifest(MANIFEST_SPONSOR_MAP):
        nct = r.get("nct_id")
        nt = r.get("new_ticker")
        if nct and nt:
            sm[nct] = nt

    out: dict[str, dict] = {}
    for r in read_manifest(MANIFEST_AMENDMENT_FETCH):
        nct = r.get("nct_id")
        if not nct:
            continue
        ticker = sm.get(nct) or r.get("ticker")
        if not ticker or "." in ticker or ":" in ticker:
            continue
        event_date = r.get("last_update_post_date")
        if not event_date:
            continue
        out[nct] = {"ticker": ticker, "event_date": event_date}
    return out


def compute_event_car(ticker_prices: dict[str, pd.DataFrame],
                      ticker: str, event_date: str,
                      benchmark: str = "SPY") -> dict | None:
    """Compute CAR for one event. Returns horizons or None if no data."""
    if ticker not in ticker_prices or benchmark not in ticker_prices:
        return None
    pt = ticker_prices[ticker]
    pb = ticker_prices[benchmark]
    if pt.empty or pb.empty:
        return None

    try:
        ed = pd.Timestamp(datetime.fromisoformat(event_date).date())
    except Exception:
        return None

    after = pt.index[pt.index >= ed]
    if len(after) == 0:
        return None
    t0 = after[0]

    horizons = {}
    for label, days in (("t_minus_1_to_t_0", -1), ("t_0_to_5", 5), ("t_0_to_30", 30)):
        if days < 0:
            before = pt.index[pt.index < t0]
            if len(before) == 0:
                horizons[label] = None
                continue
            sd, ee = before[-1], t0
        else:
            future = pt.index[pt.index >= t0]
            if len(future) <= days:
                horizons[label] = None
                continue
            sd, ee = t0, future[days]

        try:
            rt = float(pt.loc[ee] / pt.loc[sd] - 1)
            sd_b = pb.index[pb.index >= sd][0] if any(pb.index >= sd) else None
            ee_b = pb.index[pb.index <= ee][-1] if any(pb.index <= ee) else None
            if sd_b is None or ee_b is None or sd_b > ee_b:
                horizons[label] = None
                continue
            rb = float(pb.loc[ee_b] / pb.loc[sd_b] - 1)
            horizons[label] = {"stock": rt, benchmark.lower(): rb, "car": rt - rb}
        except (KeyError, IndexError, ValueError):
            horizons[label] = None

    return {"ticker": ticker, "event_date": event_date, "t0": str(t0.date()), "horizons": horizons}


def fetch_prices_batch(tickers: set[str], start: str, end: str) -> dict[str, pd.DataFrame]:
    """yfinance batch download. Returns {ticker: Close-series}."""
    import yfinance as yf

    all_tickers = list(tickers) + ["SPY", "XBI"]
    out: dict[str, pd.DataFrame] = {}
    print(f"  yfinance: downloading {len(all_tickers)} tickers from {start} to {end} ...")
    df = yf.download(all_tickers, start=start, end=end, auto_adjust=True, progress=False, threads=True, group_by="ticker")
    if df is None or df.empty:
        return {}
    if isinstance(df.columns, pd.MultiIndex):
        for t in all_tickers:
            try:
                close = df[t]["Close"].dropna()
                out[t] = close
            except (KeyError, AttributeError):
                continue
    else:
        # Single ticker
        out[all_tickers[0]] = df["Close"].dropna()
    return out


def run_cross_section_car(restrict_to_dispatch: bool = True) -> dict:
    """Compute CAR for all (NCT, ticker, event_date) with LLM labels.

    restrict_to_dispatch: True -> only NCTs with LLM labels (typical Phase 1).
                         False -> all mapped NCTs (universe view).
    """
    ensure_data_dir()
    labels = _latest_labels_by_nct()
    td = _ticker_and_date_by_nct()

    events = []
    for nct, td_rec in td.items():
        if restrict_to_dispatch and nct not in labels:
            continue
        events.append({
            "nct_id": nct,
            "ticker": td_rec["ticker"],
            "event_date": td_rec["event_date"],
            "labels": labels.get(nct, {}),
        })
    print(f"Events with LLM labels + ticker + date: {len(events)}")

    if not events:
        return {"n_events": 0, "error": "no events"}

    # yfinance batch: full date range
    dates = [datetime.fromisoformat(e["event_date"]) for e in events]
    start = (min(dates) - timedelta(days=20)).strftime("%Y-%m-%d")
    end = (max(dates) + timedelta(days=45)).strftime("%Y-%m-%d")
    tickers = {e["ticker"] for e in events}

    prices = fetch_prices_batch(tickers, start, end)
    print(f"  yfinance returned {len(prices)} ticker series.")

    n_computed = 0
    n_skipped = 0
    by_pivotal: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        car = compute_event_car(prices, e["ticker"], e["event_date"], benchmark="SPY")
        if car is None or all(v is None for v in car.get("horizons", {}).values()):
            n_skipped += 1
            continue
        n_computed += 1
        ps = e["labels"].get("pivotal_shift", "unknown")
        rec = {
            "nct_id": e["nct_id"],
            "ticker": e["ticker"],
            "event_date": e["event_date"],
            "pivotal_shift": ps,
            "admin_vs_substantive": e["labels"].get("admin_vs_substantive"),
            "driver": e["labels"].get("driver"),
            "horizons": car["horizons"],
            "computed_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        append_manifest(MANIFEST_CAR, rec)
        by_pivotal[ps].append(rec)

    return {
        "n_events": len(events),
        "n_computed": n_computed,
        "n_skipped_no_data": n_skipped,
        "by_pivotal_count": {k: len(v) for k, v in by_pivotal.items()},
        "by_pivotal_mean_t_5_car": {
            k: round(sum((r["horizons"].get("t_0_to_5") or {}).get("car", 0) or 0 for r in v) / max(len(v), 1), 4)
            for k, v in by_pivotal.items()
        },
        "by_pivotal_mean_t_30_car": {
            k: round(sum((r["horizons"].get("t_0_to_30") or {}).get("car", 0) or 0 for r in v) / max(len(v), 1), 4)
            for k, v in by_pivotal.items()
        },
    }


if __name__ == "__main__":
    import json
    res = run_cross_section_car(restrict_to_dispatch=True)
    print(json.dumps(res, indent=2, default=str))
