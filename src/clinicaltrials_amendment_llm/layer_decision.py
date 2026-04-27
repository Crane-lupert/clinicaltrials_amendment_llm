"""Final Layer A/B/C/D close path decision per CLAUDE.md spec + F1-6 lesson.

Reads all Phase 1 measurement outputs (cross_llm_analyzer, day14_midcheckpoint,
incremental_sharpe_regression, rigor_pass) and applies the close-path rules:

- **Layer A (academic success)**:
    - trigger #4 cross-LLM PASS
    - trigger #3 CAR Bonferroni-strict PASS
    - trigger #2 incremental Δ Sharpe ≥ 0.3 OR partial-α t ≥ 2.0 (Bonferroni)
    - F1-1 lock-safe (minority class ≥ 20)

- **Layer D (CTP-LLM 흡수, writeup-only freeze)**:
    - Per CLAUDE.md: trigger #2 < 0.3 → writeup-only freeze (NOT full kill).
    - Negative incremental contribution publishable.

- **Layer C (frozen-as-is mechanical kill)**:
    - trigger #3 fire AND no within-stratum mitigation AND directional reversal.
    - F6's directional signal would have to flip negative.

- **Hybrid A+D**: Layer A finding (within-stratum) + Layer D footnote (additive Δ).

Output: `analysis/F6_layer_decision.json` + console summary.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from clinicaltrials_amendment_llm.manifest import DATA_DIR
from shared_utils.atomic_io import atomic_write_json

ANALYSIS_DIR = DATA_DIR.parent / "analysis"


def _safe_load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def decide_layer() -> dict:
    """Apply close-path rules and return Layer decision."""
    cross_llm_path = ANALYSIS_DIR / "day14_midcheckpoint.json"
    incr_path = ANALYSIS_DIR / "incremental_sharpe_regression.json"
    incr_legacy_path = ANALYSIS_DIR / "incremental_sharpe.json"
    rigor_path = ANALYSIS_DIR / "rigor_pass.json"

    midcheck = _safe_load(cross_llm_path)
    incr = _safe_load(incr_path) or _safe_load(incr_legacy_path)
    rigor = _safe_load(rigor_path)

    # Pull key metrics with safe defaults
    cross_llm = (midcheck.get("cross_llm") or {})
    trigger4_pass = bool(cross_llm.get("trigger4_pass", False))
    cross_llm_rate = cross_llm.get("overall_majority_2of3_rate")

    car_30 = (midcheck.get("car_effect_size_t_0_to_30") or {})
    welch_t_30 = car_30.get("welch_t")
    car_t_uncorrected_pass = bool(car_30.get("trigger3_pass", False))
    bonf_critical = rigor.get("welch_t_threshold_bonferroni_18")
    car_t_bonf_pass = bool(rigor.get("pass_bonferroni_18", False))

    # Incremental Sharpe metrics (regression-based preferred)
    t_pivotal = incr.get("t_pivotal")
    bonf_critical_inc = incr.get("bonferroni_critical_t", bonf_critical or 2.99)
    partial_alpha_uncorrected = bool(incr.get("trigger2_partial_alpha_pass_uncorrected", False))
    partial_alpha_bonf = bool(incr.get("trigger2_partial_alpha_pass_bonferroni", False))
    delta_sharpe = incr.get("delta_sharpe_full_minus_baseline")
    delta_pass = bool(incr.get("trigger2_delta_sharpe_pass", False))
    pivotal_only_sharpe = (incr.get("portfolio_pivotal_only") or {}).get("sharpe")

    # F1-1 lock check
    n_events_regression = incr.get("n_events_in_regression", 0)
    by_pivotal = (rigor.get("by_pivotal_count") or
                  (midcheck.get("car_effect_size_t_0_to_30") or {}).get("by_pivotal_count") or
                  {})
    minority_count = min(by_pivotal.values()) if by_pivotal else 0
    f1_1_lock_safe = minority_count >= 20

    # Layer decision logic
    triggers_summary = {
        "trigger4_cross_llm_majority": trigger4_pass,
        "trigger3_car_uncorrected": car_t_uncorrected_pass,
        "trigger3_car_bonferroni_18": car_t_bonf_pass,
        "trigger2_partial_alpha_uncorrected": partial_alpha_uncorrected,
        "trigger2_partial_alpha_bonferroni": partial_alpha_bonf,
        "trigger2_delta_sharpe_03": delta_pass,
        "f1_1_lock_safe": f1_1_lock_safe,
    }

    # Layer A criteria: all hard triggers PASS (F1-1 lock_safe is a CAVEAT, not gate).
    # Per F1 lesson F1-1: minority<20 means we report results as "tentative",
    # NOT that the result is invalid.
    layer_a_hard = (
        trigger4_pass
        and car_t_bonf_pass
        and (partial_alpha_bonf or delta_pass)
    )

    # Layer C criteria: directional reversal + no signal at all
    layer_c = (
        trigger4_pass
        and not car_t_uncorrected_pass
        and (welch_t_30 is not None and welch_t_30 < 0)  # reversal
    )

    # Layer D criteria: trigger #2 fire (incremental Δ Sharpe < 0.3 AND partial-α not significant)
    layer_d = (
        trigger4_pass
        and not (partial_alpha_bonf or delta_pass)
        and not layer_c  # directional intact
    )

    # Hybrid A+D: Layer A pivotal-only strong + uncorrected CAR PASS, but trigger #2 strict FAIL
    layer_hybrid = (
        trigger4_pass
        and car_t_uncorrected_pass
        and (pivotal_only_sharpe is not None and pivotal_only_sharpe >= 0.5)
        and not (partial_alpha_bonf or delta_pass)
    )

    # F1-1 caveat: tentative-label discipline
    tentative_caveat = not f1_1_lock_safe

    # Pick the strongest matching layer (caveat applied to label, not gate)
    if layer_a_hard:
        layer = "A_TENTATIVE" if tentative_caveat else "A"
        layer_reason = (
            f"All hard triggers PASS Bonferroni-strict (cross-LLM {trigger4_pass}, "
            f"CAR-Bonf {car_t_bonf_pass}, Δ Sharpe {delta_pass} OR partial-α-Bonf {partial_alpha_bonf})."
            + (" F1-1 caveat: minority class < 20 → 'tentative' label until full dispatch lock."
               if tentative_caveat else " F1-1 lock-safe.")
        )
    elif layer_hybrid:
        layer = "Hybrid_A+D" + ("_TENTATIVE" if tentative_caveat else "")
        layer_reason = "Pivotal-only signal strong (Sharpe ≥ 0.5) + uncorrected CAR PASS, but additive Δ Sharpe < 0.3 (writeup acknowledges both)"
    elif layer_d:
        layer = "D" + ("_TENTATIVE" if tentative_caveat else "")
        layer_reason = "Trigger #2 fire (Δ Sharpe < 0.3 strict, partial-α below Bonferroni) — writeup-only freeze, negative incremental publishable per CLAUDE.md"
    elif layer_c:
        layer = "C" + ("_TENTATIVE" if tentative_caveat else "")
        layer_reason = "Directional reversal — F6 thesis falsified at scale"
    else:
        layer = "TENTATIVE"
        layer_reason = "Incomplete measurement — full dispatch pending"

    return {
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
        "n_events_regression": n_events_regression,
        "minority_class_count": minority_count,
        "f1_1_lock_safe": f1_1_lock_safe,
        "tentative": tentative_caveat,
        "metrics": {
            "cross_llm_majority_rate": cross_llm_rate,
            "car_welch_t_30": welch_t_30,
            "car_bonferroni_critical": bonf_critical,
            "incremental_partial_alpha_t": t_pivotal,
            "incremental_bonferroni_critical": bonf_critical_inc,
            "incremental_delta_sharpe": delta_sharpe,
            "pivotal_only_sharpe": pivotal_only_sharpe,
            "by_pivotal_count": by_pivotal,
        },
        "triggers": triggers_summary,
        "candidate_layers": {
            "A_hard_triggers": layer_a_hard,
            "Hybrid_A+D": layer_hybrid,
            "D": layer_d,
            "C": layer_c,
            "tentative_caveat": tentative_caveat,
        },
        "decision": layer,
        "decision_reason": layer_reason,
        "next_action": {
            "A": "Day 19-20: SSRN paper draft + Streamlit dashboard + Day 21 hard cap",
            "A_TENTATIVE": "Continue full dispatch to lock minority class >= 20; preliminary Layer A writeup with F1-1 caveat in §Limitations",
            "Hybrid_A+D": "Day 19-20: paper draft with within-stratum Layer A finding + additive Δ Layer D footnote",
            "Hybrid_A+D_TENTATIVE": "Same as Hybrid_A+D with F1-1 caveat",
            "D": "Day 19-20: writeup-only freeze. Paper headline: 'Why LLM 3-axis pivotal-shift does not improve over CTP-LLM phase transition baseline for biotech equity alpha'",
            "D_TENTATIVE": "Same as D with F1-1 caveat",
            "C": "ABANDONED.md + postmortem + freeze",
            "C_TENTATIVE": "Same as C with F1-1 caveat",
            "TENTATIVE": "Continue full dispatch until F1-1 lock-safe; re-run measurements",
        }.get(layer, "—"),
    }


if __name__ == "__main__":
    res = decide_layer()
    ANALYSIS_DIR.mkdir(exist_ok=True)
    atomic_write_json(ANALYSIS_DIR / "F6_layer_decision.json", res)
    print(json.dumps(res, indent=2, default=str))
