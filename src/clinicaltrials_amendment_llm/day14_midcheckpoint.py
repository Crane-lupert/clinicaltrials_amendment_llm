"""Day 14 mid-checkpoint runner.

Aggregates Phase 1 dispatch outputs into a 3-metric mid-checkpoint report:
1. Cross-LLM consistency (trigger #4 candidate): >= 80% 2/3 majority rate.
2. 3-axis label distribution (sanity / sample power readiness for F1-1 lock).
3. Cross-section CAR effect size (trigger #3 candidate): low-pivotal-shift -
   high-pivotal-shift CAR spread + Welch t-stat.

Phase 1 trigger #1 (phase transition ROC-AUC) requires phase_transition_labels
which depends on phase_transition_labels.py construction (Day 12-13 task).
Excluded from this checkpoint — runs separately.

Output: analysis/day14_midcheckpoint.json + console summary.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from clinicaltrials_amendment_llm.cross_llm_analyzer import measure_cross_llm
from clinicaltrials_amendment_llm.cross_section_car import (
    _latest_labels_by_nct,
    _ticker_and_date_by_nct,
)
from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    MANIFEST_CAR,
    read_manifest,
)
from shared_utils.atomic_io import atomic_write_json

ANALYSIS_DIR = DATA_DIR.parent / "analysis"


def _welch_t(a: list[float], b: list[float]) -> tuple[float, int, int]:
    """Welch's t-statistic. Returns (t_stat, n_a, n_b). t_stat=NaN if degenerate."""
    if len(a) < 2 or len(b) < 2:
        return float("nan"), len(a), len(b)
    n_a, n_b = len(a), len(b)
    mean_a = sum(a) / n_a
    mean_b = sum(b) / n_b
    var_a = sum((x - mean_a) ** 2 for x in a) / (n_a - 1)
    var_b = sum((x - mean_b) ** 2 for x in b) / (n_b - 1)
    se = (var_a / n_a + var_b / n_b) ** 0.5
    if se < 1e-12:
        return float("nan"), n_a, n_b
    return (mean_a - mean_b) / se, n_a, n_b


def axis_distribution() -> dict:
    labels = _latest_labels_by_nct()
    counts: dict[str, dict[str, int]] = {
        "pivotal_shift": defaultdict(int),
        "admin_vs_substantive": defaultdict(int),
        "driver": defaultdict(int),
    }
    for axes in labels.values():
        for axis, val in axes.items():
            counts[axis][val] += 1
    return {
        "n_ncts": len(labels),
        "pivotal_shift": dict(counts["pivotal_shift"]),
        "admin_vs_substantive": dict(counts["admin_vs_substantive"]),
        "driver": dict(counts["driver"]),
    }


def car_effect_size(horizon: str = "t_0_to_5") -> dict:
    """CAR effect size: low-pivotal-shift quintile minus high-pivotal-shift.

    2026-05-17 dedup audit: replaced row-iteration aggregation with
    (nct_id, event_date) dedup. Welch's t-test assumes independent
    observations; re-classification rows of the same amendment are not
    independent and inflated the t-statistic under the prior method.
    Consensus pivotal_shift label per unique amendment is the most-common
    non-unknown label across rows.
    """
    labels = _latest_labels_by_nct()
    seen: dict[tuple[str, str], dict] = {}
    for r in read_manifest(MANIFEST_CAR):
        nct = r.get("nct_id")
        ed = r.get("event_date")
        if not nct or not ed:
            continue
        hzns = r.get("horizons") or {}
        h = hzns.get(horizon)
        if not isinstance(h, dict):
            continue
        car = h.get("car")
        if car is None:
            continue
        key = (nct, ed)
        if key not in seen:
            seen[key] = {"car": float(car), "labels": []}
        ps_row = r.get("pivotal_shift")
        if ps_row:
            seen[key]["labels"].append(ps_row)

    by_pivotal: dict[str, list[float]] = defaultdict(list)
    for (nct, _ed), ev in seen.items():
        consensus = labels.get(nct, {}).get("pivotal_shift")
        if not consensus:
            counts: dict[str, int] = defaultdict(int)
            for v in ev["labels"]:
                if v and v != "unknown":
                    counts[v] += 1
            if counts:
                consensus = max(counts.items(), key=lambda kv: kv[1])[0]
            else:
                consensus = "unknown"
        by_pivotal[consensus].append(ev["car"])

    # Spread: long-positive (positive amendments) vs short-negative (negative amendments).
    # If "negative" is sparse, fall back to neutral as the short leg.
    long_arm = "positive"
    short_arm = "negative" if len(by_pivotal.get("negative", [])) >= 5 else "neutral"

    long_returns = by_pivotal.get(long_arm, [])
    short_returns = by_pivotal.get(short_arm, [])

    t_stat, n_long, n_short = _welch_t(long_returns, short_returns)
    return {
        "horizon": horizon,
        "long_arm": long_arm,
        "short_arm": short_arm,
        "n_long": n_long,
        "n_short": n_short,
        "mean_long_car": round(sum(long_returns) / max(n_long, 1), 4) if long_returns else None,
        "mean_short_car": round(sum(short_returns) / max(n_short, 1), 4) if short_returns else None,
        "spread": round(
            (sum(long_returns) / max(n_long, 1)) - (sum(short_returns) / max(n_short, 1)),
            4,
        ) if (long_returns and short_returns) else None,
        "welch_t": round(t_stat, 4) if not (t_stat != t_stat) else None,  # NaN guard
        "trigger3_threshold_t": 2.0,
        "trigger3_pass": bool(t_stat == t_stat and abs(t_stat) >= 2.0),
        "by_pivotal_count": {k: len(v) for k, v in by_pivotal.items()},
    }


def run_midcheckpoint() -> dict:
    """Compose the 3-metric mid-checkpoint report."""
    cross_llm = measure_cross_llm()
    distrib = axis_distribution()
    car_5 = car_effect_size("t_0_to_5")
    car_30 = car_effect_size("t_0_to_30")

    out = {
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
        "cross_llm": cross_llm,
        "axis_distribution": distrib,
        "car_effect_size_t_0_to_5": car_5,
        "car_effect_size_t_0_to_30": car_30,
        "summary": {
            "n_ncts_with_3_vendor_labels": cross_llm.get("n_ncts_full"),
            "n_ncts_total": distrib.get("n_ncts"),
            "trigger4_cross_llm_pass": cross_llm.get("trigger4_pass"),
            "trigger3_t_5_pass": car_5.get("trigger3_pass"),
            "trigger3_t_30_pass": car_30.get("trigger3_pass"),
        },
    }
    ANALYSIS_DIR.mkdir(exist_ok=True)
    atomic_write_json(ANALYSIS_DIR / "day14_midcheckpoint.json", out)
    return out


if __name__ == "__main__":
    res = run_midcheckpoint()
    print(json.dumps(res, indent=2, default=str))
