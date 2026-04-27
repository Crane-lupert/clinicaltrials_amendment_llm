"""Day 17-18 CTP-LLM 흡수 — regression-based partial-α (proper measurement).

User-directive 2026-04-28: replace additive scoring with regression-based
partial-α. The previous incremental_sharpe.py used score-additive Δ Sharpe
which had a scale-mismatch artifact (phase score [2,3] dwarfs pivotal
score [-1,+1] when added directly).

Proper measurement (per Phase 0 plan §6.1, F1 frozen rigor_pass pattern):

    CAR_i = α + β1 · phase_i + β2 · pivotal_i + ε_i

- β2 t-stat tests whether pivotal_shift adds CAR-predictive power AFTER
  controlling for phase. This is the partial-α coefficient.
- |β2_t| ≥ 2.0 (Bonferroni-K corrected) → trigger #2 PASS at the
  *signal-existence* level.
- F6 incremental Sharpe Δ via constructed portfolios:
    baseline_score = phase only
    full_score     = phase + pivotal (regression-fitted weight)
    Δ Sharpe = Sharpe(full portfolio) - Sharpe(baseline portfolio)

Returns both (a) regression t-stat on β2 and (b) portfolio-level Δ Sharpe
using regression-fitted (not additive) feature weights.
"""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from clinicaltrials_amendment_llm.cross_section_car import _latest_labels_by_nct
from clinicaltrials_amendment_llm.incremental_sharpe import _baseline_score, _pivotal_score
from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    MANIFEST_AMENDMENT_FETCH,
    MANIFEST_CAR,
    MANIFEST_INCREMENTAL_SHARPE,
    append_manifest,
    ensure_data_dir,
    read_manifest,
)
from shared_utils.atomic_io import atomic_write_json

ANALYSIS_DIR = DATA_DIR.parent / "analysis"


def _ols(X: list[list[float]], y: list[float]) -> dict:
    """Minimal OLS via normal equations: β = (X'X)^-1 X'y. Returns betas + se + t.

    X is (n, k) list-of-rows including intercept column. y is (n,) list.
    """
    n = len(y)
    if n == 0:
        return {"error": "empty"}
    k = len(X[0])

    # X'X (k × k), X'y (k,)
    xtx = [[0.0] * k for _ in range(k)]
    xty = [0.0] * k
    for i in range(n):
        for a in range(k):
            xty[a] += X[i][a] * y[i]
            for b in range(k):
                xtx[a][b] += X[i][a] * X[i][b]

    # Invert k × k via Gauss-Jordan (k typically 2 or 3)
    inv = [[1.0 if i == j else 0.0 for j in range(k)] for i in range(k)]
    aug = [row[:] + inv_row for row, inv_row in zip(xtx, inv)]
    for i in range(k):
        # Pivot
        if abs(aug[i][i]) < 1e-12:
            for r in range(i + 1, k):
                if abs(aug[r][i]) > 1e-12:
                    aug[i], aug[r] = aug[r], aug[i]
                    break
            else:
                return {"error": "singular X'X"}
        piv = aug[i][i]
        for j in range(2 * k):
            aug[i][j] /= piv
        for r in range(k):
            if r == i:
                continue
            factor = aug[r][i]
            for j in range(2 * k):
                aug[r][j] -= factor * aug[i][j]

    inv_xtx = [[aug[i][j + k] for j in range(k)] for i in range(k)]

    # β = inv(X'X) X'y
    beta = [sum(inv_xtx[a][b] * xty[b] for b in range(k)) for a in range(k)]

    # Residuals + σ²
    sse = 0.0
    for i in range(n):
        y_hat = sum(X[i][a] * beta[a] for a in range(k))
        sse += (y[i] - y_hat) ** 2
    if n - k <= 0:
        return {"error": f"n-k={n - k}<=0"}
    sigma2 = sse / (n - k)

    # SE: sqrt(sigma² × diag(inv(X'X)))
    se = [math.sqrt(max(sigma2 * inv_xtx[a][a], 0.0)) for a in range(k)]
    t = [(beta[a] / se[a]) if se[a] > 1e-12 else float("nan") for a in range(k)]

    return {
        "n": n,
        "k": k,
        "beta": beta,
        "se": se,
        "t": t,
        "sse": sse,
        "sigma2": sigma2,
    }


