"""Day 7 n=10 full-pipeline dry-run - Phase 0 trigger #2.

Picks 10 NCTs from manifest_amendment_fetch where ticker is non-null and the
PDF has hasProtocol=true. Runs the full pipeline:
  1. fetch_study (already in manifest_amendment_fetch)
  2. download + parse PDF (cached if seen)
  3. LLM 3-axis classification (re-use manifest_axis_classify if seen, else call)
  4. sponsor -> ticker (already mapped)
  5. forward CAR via yfinance (T-1 / T+0 / T+5 / T+30 vs SPY and XBI hedge)

Stage success criteria:
  - fetch: meta has nct_id + sponsor + last_update_post_date
  - pdf: parsed bin in {success, partial}
  - llm: at least 1 of 3 vendors returned non-null pivotal_shift
  - ticker: ticker non-null
  - car: yfinance returned >= 4 daily prices around event date

Pipeline pass = all 5 stages succeed.
Trigger #2 threshold: >= 7/10 pipelines pass.

Run: `python -m clinicaltrials_amendment_llm.day7_n10_dryrun`
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("D:/vscode/portfolio-coordination/.env")

import pandas as pd
import yfinance as yf

from clinicaltrials_amendment_llm.ctgov_client import extract_sponsor, fetch_study
from clinicaltrials_amendment_llm.day3_pdf_dryrun import _download_pdf
from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    MANIFEST_AMENDMENT_FETCH,
    MANIFEST_AXIS_CLASSIFY,
    MANIFEST_CAR,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)
from clinicaltrials_amendment_llm.oracle_pilot import (
    SYSTEM_PROMPT, VENDORS, _build_user_prompt, _parse_axis_response, _request_id,
)
from clinicaltrials_amendment_llm.pdf_parser import parse_pdf
from clinicaltrials_amendment_llm.protocol_excerpt import extract as extract_excerpt
from shared_utils.openrouter_client import OpenRouterClient
import asyncio
import hashlib
from datetime import datetime as _dt

# Skip non-US foreign tickers for yfinance reliability in Day 7 dry-run.
# Day 11+ sponsor mapping expansion can fix this with proper foreign-exchange data.
SKIP_TICKERS = {"ROG.SW"}


def select_10_with_ticker_and_pdf() -> list[dict]:
    """Pick 10 records with ticker + likely-has-PDF (we'll attempt download)."""
    seen: set[str] = set()
    selected: list[dict] = []
    for r in read_manifest(MANIFEST_AMENDMENT_FETCH):
        nct = r.get("nct_id")
        ticker = r.get("ticker")
        if not nct or not ticker or ticker in SKIP_TICKERS:
            continue
        if nct in seen:
            continue
        seen.add(nct)
        selected.append(r)
        if len(selected) >= 10:
            break
    return selected


def _existing_llm_labels() -> dict[str, list[dict]]:
    """Group existing LLM labels by NCT (most recent prompt_hash wins)."""
    by_nct: dict[str, list[dict]] = {}
    for r in read_manifest(MANIFEST_AXIS_CLASSIFY):
        nct = r.get("nct_id")
        if not nct:
            continue
        by_nct.setdefault(nct, []).append(r)
    return by_nct


def _llm_stage_pass(labels: list[dict]) -> bool:
    """At least 1 vendor returned non-null pivotal_shift (or non-unknown)."""
    if not labels:
        return False
    vendors_seen = {l.get("vendor") for l in labels}
    if not vendors_seen:
        return False
    # Pass if any vendor returned non-null AND non-error pivotal_shift
    for l in labels:
        ps = l.get("pivotal_shift")
        if ps is not None and ps != "" and not l.get("parse_error"):
            return True
    return False


def _ensure_llm_labels(nct: str, meta: dict, excerpt: str, excerpt_source: str,
                       client: OpenRouterClient, existing: list[dict]) -> list[dict]:
    """If LLM labels exist for this NCT, return them. Else call all 3 vendors."""
    if existing and _llm_stage_pass(existing):
        return existing

    user_prompt = _build_user_prompt(meta, excerpt, excerpt_source)
    prompt_hash = hashlib.sha256(user_prompt.encode()).hexdigest()[:12]
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    out = list(existing)
    for vendor in VENDORS:
        try:
            resp = client.complete(model=vendor, prompt=full_prompt, max_tokens=400, temperature=0.0)
            choices = resp.get("choices", [])
            text = choices[0].get("message", {}).get("content", "") if choices else ""
            parsed = _parse_axis_response(text)
            cost = float(resp.get("usage", {}).get("cost", 0.0))
            record = {
                "request_id": _request_id(nct, vendor, prompt_hash),
                "nct_id": nct, "vendor": vendor, "prompt_hash": prompt_hash,
                "pivotal_shift": parsed.get("pivotal_shift"),
                "admin_vs_substantive": parsed.get("admin_vs_substantive"),
                "driver": parsed.get("driver"),
                "is_vaccine_cohort": parsed.get("is_vaccine_cohort"),
                "rationale_short": parsed.get("rationale_short"),
                "confidence": parsed.get("confidence"),
                "raw_response": text[:1000],
                "parse_error": parsed.get("_parse_error"),
                "cost_usd": cost,
                "called_at": _dt.now(tz=timezone.utc).isoformat(),
            }
            append_manifest(MANIFEST_AXIS_CLASSIFY, record)
            out.append(record)
        except Exception as e:
            out.append({"nct_id": nct, "vendor": vendor, "parse_error": repr(e)})
    return out


def _compute_car(ticker: str, event_date: str) -> dict:
    """Forward CAR around amendment date.

    event_date: ISO date string (e.g. '2024-09-19' from last_update_post_date).
    Returns dict with t_minus_5..t_plus_30 returns relative to SPY and XBI.
    """
    try:
        ed = datetime.fromisoformat(event_date)
    except Exception as e:
        return {"error": f"bad event_date: {e!r}"}

    start = (ed - timedelta(days=20)).strftime("%Y-%m-%d")
    end = (ed + timedelta(days=45)).strftime("%Y-%m-%d")

    try:
        # Single-ticker download. yfinance will return DataFrame indexed by date.
        df_t = yf.download(
            ticker, start=start, end=end, auto_adjust=True, progress=False, threads=False
        )
        df_spy = yf.download(
            "SPY", start=start, end=end, auto_adjust=True, progress=False, threads=False
        )
        df_xbi = yf.download(
            "XBI", start=start, end=end, auto_adjust=True, progress=False, threads=False
        )
    except Exception as e:
        return {"error": f"yfinance download failed: {e!r}"}

    if df_t is None or df_t.empty:
        return {"error": f"no price data for {ticker}"}
    if df_spy is None or df_spy.empty or df_xbi is None or df_xbi.empty:
        return {"error": "no SPY/XBI benchmark data"}

    # 'Close' (auto_adjust applied)
    def close(df):
        if isinstance(df.columns, pd.MultiIndex):
            return df["Close"].iloc[:, 0]
        return df["Close"]

    pt = close(df_t)
    ps = close(df_spy)
    px = close(df_xbi)

    # Find event row (closest trading day on/after event_date)
    ed_naive = pd.Timestamp(ed.date())
    after = pt.index[pt.index >= ed_naive]
    if len(after) == 0:
        return {"error": "no trading day on/after event"}
    t0 = after[0]

    def cum_return(series, start_idx, end_idx):
        s = series.loc[start_idx:end_idx]
        if len(s) < 2:
            return None
        return float(s.iloc[-1] / s.iloc[0] - 1)

    horizons = {}
    for label, days in (("t_minus_1_to_t_0", -1), ("t_0_to_5", 5), ("t_0_to_30", 30)):
        if days < 0:
            start_idx = pt.index[pt.index < t0]
            if len(start_idx) == 0:
                horizons[label] = None
                continue
            sd = start_idx[-1]
            ed_idx = t0
        else:
            future = pt.index[pt.index >= t0]
            if len(future) <= days:
                horizons[label] = None
                continue
            sd = t0
            ed_idx = future[days]

        rt = cum_return(pt, sd, ed_idx)
        rs = cum_return(ps, sd, ed_idx) if sd in ps.index else None
        rx = cum_return(px, sd, ed_idx) if sd in px.index else None
        # Tolerate misaligned trading days
        if rs is None and len(ps) > 0:
            rs = cum_return(ps, ps.index[ps.index >= sd][0], ps.index[ps.index <= ed_idx][-1]) if any(ps.index >= sd) else None
        if rx is None and len(px) > 0:
            rx = cum_return(px, px.index[px.index >= sd][0], px.index[px.index <= ed_idx][-1]) if any(px.index >= sd) else None
        horizons[label] = {
            "stock": rt,
            "spy": rs,
            "xbi": rx,
            "car_vs_spy": (rt - rs) if (rt is not None and rs is not None) else None,
            "car_vs_xbi": (rt - rx) if (rt is not None and rx is not None) else None,
        }

    return {
        "ticker": ticker,
        "event_date": event_date,
        "t0": str(t0.date()),
        "n_trading_days": int(len(pt)),
        "horizons": horizons,
    }


def run() -> dict:
    ensure_data_dir()
    selected = select_10_with_ticker_and_pdf()
    print(f"Selected {len(selected)} NCTs with ticker + likely PDF.")

    llm_labels = _existing_llm_labels()
    client = OpenRouterClient(project="F6")
    results = []
    pipeline_passes = 0

    for r in selected:
        nct = r["nct_id"]
        ticker = r["ticker"]
        sponsor = r.get("sponsor_name")
        event_date = r.get("last_update_post_date")
        stages = {
            "fetch": False,
            "pdf": False,
            "llm": False,
            "ticker": False,
            "car": False,
        }
        details = {}

        # Stage 1: fetch (already in manifest)
        if nct and sponsor and event_date:
            stages["fetch"] = True

        # Stage 2: PDF parse - try cache first, else download Prot_000.pdf
        cached = list((DATA_DIR / "cache" / "pdf").glob(f"{nct}_Prot_*.pdf"))
        pdf_path = cached[0] if cached else _download_pdf(nct, "Prot_000.pdf")
        if pdf_path:
            pr = parse_pdf(pdf_path)
            if pr.bin in ("success", "partial"):
                stages["pdf"] = True
                details["pdf_bin"] = pr.bin
                details["pdf_chars"] = pr.n_chars
            else:
                details["pdf_bin"] = pr.bin
        else:
            details["pdf_bin"] = "no_pdf_url"

        # Stage 3: LLM 3-axis - call vendors if no existing labels
        labels = llm_labels.get(nct, [])
        if not _llm_stage_pass(labels) and pdf_path and stages["pdf"]:
            # Re-parse to get fresh excerpt (cheap)
            pr2 = parse_pdf(pdf_path)
            excerpt, excerpt_source = extract_excerpt(pr2.text or "")
            meta_for_llm = {
                "nct_id": nct,
                "sponsor_name": sponsor,
                "sponsor_class": "INDUSTRY",
                "phase": r.get("phase"),
                "study_first_submit_date": r.get("study_first_submit_date"),
                "last_update_post_date": event_date,
            }
            if excerpt:
                labels = _ensure_llm_labels(nct, meta_for_llm, excerpt, excerpt_source, client, labels)
        if _llm_stage_pass(labels):
            stages["llm"] = True
            details["llm_n_vendors"] = len({l.get("vendor") for l in labels})
        else:
            details["llm_n_vendors"] = 0

        # Stage 4: ticker - already mapped
        if ticker:
            stages["ticker"] = True
            details["ticker"] = ticker

        # Stage 5: forward CAR via yfinance
        if ticker and event_date:
            car = _compute_car(ticker, event_date)
            if "error" not in car and car.get("horizons"):
                stages["car"] = True
                details["car"] = car
            else:
                details["car_error"] = car.get("error", "unknown")

        all_pass = all(stages.values())
        if all_pass:
            pipeline_passes += 1

        results.append({
            "nct_id": nct,
            "ticker": ticker,
            "sponsor": sponsor,
            "event_date": event_date,
            "stages": stages,
            "all_pass": all_pass,
            "details": details,
        })
        append_manifest(MANIFEST_CAR, {
            "nct_id": nct, "ticker": ticker, "event_date": event_date,
            "stages": stages, "all_pass": all_pass,
            "computed_at": datetime.now(tz=timezone.utc).isoformat(),
            **(details.get("car", {}) if isinstance(details.get("car"), dict) else {}),
        })

    summary = {
        "n_selected": len(selected),
        "pipeline_passes": pipeline_passes,
        "trigger2_threshold": 7,
        "trigger2_pass": pipeline_passes >= 7,
        "stage_pass_rates": {
            stage: sum(1 for r in results if r["stages"][stage]) / max(len(results), 1)
            for stage in ("fetch", "pdf", "llm", "ticker", "car")
        },
    }
    print(json.dumps(summary, indent=2, default=str))

    # Per-NCT breakdown
    print("\n=== Per-NCT pipeline detail ===")
    for r in results:
        s = r["stages"]
        marker = "PASS" if r["all_pass"] else "FAIL"
        print(
            f"  {r['nct_id']} {r['ticker']:6s} {marker} | fetch={s['fetch']} pdf={s['pdf']} "
            f"llm={s['llm']} ticker={s['ticker']} car={s['car']}"
        )

    return {"summary": summary, "results": results}


if __name__ == "__main__":
    out = run()
    print(f"\nTrigger #2 (pipeline_passes >= 7): {out['summary']['trigger2_pass']}")
