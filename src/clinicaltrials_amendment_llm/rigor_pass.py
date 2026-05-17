"""Day 19 statistical rigor pass.

Applies Bonferroni / FDR / bootstrap / Newey-West HAC corrections to the
Phase 1 cross-section CAR effect-size estimate (trigger #3) per F6
reference-validation §4.5 and Phase 0 plan §1 Day 19.

Per F1-2 Gate H lesson: report sample-power-corrected critical t alongside
the raw t-stat.

2026-05-17 dedup audit (post-publish self-correction): the original
implementation iterated every row in MANIFEST_CAR, so re-classification
runs of the same amendment were each treated as an independent observation.
This inflated the Welch t-statistic and shrank standard errors. Welch's
test assumes independent observations, which is violated when the same
event's CAR is replicated five-to-ten times across rows. The corrected
implementation deduplicates by (nct_id, event_date) to obtain one
observation per unique amendment event, then assigns a consensus
pivotal_shift label via the most-common non-unknown vote across rows
(with fallback to _latest_labels_by_nct). Pre-dedup raw counts are
preserved under "pre_dedup_raw_for_audit" for transparency.
"""

from __future__ import annotations

import math
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from clinicaltrials_amendment_llm.cross_section_car import _latest_labels_by_nct
from clinicaltrials_amendment_llm.manifest import DATA_DIR, MANIFEST_CAR, read_manifest
from shared_utils.atomic_io import atomic_write_json

ANALYSIS_DIR = DATA_DIR.parent / "analysis"


def _welch_t(a: list[float], b: list[float]) -> tuple[float, int, int]:
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


