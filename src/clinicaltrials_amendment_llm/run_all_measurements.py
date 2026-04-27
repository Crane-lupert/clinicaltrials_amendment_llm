"""Run all Phase 1 measurements in sequence + final layer decision.

After dispatch + phase_transition_labels complete, this orchestrates:
1. cross_section_car (CAR per (NCT, event_date, ticker))
2. cross_llm_analyzer (trigger #4)
3. day14_midcheckpoint (composite mid-checkpoint)
4. incremental_sharpe_regression (trigger #2 partial-α + Δ Sharpe)
5. rigor_pass (trigger #3 Bonferroni + bootstrap + DSR)
6. phase_transition_roc (trigger #1 ROC-AUC if labels available)
7. layer_decision (Layer A/B/C/D)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from clinicaltrials_amendment_llm.cross_llm_analyzer import measure_cross_llm
from clinicaltrials_amendment_llm.cross_section_car import run_cross_section_car
from clinicaltrials_amendment_llm.day14_midcheckpoint import run_midcheckpoint
from clinicaltrials_amendment_llm.incremental_sharpe_regression import run_regression_incremental
from clinicaltrials_amendment_llm.layer_decision import decide_layer
from clinicaltrials_amendment_llm.manifest import (
    DATA_DIR,
    MANIFEST_PHASE_TRANSITION,
    read_manifest,
)
from clinicaltrials_amendment_llm.rigor_pass import run_rigor_pass
from shared_utils.atomic_io import atomic_write_json

ANALYSIS_DIR = DATA_DIR.parent / "analysis"


def measure_phase_transition_roc() -> dict:
    """Trigger #1: ROC-AUC of LLM 3-axis pivotal-shift score vs phase transition outcome.

    Simple measure: among trials with `transitioned: True` outcome, did LLM
    pivotal_shift skew positive vs trials with `transitioned: False`?
    """
    from clinicaltrials_amendment_llm.cross_section_car import _latest_labels_by_nct

    pt_records = list(read_manifest(MANIFEST_PHASE_TRANSITION))
    if len(pt_records) < 20:
        return {"n_pt_records": len(pt_records), "error": "phase_transition_labels not yet generated"}

    # Build NCT -> transition status
    pt_by_nct: dict[str, bool] = {}
    for r in pt_records:
        nct = r.get("nct_id")
        if nct:
            pt_by_nct[nct] = bool(r.get("transitioned"))

    labels = _latest_labels_by_nct()

    # Pair LLM pivotal_shift with transition outcome
    score_label_pairs = []
    for nct, axes in labels.items():
        if nct not in pt_by_nct:
            continue
        ps = axes.get("pivotal_shift")
        if ps == "positive":
            s = 1.0
        elif ps == "negative":
            s = -1.0
        else:
            s = 0.0
        score_label_pairs.append((s, pt_by_nct[nct]))

    if len(score_label_pairs) < 20:
        return {
            "n_pt_records": len(pt_records),
            "n_paired": len(score_label_pairs),
            "error": "n<20 paired (LLM × phase_transition) — need more dispatch",
        }

    # ROC-AUC via Mann-Whitney U
    pos_scores = [s for s, lab in score_label_pairs if lab]
    neg_scores = [s for s, lab in score_label_pairs if not lab]
    n_pos = len(pos_scores)
    n_neg = len(neg_scores)
    if n_pos == 0 or n_neg == 0:
        return {"n_paired": len(score_label_pairs), "error": "one class missing"}

    # Mann-Whitney U statistic
    rank_sum = 0
    all_scores = sorted(pos_scores + neg_scores)
    rank_map: dict[float, list[int]] = {}
    for i, s in enumerate(all_scores, 1):
        rank_map.setdefault(s, []).append(i)
    avg_ranks = {s: sum(rs) / len(rs) for s, rs in rank_map.items()}
    rank_sum_pos = sum(avg_ranks[s] for s in pos_scores)
    U = rank_sum_pos - n_pos * (n_pos + 1) / 2
    auc = U / (n_pos * n_neg)

    return {
        "n_pt_records": len(pt_records),
        "n_paired": len(score_label_pairs),
        "n_transitioned": n_pos,
        "n_not_transitioned": n_neg,
        "transition_rate_in_paired": round(n_pos / len(score_label_pairs), 4),
        "roc_auc": round(auc, 4),
        "trigger1_threshold": 0.65,
        "trigger1_pass": auc >= 0.65,
    }


def run_all() -> dict:
    print("=== Running all Phase 1 measurements ===", flush=True)

    print("\n[1/7] cross_section_car ...", flush=True)
    car = run_cross_section_car(restrict_to_dispatch=True)
    print(f"  events computed: {car.get('n_computed')}", flush=True)

    print("\n[2/7] cross_llm_analyzer ...", flush=True)
    cross_llm = measure_cross_llm()
    print(f"  cross-LLM 2/3 majority: {cross_llm.get('overall_majority_2of3_rate')}", flush=True)

    print("\n[3/7] day14_midcheckpoint ...", flush=True)
    mid = run_midcheckpoint()
    print(f"  car_t_30 t-stat: {mid.get('car_effect_size_t_0_to_30', {}).get('welch_t')}", flush=True)

    print("\n[4/7] incremental_sharpe_regression ...", flush=True)
    incr = run_regression_incremental()
    print(f"  partial-α t (pivotal): {incr.get('t_pivotal')}", flush=True)
    print(f"  Δ Sharpe: {incr.get('delta_sharpe_full_minus_baseline')}", flush=True)

    print("\n[5/7] rigor_pass ...", flush=True)
    rigor = run_rigor_pass()
    atomic_write_json(ANALYSIS_DIR / "rigor_pass.json", rigor)
    print(f"  Bonferroni-18 PASS: {rigor.get('pass_bonferroni_18')}", flush=True)

    print("\n[6/7] phase_transition_roc ...", flush=True)
    roc = measure_phase_transition_roc()
    atomic_write_json(ANALYSIS_DIR / "phase_transition_roc.json", roc)
    print(f"  ROC-AUC: {roc.get('roc_auc')} | trigger #1 PASS: {roc.get('trigger1_pass')}", flush=True)

    print("\n[7/7] layer_decision ...", flush=True)
    layer = decide_layer()
    atomic_write_json(ANALYSIS_DIR / "F6_layer_decision.json", layer)
    print(f"  DECISION: Layer {layer.get('decision')}", flush=True)
    print(f"  REASON: {layer.get('decision_reason')}".encode('utf-8', errors='replace').decode('ascii', errors='replace'), flush=True)

    out = {
        "computed_at": datetime.now(tz=timezone.utc).isoformat(),
        "measurements": {
            "cross_section_car": car,
            "cross_llm": cross_llm,
            "midcheckpoint": mid,
            "incremental_sharpe_regression": incr,
            "rigor_pass": rigor,
            "phase_transition_roc": roc,
        },
        "layer_decision": layer,
    }
    atomic_write_json(ANALYSIS_DIR / "F6_final_summary.json", out)
    return out


if __name__ == "__main__":
    res = run_all()
    print("\n=== FINAL SUMMARY ===")
    print(json.dumps(res["layer_decision"], indent=2, default=str))
