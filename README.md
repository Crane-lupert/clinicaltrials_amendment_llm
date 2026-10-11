# F6 — ClinicalTrials.gov Protocol Amendment LLM

ClinicalTrials.gov v2 amendment text × multi-vendor LLM ensemble × 3-axis *pivotal shift* classification → biotech forward CAR cross-section.

**Status**: ❌ **Layer A LOCK retracted** — locked 2026-04-28, downgraded 2026-05-17 (self-correction #1), no pre-registered pass route left after self-correction #2 (2026-10-11). Pre-registered close path: writeup-only freeze. See *Erratum* below. **한국어 실무 보고**: [README_KR.md](README_KR.md).
**Type**: discovery-form alpha-research, F1 frozen swap-queue 1순위 fill (the Layer A claim is retracted — see *Erratum*).
**Daemon**: PURE daemon-free (Gate F ✓) — ClinicalTrials.gov v2 API + yfinance + OpenRouter only.

## Erratum — Post-publication self-correction #2 (2026-10-11)

The incremental-Sharpe result (Phase 1 trigger #2, "ΔSharpe = +0.341 ≥ 0.30, PASS") is **withdrawn**. It was the last pass claim left after self-correction #1.

**Previously reported**: baseline (phase only) 0.194, full (regression-fitted) 0.535, ΔSharpe **+0.341** (margin 0.041); pivotal-only 1.088; "additive 0.066 → regression-fitted 0.341" presented as a scale-mismatch fix.

**What is wrong.** The arithmetic reproduces exactly from `data/manifest_*.jsonl`. The statistic cannot carry the gate:

1. Each "Sharpe" is mean / sd × √n over the 52 pooled long and sign-flipped short events, i.e. a one-sample t-statistic. Per event, ΔSharpe = **0.047**.
2. The full-model weights are OLS-fitted on the same 80 events that are then ranked. Under a permutation null (shuffle CAR, refit OLS, 10,000 draws), **68%** of draws reach ΔSharpe ≥ 0.341. The test does not separate the result from noise.
3. With leave-one-out weights, ΔSharpe = **−0.78**.
4. Scores take only 3–9 distinct values, so the tercile cut falls inside tied groups, and leg membership follows manifest row order. Random tie order gives a median of 0.28 (90% range −0.62 to +1.15); reversed row order gives 0.21.
5. "0.066 → 0.341" compares different samples. On the 70-event sample that produced 0.066 (additive), the regression-fitted ΔSharpe was −0.028. On the 80-event sample, the additive ΔSharpe is +0.427. The pass came from 10 added events, not from the change of method.

The pivotal-only 1.088 is the same pooled t-statistic (per event 0.15; tie-order 90% range −0.77 to +2.12). It is not evidence of a standalone signal.

**Consequence.** Trigger #2 is not passed. The only other pass route, partial-α t ≥ 2.0, also fails (t = 0.958). Under the pre-registered rule (CLAUDE.md, Phase 1 #2) the project closes as a writeup-only freeze: a negative incremental result.

**How it was found.** A multi-model code review on 2026-10-10 flagged the routine, and an independent recomputation on 2026-10-11 confirmed it. The project's own audit gates did not catch it.

Self-correction #1 (2026-05-17, row-aggregation dedup: Welch t 4.37 → 1.69, negative arm n = 21 → 4) is documented in the paper, but this README had not been updated for it. The table below now reflects both corrections. Original values: Welch t 4.371 ✅, ΔSharpe 0.341 ✅, minority class 21 ✅ LOCK-SAFE, abandon triggers fired 0, negative-arm CAR −7.65% (n = 21) vs positive +0.14% (n = 96), spread +7.79%.

Paper: `analysis/paper_v2_en.md`, section "Erratum / Post-Publication Self-Correction #2". The PDF is regenerated in the same commit.

## Headline metrics (corrected 2026-10-11)

| Trigger | Threshold | Final value | Verdict |
|---|---|---:|---|
| #4 Cross-LLM 2/3 majority | ≥ 80% | **99.29%** | ✅ |
| #3 CAR T+30 Welch t (Bonferroni-18) | ≥ 2.99 | **1.69** (unique amendments, n = 16 vs 4) | ❌ (self-correction #1) |
| #2 Δ Sharpe (regression-fitted) | ≥ 0.30 | not passed (in-sample 0.341 is a pooled t difference; permutation p ≈ 0.68; leave-one-out −0.78) | ❌ (self-correction #2) |
| F1-1 minority class lock | ≥ 20 | **4** | ❌ |
| Cumulative spend | ≤ $30 | **$0.47** | ✅ (1.6%) |
| Abandon trigger fired | 0 | **#2** (writeup-only freeze) | ❌ |

**Cross-section CAR**: negative pivotal-shift amendments show **−7.34%** mean T+30 CAR vs SPY (n = 4 unique amendments), versus positive **+0.14%** (n = 16). Spread +7.48%, Welch t = 1.69: not significant.

**Paper draft**: [analysis/F6_paper_draft.md](analysis/F6_paper_draft.md) (8-12pp, SSRN-ready).
**Dashboard**: `streamlit run src/clinicaltrials_amendment_llm/dashboard.py` (5-page MVP).

---

## Hypothesis

amendment 의 pivotal-shift type (positive: dose escalation / scope expansion / accelerated timeline; negative: endpoint shrink / sample size 축소 / population narrowing) 이 시험 진행의 *leading indicator*. positive amendment biotech long, negative short → cross-section forward CAR alpha.

**Contribution**: CTP-LLM (arxiv 2408.10995) 의 *financial extension* — phase-transition prediction 학술 한정 → equity alpha cross-section.

**CTP-LLM 흡수 risk (Phase 1 trigger #2)**: incremental Sharpe Δ ≥ 0.3 미달 시 → writeup-only freeze (full kill 아님 — negative incremental publishable).

---

## Phase 0 — Week 1 (Day 1-7)

| Day | Deliverable | Gate |
|---|---|---|
| 1 | repo init + manifest skeleton + CT.gov v2 client + CTP-LLM read + scoop check + OpenRouter register | repo bootable, daemon-free verified |
| 2 | biotech R1000 universe filter + amendment fetch first | universe ≥ 200 firms |
| 3 | PDF parser dry-run + 3-axis prompt + sponsor mapping skeleton | PDF parser yield ≥ 90% (n=20) |
| 4 | n=10 dry-run + n=20 oracle start | dry-run ≥ 5/10 |
| 5 | n=10 complete + PDF yield 1차 + oracle complete | trigger #1 (fetched ≥ 3000), trigger #2 (≥ 7/10) |
| 6 | n=10 second + 3-vendor κ measure + PDF yield 2차 | trigger #3 (κ ≥ 0.6) |
| 7 | **Phase 0 EOD single kill gate** — 6 metric AND | GO/KILL |

**Day 7 EOD 6-metric AND**: fetched ≥ 3,000 + n=10 dry-run pass ≥ 7/10 + 3-vendor Fleiss κ ≥ 0.6 + Phase 0 spend ≤ $8 + scoop 미발견 + **PDF parsing yield ≥ 80% (F6 special)**.

## Phase 1 — Week 2-3 (Day 8-21)

Day 8-12 full sample LLM inference + sponsor → ticker mapping + phase-transition outcome join. Day 13 CTP-LLM baseline replication. Day 14 mid-checkpoint. Day 15-16 cross-section forward CAR + vaccine-cohort stratum (F1-4 lesson). **Day 17-18 CTP-LLM incremental Sharpe Δ measurement (핵심 gate)**. Day 19 rigor pass. Day 20 writeup + dashboard. Day 21 hard cap.

---

## Resume

```bash
python -m clinicaltrials_amendment_llm.resume
```

Reads `data/manifest_global.json` and prints current phase + next undone task. Used at the start of every Claude session for re-anchoring (drift-watchdog Rule 25).

---

## Layout

```
src/clinicaltrials_amendment_llm/
  manifest.py           # atomic manifests + task sequence
  resume.py             # CLI entry point
  ctgov_client.py       # ClinicalTrials.gov v2 API (daemon-free guard)
  pdf_parser.py         # pdfplumber → pypdf fallback chain (F6 trigger #6)
analysis/
  ctp_llm_baseline_spec.md   # Day 1 deliverable
audits/
  scoop_check_2026-04-27.md  # Phase 0 trigger #5 weekly
data/
  manifest_*.json{l}    # resumable state
checkpoints/
  YYYY-MM-DD.md         # daily progress (08:00 / 20:00 KST)
```

---

## Statistical Rigor

- IS 2010-2020 / OOS 2021-2026 (frozen).
- FDR 보정 (3-axis × 3-horizon × phase = ~12 검정).
- Deflated Sharpe Ratio.
- Bootstrap CI B=1000, cluster by sponsor.
- Newey-West HAC.
- FF5 + momentum 직교화.
- Vaccine cohort stratum (2020-2022 COVID/RSV/influenza 별도, F1-4 lesson).
- **CTP-LLM incremental Sharpe ≥ 0.3 verify (Phase 1 trigger #2 의무)**.
- Contamination audit: LLM cutoff vs amendment date + drug-name + sponsor-name masking.

---

## Close paths (Layer A/B/C/D — F1-6 lesson)

- **Layer A (academic success)** → SSRN paper draft + GitHub
- **Layer B (production-grade)** → deployment audit + Streamlit
- **Layer C (frozen-as-is mechanical kill)** → ABANDONED.md + postmortem
- **Layer D (CTP-LLM 흡수, Phase 1 #2 incremental Sharpe Δ < 0.3)** → writeup-only freeze, paper publishable as negative incremental

---

## References

- arxiv 2408.10995 (CTP-LLM, Aug 2024) — primary anchor
- FDAAA 2007 §801 + 2017 Final Rule — ClinicalTrials.gov mandate
- DiMasi-Grabowski 2003 / 2016 (J Health Econ)
- Tufts CSDD / Citeline / FDA approval calendar — outcome cross-reference
- F1 frozen postmortem (`d:/vscode/meta-harness/audits/2026-04-27-fda-adcomm-frozen-postmortem.md`) — F1-1~F1-6 lessons applied