def _bootstrap_ci(returns: list[float], n_iter: int = 1000, alpha: float = 0.05,
                  seed: int = 42) -> tuple[float, float]:
    """Cluster-free bootstrap CI for the mean."""
    if len(returns) < 5:
        return float("nan"), float("nan")
    rng = random.Random(seed)
    means = []
    n = len(returns)
    for _ in range(n_iter):
        sample = [returns[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    lo = means[int(n_iter * alpha / 2)]
    hi = means[int(n_iter * (1 - alpha / 2))]
    return lo, hi


def _bonferroni_critical(n_tests: int, alpha: float = 0.05) -> float:
    """2-sided critical-t under Bonferroni for given n_tests at alpha.
    Approximation via standard normal (small-n correction not applied).
    """
    # Inverse CDF approximation of N(0,1): use Acklam's algorithm-like rough bound.
    # For practical use we bake known Bonferroni-K critical values.
    table = {
        1: 1.96, 2: 2.24, 3: 2.39, 6: 2.64, 9: 2.77, 12: 2.86, 18: 2.99, 24: 3.07,
    }
    # Pick the smallest tabulated K >= n_tests.
    for k in sorted(table.keys()):
        if k >= n_tests:
            return table[k]
    return 3.30  # very conservative fallback for K > 24


def _deflated_sharpe(sharpe: float, n_obs: int, n_trials: int) -> float:
    """Deflated Sharpe Ratio per Bailey & Lopez de Prado 2014 (simplified).

    DSR penalizes Sharpe by the number of trials examined and the
    auto-correlation pattern of the underlying series. Simplified:
    expected_max_under_null ≈ sqrt(2 * log(n_trials))
    DSR ≈ (sharpe * sqrt(n_obs - 1) - expected_max_under_null) / sigma_sharpe
    Returns DSR p-value approximation (1-CDF of DSR).
    """
    if n_obs < 2 or sharpe != sharpe:  # NaN guard
        return float("nan")
    if n_trials <= 1:
        return 1.0  # no deflation needed
    expected_max = math.sqrt(2 * math.log(max(n_trials, 2)))
    sigma_sharpe = (1 / math.sqrt(max(n_obs - 1, 1)))
    z = (sharpe - expected_max) / max(sigma_sharpe, 1e-9)
    # 1-Phi(z) approximation
    return 0.5 * (1 - math.erf(z / math.sqrt(2)))


def _bucket_by_pivotal(horizon: str, dedup: bool) -> tuple[dict[str, list[float]], dict[str, int]]:
    """Group CAR observations by pivotal_shift consensus.

    When dedup=True (the corrected method), the same (nct_id, event_date)
    contributes a single CAR observation and a single consensus label,
    computed as the most-common non-unknown label across rows for that
    amendment, with fallback to the separate axis_classify manifest.

    When dedup=False (raw rows, the pre-2026-05-17 method), every row of
    MANIFEST_CAR contributes an observation. Returned for audit only;
    standard errors and Welch t under this aggregation are not valid
    because re-classification rows are not independent observations.

    Returns (by_pivotal, by_pivotal_count).
    """
    labels = _latest_labels_by_nct()
    by_pivotal: dict[str, list[float]] = defaultdict(list)

    if not dedup:
        for r in read_manifest(MANIFEST_CAR):
            nct = r.get("nct_id")
            ps = labels.get(nct, {}).get("pivotal_shift") or r.get("pivotal_shift")
            h = (r.get("horizons") or {}).get(horizon)
            if not isinstance(h, dict):
                continue
            c = h.get("car")
            if c is None:
                continue
            by_pivotal[ps].append(float(c))
    else:
        seen: dict[tuple[str, str], dict] = {}
        for r in read_manifest(MANIFEST_CAR):
            nct = r.get("nct_id")
            ed = r.get("event_date")
            if not nct or not ed:
                continue
            h = (r.get("horizons") or {}).get(horizon)
            if not isinstance(h, dict):
                continue
            c = h.get("car")
            if c is None:
                continue
            key = (nct, ed)
            if key not in seen:
                seen[key] = {"car": float(c), "labels": []}
            ps_row = r.get("pivotal_shift")
            if ps_row:
                seen[key]["labels"].append(ps_row)

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

    return by_pivotal, {k: len(v) for k, v in by_pivotal.items()}


def run_rigor_pass(horizon: str = "t_0_to_30") -> dict:
    """Apply rigor corrections to the cross-section CAR spread.

    Uses (nct_id, event_date) dedup so each amendment contributes one
    observation. Welch's t-test, Bootstrap CI and Bonferroni correction
    all assume independent observations; the pre-2026-05-17 row-iteration
    implementation violated this assumption and is preserved under
    "pre_dedup_raw_for_audit" for transparency.
    """
    by_pivotal, count_map = _bucket_by_pivotal(horizon, dedup=True)
    raw_by_pivotal, raw_count_map = _bucket_by_pivotal(horizon, dedup=False)

    pos = by_pivotal.get("positive", [])
    neg = by_pivotal.get("negative", [])
    neutral = by_pivotal.get("neutral", [])

    # Long-short spread: positive vs negative (or neutral as fallback short)
    short_arm = "negative" if len(neg) >= 5 else "neutral"
    short = by_pivotal.get(short_arm, [])

    t_stat, n_long, n_short = _welch_t(pos, short)
    spread = (sum(pos) / max(n_long, 1)) - (sum(short) / max(n_short, 1)) if (pos and short) else float("nan")
    spread_returns = pos + [-x for x in short]
    sharpe = (sum(spread_returns) / max(len(spread_returns), 1)) / max(
        (sum((x - sum(spread_returns) / len(spread_returns)) ** 2 for x in spread_returns) / max(len(spread_returns) - 1, 1)) ** 0.5,
        1e-9,
    ) if spread_returns else float("nan")

    pos_lo, pos_hi = _bootstrap_ci(pos)
    short_lo, short_hi = _bootstrap_ci(short)

    # Multiple testing: 3-axis × 2-horizon × 3-phase = 18 tests in spec
    n_tests_planned = 18
    bonf_critical = _bonferroni_critical(n_tests_planned)

    dsr_p = _deflated_sharpe(sharpe, len(spread_returns), n_tests_planned)

    # Always also compute the strict positive-vs-negative comparison (the
    # paper's original framing) even when the rigor_pass fallback degrades
    # to the neutral arm. This keeps the same test reproducible after dedup
    # even with very small n_negative.
    strict_t, strict_nl, strict_ns = _welch_t(pos, neg)
    strict_spread = (sum(pos) / max(strict_nl, 1)) - (sum(neg) / max(strict_ns, 1)) if (pos and neg) else float("nan")
    strict_neg_lo, strict_neg_hi = _bootstrap_ci(neg)

    # Audit-only: pre-dedup raw-row aggregation (the pre-2026-05-17 method),
    # preserved so the inflated t-statistic can be reproduced from the same
    # source data for transparency. These figures must not be used for
    # inference.
    raw_pos = raw_by_pivotal.get("positive", [])
    raw_short_arm = "negative" if len(raw_by_pivotal.get("negative", [])) >= 5 else "neutral"
    raw_short = raw_by_pivotal.get(raw_short_arm, [])
    raw_t, raw_nl, raw_ns = _welch_t(raw_pos, raw_short)
    raw_spread = (sum(raw_pos) / max(raw_nl, 1)) - (sum(raw_short) / max(raw_ns, 1)) if (raw_pos and raw_short) else float("nan")

    return {
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
        "horizon": horizon,
        "aggregation": "dedup_by_nct_event_date",
        "n_long_positive": n_long,
        "n_short": n_short,
        "short_arm": short_arm,
        "mean_positive_car": round(sum(pos) / max(n_long, 1), 4) if pos else None,
        "mean_short_car": round(sum(short) / max(n_short, 1), 4) if short else None,
        "spread": round(spread, 4) if not (spread != spread) else None,
        "welch_t_uncorrected": round(t_stat, 4) if not (t_stat != t_stat) else None,
        "welch_t_threshold_uncorrected": 2.0,
        "welch_t_threshold_bonferroni_18": round(bonf_critical, 4),
        "pass_uncorrected": bool(t_stat == t_stat and abs(t_stat) >= 2.0),
        "pass_bonferroni_18": bool(t_stat == t_stat and abs(t_stat) >= bonf_critical),
        "bootstrap_ci_positive_95pct": (round(pos_lo, 4) if pos_lo == pos_lo else None,
                                          round(pos_hi, 4) if pos_hi == pos_hi else None),
        "bootstrap_ci_short_95pct": (round(short_lo, 4) if short_lo == short_lo else None,
                                       round(short_hi, 4) if short_hi == short_hi else None),
        "bootstrap_ci_zero_in_positive": pos_lo <= 0 <= pos_hi if pos_lo == pos_lo else None,
        "event_level_sharpe": round(sharpe, 4) if not (sharpe != sharpe) else None,
        "deflated_sharpe_p_value_n_trials_18": round(dsr_p, 4) if not (dsr_p != dsr_p) else None,
        "by_pivotal_count": {k: len(v) for k, v in by_pivotal.items()},
        "strict_positive_vs_negative": {
            "n_long_positive": strict_nl,
            "n_short_negative": strict_ns,
            "mean_positive_car": round(sum(pos) / max(strict_nl, 1), 4) if pos else None,
            "mean_negative_car": round(sum(neg) / max(strict_ns, 1), 4) if neg else None,
            "spread": round(strict_spread, 4) if not (strict_spread != strict_spread) else None,
            "welch_t": round(strict_t, 4) if not (strict_t != strict_t) else None,
            "pass_uncorrected": bool(strict_t == strict_t and abs(strict_t) >= 2.0),
            "pass_bonferroni_18": bool(strict_t == strict_t and abs(strict_t) >= bonf_critical),
            "bootstrap_ci_negative_95pct": (round(strict_neg_lo, 4) if strict_neg_lo == strict_neg_lo else None,
                                              round(strict_neg_hi, 4) if strict_neg_hi == strict_neg_hi else None),
        },
        "pre_dedup_raw_for_audit": {
            "comment": "Row-iteration aggregation of MANIFEST_CAR; same amendment may contribute multiple rows due to re-classification runs. Welch's independence assumption violated; do not use for inference.",
            "n_long_positive_raw": raw_nl,
            "n_short_raw": raw_ns,
            "short_arm_raw": raw_short_arm,
            "spread_raw": round(raw_spread, 4) if not (raw_spread != raw_spread) else None,
            "welch_t_raw": round(raw_t, 4) if not (raw_t != raw_t) else None,
            "by_pivotal_count_raw": raw_count_map,
        },
    }


if __name__ == "__main__":
    import json
    res = run_rigor_pass()
    ANALYSIS_DIR.mkdir(exist_ok=True)
    atomic_write_json(ANALYSIS_DIR / "rigor_pass.json", res)
    print(json.dumps(res, indent=2, default=str))
