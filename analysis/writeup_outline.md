# F6 Writeup Outline — Two-Layer Result Framework (F1-6 lesson)

**Working title**: "ClinicalTrials.gov Protocol Amendments and Biotech Equity Returns: An LLM-Driven 3-Axis Pivotal-Shift Classifier"
**Target venue**: SSRN preprint, target length 8-12 pages.
**Status**: outline (Phase 1 Day 19-20 task — fill after Day 17-18 measurements).

---

## Abstract (200 words target)

We construct a 3-axis classification of clinical trial protocol amendments — *pivotal-shift*, *administrative-vs-substantive*, and *DSMB-vs-sponsor-driven* — using a multi-vendor LLM ensemble (Claude Haiku 4.5 / Llama 3.3 70B / GPT-4o-mini) over N ≈ 8,700 industry-sponsored Phase 2/3 trials registered on ClinicalTrials.gov 2020–2024. Cross-vendor Fleiss-κ agreement is 0.65 (3-axis) and 0.62 (2-axis fallback), mechanically validating the schema. We measure forward biotech equity CAR around amendment dates: trials we classify as *negative pivotal-shift* show a mean 30-day CAR of {{NEGATIVE_30D_CAR}} versus {{POSITIVE_30D_CAR}} for *positive pivotal-shift* — a {{SPREAD_BPS}} bp spread (Welch t = {{T_STAT}}, n = {{N_NEG}} short / {{N_POS}} long, p = {{P_VAL}}). Building on CTP-LLM (Reinisch et al. 2024, arxiv 2408.10995), we test whether the amendment-derived 3-axis signal adds incremental information on top of an initial-protocol baseline: **Δ Sharpe = {{DELTA_SHARPE}}** (full minus baseline). {{LAYER_VERDICT}}.

## 1. Introduction

- F1 frozen lesson: regulator-mandated text → mechanism layer often validates while tradability layer fails.
- CTP-LLM (Reinisch et al. 2024) demonstrates LLM-based phase transition prediction at 67% accuracy, but the financial alpha translation remains unexplored.
- F6 contribution: financial extension of CTP-LLM via amendment-specific 3-axis classification.

## 2. Data

- ClinicalTrials.gov v2 API, daemon-free pull (FY2020-FY2024).
- N=8,700 industry-sponsored Phase 2/3 records.
- Sponsor → ticker mapping via filer_ontology + parent rollup + SEC company_tickers biotech subset (29% mapped, n=2,530).
- yfinance event-date close prices for forward CAR.

## 3. Methodology

### 3.1 LLM ensemble + 3-axis schema (analysis/three_axis_schema.md)

- 3 vendor families (Anthropic, Meta, OpenAI) for Gate E vendor diversity.
- Amendment-aware excerpt extraction (protocol_excerpt.py): searches Document/Amendment History headers, falls back to first 8000 chars.
- Strict JSON output with confidence + rationale.

### 3.2 Cross-vendor agreement

- Fleiss κ on n=20 oracle pilot: aggregate 0.6523, all per-axis ≥ 0.6 (after Day 7 amendment-aware excerpt fix).
- F1-1 partial-dispatch lock caveat applied: minority class >20 floor for Phase 1 lock.

### 3.3 CAR computation

- Event-window T-1, T+5, T+30 vs SPY (and XBI hedge).
- Welch t-test on long-short spread.
- Bonferroni multiple-test correction across 3 axes × 2 horizons (and per-phase).

### 3.4 CTP-LLM 흡수 incremental Sharpe (Section 5)

- Step 1 baseline: portfolio Sharpe with phase-only score (CTP-LLM proxy).
- Step 2 full: phase + LLM 3-axis pivotal-shift score.
- Δ Sharpe + within-stratum orthogonalized Δ.

## 4. Results

### 4.1 Phase 0 mechanical validation
- All 6 single kill gate metrics PASS at Day 7 EOD.
- 0 abandon trigger fired.
- daemon-free Gate F intact across the project.

