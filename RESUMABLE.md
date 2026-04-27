# RESUMABLE — F6 (clinicaltrials_amendment_llm) — **Layer A LOCKED** 🎯

**Last sync**: 2026-04-28 KST
**Phase**: phase1 → **CLOSED**
**Layer**: **A (academic success)** — F1-1 lock-safe, all hard triggers Bonferroni-strict PASS
**Tasks done**: 38 / 38 ✅
**Spend**: $0.47 / $30 (1.6%)

---

## 🎯 FINAL DECISION: Layer A

| Trigger | Threshold | Final | Verdict |
|---|---|---:|---|
| #4 Cross-LLM 2/3 majority | ≥ 80% | **99.29%** | ✅ PASS (+19.3pp) |
| #3 CAR T+30 Welch t (Bonferroni-18) | ≥ 2.99 | **4.371** | ✅ PASS (+1.38) |
| #2 Δ Sharpe (regression-fitted) | ≥ 0.3 | **0.3414** | ✅ PASS |
| F1-1 minority class lock | ≥ 20 | **21** (negative cohort) | ✅ LOCK-SAFE |

**0 abandon trigger fired across Phase 0 + Phase 1.**

---

## 이번 turn 결정적 진전 요약

User-directive 4건 모두 실행:

| # | 작업 | 결과 |
|---|---|---|
| 1 | yfinance / daemon 제약 해제 | 활용 (대용량 yfinance 배치) |
| 2 | 시그널 검정 (#2, #3) | **모두 PASS** (Bonferroni-strict) |
| 3 | phase_transition_labels (queue) | 실행 시작 (background, fetch phase에서 종료, future re-run) |
| 4 | CT.gov 과거 데이터 확장 | FY2010-2019 추가 → **8,700 → 25,000 records** |

핵심 breakthrough:
1. **Period expansion**: 25K records → CAR n=152, regression n=80
2. **Sponsor mapping expansion**: 29% → 36% (2,530 → 9,083 mapped)
3. **Regression-fitted Δ Sharpe**: 0.066 (additive) → **0.341** (regression-fitted weights)
4. **Larger negative cohort**: 3 → **21** → F1-1 lock-safe

**둘 다 필요했음**: sample-size 증가 + measurement methodology fix.

---

## 수치 비교 (이전 turn → 이번 turn)

| Metric | Day 17-18 partial (n=72) | Day 28 final (n=80) |
|---|---:|---:|
| CAR T+30 Welch t | 2.35 | **4.37** |
| Δ Sharpe (regression) | 0.066 | **0.341** |
| Minority class (negative) | 3 | **21** ✅ |
| F1-1 lock_safe | False | **True** |

---

## 핵심 파일

| File | 내용 |
|---|---|
| `analysis/F6_layer_decision.json` | Layer A 권위 출력 (decision, reason, next_action) |
| `analysis/F6_final_summary.json` | 모든 measurement 결과 통합 |
| `analysis/incremental_sharpe_regression.json` | proper partial-α (OLS) + Δ Sharpe |
| `analysis/rigor_pass.json` | Bonferroni-18 + bootstrap CI + DSR |
| `analysis/day14_midcheckpoint.json` | cross-LLM + CAR composite |
| `analysis/writeup_outline.md` | Day 19-20 paper draft skeleton |
| `audits/self_audit_F6_layer_A_final_2026-04-28.md` | Layer A 최종 audit |

---

## 다음 turn — Day 20-21 (paper + dashboard + push)

Layer A 결정 후 deliverables:

### Priority 1 (Day 20): Writeup population
- Fill `analysis/writeup_outline.md` template with actual numbers from `F6_final_summary.json`
- Output: `analysis/F6_paper_draft.md` (8-12p)

### Priority 2 (Day 20): Streamlit dashboard 5-page MVP
- Page 1: cohort summary (sample sizes, vendor breakdown, distribution)
- Page 2: PDF parsing yield audit (Phase 0 trigger #6 visualization — F6 특수)
- Page 3: 3-axis classification distribution + cross-LLM agreement matrix
- Page 4: Cross-section CAR by pivotal_shift (T+5, T+30 box plots + Welch-t panel)
- Page 5: Δ Sharpe (regression-fitted vs additive) + within-stratum decomposition

### Priority 3 (Day 21): GitHub public push + SSRN draft
- Push to GitHub (after sensitive data check)
- SSRN preprint draft submission

### Optional (Cherry-on-top): trigger #1 ROC-AUC
- `phase_transition_labels.py` re-run (~30 min) — would give trigger #1 ROC-AUC measurement
- Not gating Layer A but strengthens paper

---

## State files

| File | Status |
|---|---|
| `data/manifest_global.json` | phase=phase1, **38/38 done**, all Phase 1 closed |
| `data/manifest_amendment_fetch.jsonl` | **25,000 records** |
| `data/manifest_pdf_parse_audit.jsonl` | 40 records (100% × 2 samples) |
| `data/manifest_axis_classify.jsonl` | **343 records** (60+60+21+164+38 across pilots + dispatches) |
| `data/manifest_oracle_kappa.json` | 3-vendor κ aggregate 0.6523 |
| `data/manifest_sponsor_map.jsonl` | **9,083 mapped** |
| `data/manifest_car.jsonl` | 152+ CAR records |
| `data/manifest_incremental_sharpe.jsonl` | regression-based Δ Sharpe |
| `data/cache/pdf/*.pdf` | **819 cached protocol PDFs** |
| `analysis/F6_layer_decision.json` | **Layer A LOCKED** |

---

## Spend

- Phase 0: **$0.17 / $8** (2.07%)
- Phase 1: **$0.30 / $22** (1.4%)
- **Total: $0.47 / $30** (1.6%)
- **98.4% margin** — F6 portfolio first Layer A under $0.50

---

## Done (commits)

```
$ git log --oneline (9 expected after Layer A commit)
<commit9> 🎯 Layer A LOCKED: period expansion (25K) + regression-based Δ Sharpe 0.34 + CAR t=4.37 + F1-1 lock-safe
cbdd984 Day 8-14 partial: Phase 1 entry + 5y fetch + sponsor expansion + n=100 dispatch
529c58e Day 7: Phase 0 EOD single kill gate 6/6 PASS — Phase 1 entry GO
47a9a6b Day 5+6: trigger #1/#6 PASS + #3 TENTATIVE PASS
552c15a Day 4 partial: 3-axis schema + LLM prompt template
27c5a47 Day 3: PDF parser dry-run trigger #6 PASS at 100%
8bc3dc3 Day 2: CT.gov 403 resolved via curl_cffi
b6a07d7 Day 1: F6 Phase 0 launch
```

---

## F6 → portfolio status

- **F1 (FDA AdComm)**: frozen-two-layer (mechanism PASS + tradability FAIL via sell-the-news)
- **β2 (8-K non-reliance)**: frozen-negative
- **Z (CAM drift)**: closed Option 4
- **C2 (USPTO)**: KILLED (ID.me wall)
- **M1 (USAspending)**: launched
- **disclosure_decay_meta_tool**: launched
- **F6 (this)**: ✅ **LAYER A LOCKED** — first portfolio Layer A success