def _bonferroni_critical(n_tests: int) -> float:
    """2-sided 95% critical-t for Bonferroni-K (rough table)."""
    table = {1: 1.96, 2: 2.24, 3: 2.39, 6: 2.64, 9: 2.77, 12: 2.86, 18: 2.99, 24: 3.07}
    for k in sorted(table.keys()):
        if k >= n_tests:
            return table[k]
    return 3.30


def _compute_sharpe(returns: list[float]) -> tuple[float, int]:
    n = len(returns)
    if n < 2:
        return float("nan"), n
    mean = sum(returns) / n
    var = sum((x - mean) ** 2 for x in returns) / (n - 1)
    if var <= 0:
        return float("nan"), n
    return (mean / math.sqrt(var)) * math.sqrt(n), n


def _portfolio_sharpe_by_score(events: list[dict], score_fn, *, horizon: str = "t_0_to_30") -> dict:
    enriched = []
    for e in events:
        score = score_fn(e)
        car = (e.get("horizons", {}) or {}).get(horizon)
        if not isinstance(car, dict):
            continue
        c = car.get("car")
        if c is None:
            continue
        enriched.append({"score": score, "car": float(c)})
    if len(enriched) < 6:
        return {"n": len(enriched), "sharpe": None, "error": "n<6"}
    enriched.sort(key=lambda r: r["score"])
    tercile = max(2, len(enriched) // 3)
    short_leg = enriched[:tercile]
    long_leg = enriched[-tercile:]
    port = [r["car"] for r in long_leg] + [-r["car"] for r in short_leg]
    sharpe, _ = _compute_sharpe(port)
    return {
        "n_total": len(enriched),
        "n_long": len(long_leg),
        "n_short": len(short_leg),
        "sharpe": round(sharpe, 4) if not math.isnan(sharpe) else None,
        "long_mean_car": round(sum(r["car"] for r in long_leg) / len(long_leg), 4),
        "short_mean_car": round(sum(r["car"] for r in short_leg) / len(short_leg), 4),
    }


def run_regression_incremental(horizon: str = "t_0_to_30", n_tests_planned: int = 18) -> dict:
    """Regression-based partial-α + portfolio Δ Sharpe.

    Linear model: CAR ~ α + β1·phase + β2·pivotal
    PASS gate: |β2_t| ≥ Bonferroni-K critical (default K=18 per spec).
    Returns both t-stat and portfolio Sharpe Δ.
    """
    ensure_data_dir()

    car_by_nct = {r["nct_id"]: r for r in read_manifest(MANIFEST_CAR) if r.get("nct_id")}
    fetch_by_nct = {r["nct_id"]: r for r in read_manifest(MANIFEST_AMENDMENT_FETCH) if r.get("nct_id")}
    labels = _latest_labels_by_nct()

    events = []
    for nct, car in car_by_nct.items():
        ph = (fetch_by_nct.get(nct) or {}).get("phase")
        ps = labels.get(nct, {}).get("pivotal_shift")
        events.append({
            "nct_id": nct,
            "phase": ph,
            "pivotal_shift": ps,
            "horizons": car.get("horizons", {}),
        })
    print(f"Events: {len(events)}")

    # Build regression dataset (CAR, phase, pivotal): exclude unknowns + missing CAR
    X = []
    y = []
    for e in events:
        h = (e.get("horizons", {}) or {}).get(horizon)
        if not isinstance(h, dict):
            continue
        c = h.get("car")
        if c is None:
            continue
        ps = e.get("pivotal_shift")
        # Keep all categories including 'unknown' as 0 — they're abstentions
        # and removing them would bias toward the discriminative subset.
        phase_s = _baseline_score(e.get("phase"))
        pivotal_s = _pivotal_score(ps)
        X.append([1.0, phase_s, pivotal_s])  # intercept, phase, pivotal
        y.append(float(c))

    if len(y) < 10:
        return {"error": "n<10 — too few for regression", "n": len(y)}

    reg = _ols(X, y)
    if "error" in reg:
        return {"error": reg["error"], "n": len(y)}

    # β2 is the pivotal coefficient (controlling for phase)
    beta_pivotal = reg["beta"][2]
    t_pivotal = reg["t"][2]
    se_pivotal = reg["se"][2]

    bonf_critical = _bonferroni_critical(n_tests_planned)

    # Also compute univariate regressions for comparison
    X_phase = [[1.0, row[1]] for row in X]
    X_pivotal = [[1.0, row[2]] for row in X]
    reg_phase = _ols(X_phase, y)
    reg_pivotal_only = _ols(X_pivotal, y)

    # Portfolio Sharpe Δ (regression-fitted weights vs phase-only)
    # Baseline portfolio: sort by phase only
    baseline_port = _portfolio_sharpe_by_score(events, lambda e: _baseline_score(e.get("phase")), horizon=horizon)
    # Full portfolio: sort by regression-fitted score
    def fitted_score(e):
        phase_s = _baseline_score(e.get("phase"))
        pivotal_s = _pivotal_score(e.get("pivotal_shift"))
        return reg["beta"][1] * phase_s + reg["beta"][2] * pivotal_s
    full_port = _portfolio_sharpe_by_score(events, fitted_score, horizon=horizon)
    # Pivotal-only portfolio (signal standalone)
    pivotal_port = _portfolio_sharpe_by_score(events, lambda e: _pivotal_score(e.get("pivotal_shift")), horizon=horizon)

    delta_sharpe = None
    if baseline_port.get("sharpe") is not None and full_port.get("sharpe") is not None:
        delta_sharpe = round(full_port["sharpe"] - baseline_port["sharpe"], 4)

    result = {
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
        "n_events_in_regression": len(y),
        "horizon": horizon,
        "regression_full_model": {
            "betas": [round(b, 6) for b in reg["beta"]],  # [intercept, phase, pivotal]
            "se": [round(s, 6) for s in reg["se"]],
            "t_stats": [round(t, 4) for t in reg["t"]],
            "sigma": round(math.sqrt(reg["sigma2"]), 4),
        },
        "beta_pivotal": round(beta_pivotal, 6),
        "se_pivotal": round(se_pivotal, 6),
        "t_pivotal": round(t_pivotal, 4),
        "regression_phase_only": {
            "beta_phase": round(reg_phase["beta"][1], 6) if "beta" in reg_phase else None,
            "t_phase": round(reg_phase["t"][1], 4) if "t" in reg_phase else None,
        },
        "regression_pivotal_only": {
            "beta_pivotal": round(reg_pivotal_only["beta"][1], 6) if "beta" in reg_pivotal_only else None,
            "t_pivotal_only": round(reg_pivotal_only["t"][1], 4) if "t" in reg_pivotal_only else None,
        },
        "bonferroni_K_planned": n_tests_planned,
        "bonferroni_critical_t": round(bonf_critical, 4),
        "trigger2_partial_alpha_pass_uncorrected": abs(t_pivotal) >= 2.0 if not math.isnan(t_pivotal) else False,
        "trigger2_partial_alpha_pass_bonferroni": abs(t_pivotal) >= bonf_critical if not math.isnan(t_pivotal) else False,
        "portfolio_baseline_phase_only": baseline_port,
        "portfolio_full_regression_fitted": full_port,
        "portfolio_pivotal_only": pivotal_port,
        "delta_sharpe_full_minus_baseline": delta_sharpe,
        "trigger2_delta_sharpe_pass": delta_sharpe is not None and delta_sharpe >= 0.3,
        "interpretation": (
            "Proper partial-α via OLS: β2 t-stat tests whether pivotal_shift adds "
            "incremental CAR-predictive power AFTER controlling for phase. "
            "|t| ≥ 2.0 (Bonferroni-K) → trigger #2 PASS at signal-existence level. "
            "Δ Sharpe (regression-fitted weights vs phase-only) = portfolio-level "
            "incremental contribution. Both metrics needed for confident PASS."
        ),
    }

    append_manifest(MANIFEST_INCREMENTAL_SHARPE, result)
    ANALYSIS_DIR.mkdir(exist_ok=True)
    atomic_write_json(ANALYSIS_DIR / "incremental_sharpe_regression.json", result)
    return result


if __name__ == "__main__":
    import json
    res = run_regression_incremental()
    print(json.dumps(res, indent=2, default=str))
