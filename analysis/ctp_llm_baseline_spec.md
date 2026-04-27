# CTP-LLM Baseline Replication Spec — F6 Phase 1 trigger #2 prerequisite

**작성일**: 2026-04-27 (Day 1)
**목적**: CTP-LLM (arxiv 2408.10995) 정확 재현 (또는 finetune) — F6 Phase 1 trigger #2 (CTP-LLM 흡수 risk gate, incremental Sharpe Δ ≥ 0.3) 의 baseline 명세화.
**Source**: arxiv abstract (WebFetch 2026-04-27) + IEEE conference publication.

---

## 1. Paper anchor

- **Title**: "CTP-LLM: Clinical Trial Phase Transition Prediction Using Large Language Models"
- **Authors**: Michael Reinisch, Jianfeng He, Chenxi Liao, Sauleh Ahmad Siddiqui, Bei Xiao
- **Venue**: arxiv 2408.10995 (Aug 2024) + IEEE conference (2025)
- **Reported headline**: 67% accuracy across all phase transitions, 75% Phase III → final approval. **NOTE: metric is accuracy, not ROC-AUC** — F6 spec previously assumed ROC-AUC ≥ 0.65 (Phase 1 trigger #1) so baseline replication must report both metrics for apples-to-apples comparison.
- **Model**: fine-tuned GPT-3.5-based.
- **Dataset**: PhaseTransition (PT) Dataset — labels trials by progression through regulatory process. Specific size / split / period not visible in abstract — must be inferred from the IEEE PDF or section §4 of arxiv html.
- **Financial extension**: **None.** Paper is purely clinical. F6 incremental contribution = financial application axis intact.

---

## 2. F6 replication strategy

### Step 1: replicate clinical baseline (Day 13)

We replicate CTP-LLM at the *clinical* level on our own data slice (industry-sponsored biotech R1000 sponsoring firm × IS 2010-2020). Goal: reproduce ~67% accuracy / equivalent ROC-AUC on our universe to confirm the baseline is implementable.

**Inputs**: protocol text per (NCT, version) at the *initial* registration (first version) — i.e., predict eventual phase transition from the protocol-as-registered, NOT from amendments. This matches the CTP-LLM thesis: prediction from original protocol design.

**Output**: binary phase-transition probability per (NCT, target_transition).
Target transitions:
- (a) Phase 1 → Phase 2
- (b) Phase 2 → Phase 3
- (c) Phase 3 → submission/approval

**Model**: instead of fine-tuning GPT-3.5 (deprecated for OpenRouter) we use 3-vendor OpenRouter ensemble with chain-of-thought prompt that asks the LLM to *score* phase-transition likelihood given protocol text. The arxiv finetune was specific to GPT-3.5; we replace with frontier-grade prompted models (Opus 4.7, Sonnet 4.7, Llama-3.3-70B). This is a *deliberate* deviation — F6 is daemon-free + cheaper inference; we pay the methodological note in §Limitations.

**Acceptance**: replication accuracy within ±5pp of paper (62-72% overall) on our test slice. If far below, a fine-tuned smaller model (e.g. Mistral-7B-Instruct via OpenRouter) is the fallback; if far above we suspect leakage and re-audit contamination.

### Step 2: financial extension (Day 14-17)

Use the CTP-LLM phase-transition probability as a *feature* in a monthly cross-section portfolio:

- **Universe**: industry-sponsored biotech R1000 sponsoring firm.
- **Feature_1 (CTP-LLM baseline)**: monthly aggregated phase-transition probability per firm = mean over active trials.
- **Feature_2 (F6 LLM 3-axis pivotal-shift)**: monthly aggregated 3-axis score per firm = mean over recent amendments.
- **Construct**: monthly long-low-pivotal-shift / short-high-pivotal-shift quintile portfolio + XBI hedge.
- **Evaluation**: Sharpe (XBI-hedged) over IS 2010-2020 + OOS 2021-2026.

### Step 3: Two-step regression (Day 17-18 — F6 핵심 결정 gate)

| Step | Features | Target Sharpe |
|---|---|---:|
| 1 (baseline) | Feature_1 (CTP-LLM phase-transition) only | Sharpe_baseline |
| 2 (full) | Feature_1 + Feature_2 (LLM 3-axis pivotal-shift) | Sharpe_full |

**Δ Sharpe = Sharpe_full − Sharpe_baseline**.

**Pass gate**: Δ Sharpe ≥ 0.3 OR partial-alpha t-stat ≥ 2.0 (controlling for Feature_1).
**Fail gate** (writeup-only freeze, NOT full kill): Δ Sharpe < 0.3 → "LLM 3-axis pivotal-shift does not improve over CTP-LLM phase transition baseline for biotech equity alpha" — negative incremental contribution publishable.

---

## 3. Open implementation questions (Day 13 must resolve)

1. **PT Dataset access / construction**: arxiv abstract does not state how the PT Dataset is split. We must construct our own labelled set from CT.gov v2 + Tufts CSDD + FDA approval calendar + Citeline. The phase transition label is derivable from study record state changes (NCT status: completed → next-phase NCT exists for same drug + sponsor).
2. **Initial protocol vs amendment**: CTP-LLM uses initial protocol. F6's contribution is *amendment text*. Step 1 baseline must use *only* initial protocol text to be apples-to-apples; Step 2 layer adds amendment-derived 3-axis features.
3. **Train/test temporal split**: CTP-LLM time period unclear. F6 uses IS 2010-2020 / OOS 2021-2026. Acknowledge in §Limitations that our temporal slice differs.
4. **Multi-class vs binary**: CTP-LLM reports both; F6 baseline collapses to binary (transitions Y/N) per target phase pair.
5. **Contamination**: GPT-3.5 / Opus / Sonnet have training cutoffs that may include the historical trials. Mitigation: per-trial mask drug names + sponsor names in prompt (Lesson F1-3 surrogate; explicit in CLAUDE.md §Statistical Rigor).

---

## 4. Day 13 deliverables

- `analysis/ctp_llm_baseline_replication.ipynb` — replication notebook
- `analysis/ctp_llm_baseline_metrics.json` — accuracy / ROC-AUC per phase pair on our slice
- `data/manifest_ctp_llm_baseline.jsonl` — per-(NCT, target_transition) prediction record
- self-audit log `audits/self_audit_ctp_llm_baseline_2026-MM-DD.md`

---

## 5. Day 17-18 deliverables (the gate)

- `analysis/ctp_llm_incremental.json` — Sharpe_baseline, Sharpe_full, Δ Sharpe, partial-α t-stat
- `data/manifest_incremental_sharpe.jsonl`
- self-audit log

---

## 6. References

- arxiv 2408.10995 — primary anchor
- IEEE Xplore CTP-LLM publication (2025)
- F6 reference-validation §7 (CTP-LLM 흡수 risk)
- F6 Phase 0+1 plan §6 (CTP-LLM 흡수 risk Gate)
- Tufts CSDD / Citeline / FDA approval calendar — outcome label cross-reference

---

**END OF CTP-LLM BASELINE SPEC**

Day 1 obligation discharged. Day 13 replication will fill numeric gaps left by abstract-only access today.