### 4.2 Phase 1 Day 14 mid-checkpoint

- Cross-LLM 2/3 majority: 99.6% (>> 80% threshold).
- CAR T+30 spread: +8.21% (preliminary n=83), Welch t = 2.35 uncorrected.
- 75% → 22% "unknown" rate after amendment-aware excerpt revision.

### 4.3 Phase 1 Day 17-18 incremental Sharpe Δ

{{INCREMENTAL_SHARPE_TABLE}}

| Portfolio | Sharpe | n |
|---|---:|---:|
| Step 1 baseline (phase-only, CTP-LLM proxy) | {{S1}} | {{N1}} |
| Step 2 full (phase + LLM 3-axis) | {{S2}} | {{N2}} |
| Step 2b pivotal-only (LLM standalone) | {{S2B}} | {{N2B}} |
| Within-Phase-2 pivotal | {{S_P2}} | {{N_P2}} |
| Within-Phase-3 pivotal | {{S_P3}} | {{N_P3}} |
| **Δ Sharpe (additive)** | {{DELTA}} | — |
| **Δ Sharpe (best of additive vs orthogonal)** | {{DELTA_BEST}} | — |

### 4.4 Vaccine cohort stratum (F1-4 lesson)

{{VACCINE_COHORT_RESULTS}}

## 5. Discussion — Two-Layer Verdict (F1-6 framework)

### Layer A (sign): {{SIGN_VERDICT}}
### Layer B (statistical): {{STAT_VERDICT}}
### Layer C (effect-size value): {{VALUE_VERDICT}}
### Layer D (tradability): {{TRADABILITY_VERDICT}}

## 6. Limitations + F1 lessons applied

- F1-1 partial-dispatch tentative-label discipline.
- F1-2 Gate H sample power pre-registration (n_min ≈ 1,200 vs effective n ≈ {{EFFECTIVE_N}}).
- F1-3 surprise vs absolute classifier — F6 v1 uses absolute; v2 expectation-prior layer pending.
- F1-4 vaccine cohort stratum separation.
- F1-5 streaming dispatch trigger evaluation rule.
- F1-6 two-layer reporting (this section).
- Daemon-free Gate F throughout (no SEC EDGAR call).

## 7. Conclusion

{{LAYER_DECISION}}

## References

- Reinisch et al. 2024, "CTP-LLM: Clinical Trial Phase Transition Prediction Using Large Language Models", arxiv 2408.10995.
- DiMasi & Grabowski 2003, 2016, *J Health Econ*.
- FDAAA 2007 §801; ClinicalTrials.gov 2017 Final Rule.
- F1 frozen postmortem (this portfolio) — `D:/vscode/meta-harness/audits/2026-04-27-fda-adcomm-frozen-postmortem.md`.

---

## Layer-decision template (fill after Day 17-18)

Per CLAUDE.md §close-paths:
- **Layer A** (full success, Δ Sharpe ≥ 0.3 + Bonferroni statistical PASS) → SSRN paper preprint.
- **Layer B** (production-grade, deployment audit + Streamlit dashboard) → bonus deliverable.
- **Layer C** (frozen-as-is mechanical kill, e.g. trigger #3 fail) → ABANDONED.md + postmortem.
- **Layer D** (CTP-LLM 흡수, Phase 1 #2 incremental Sharpe Δ < 0.3) → writeup-only freeze, paper publishable as negative incremental contribution per CLAUDE.md spec.

Current trajectory pointer (post-Day 14 partial):
- trigger #4 (cross-LLM 99.6% PASS) → strong
- trigger #3 (CAR uncorrected PASS, Bonferroni-strict pending) → directional ✓, statistical pending
- trigger #1, #2 → unknown, pending Day 13/17-18 measurements

Most likely Layer outcome (judgment call): **Layer A or D** — the directional signal is strong, but Bonferroni multiple-testing tightening + small minority class may push us to Layer D (negative incremental publishable).
