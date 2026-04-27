# RESUMABLE — F6 (clinicaltrials_amendment_llm)

**Last sync**: 2026-04-27 KST (Phase 1 Day 14 mid-checkpoint partial)
**Phase**: phase1
**Tasks done**: 30 / 38
**Current task**: `day13_ctp_llm_baseline_replication`
**Spend**: $0.41 / $30 cap (1.4%)

---

## 🎯 Phase 1 Day 14 mid-checkpoint PARTIAL PASS (n=100 strategic proof-of-concept)

| Metric | Threshold | Result | Verdict |
|---|---|---|---|
| **Trigger #4 cross-LLM 2/3 majority** | ≥ 80% | **99.6%** | ✅ PASS (margin 19.6pp) |
| **Trigger #3 CAR T+30 t-stat** | ≥ 2.0 (Bonferroni-18: ≥ 2.78) | **2.35** (uncorrected) | ✅ uncorrected PASS / ❌ Bonferroni-strict FAIL |
| Trigger #1 phase transition ROC-AUC | ≥ 0.65 | not measured | deferred to Day 13 |
| Trigger #2 CTP-LLM incremental Sharpe Δ | ≥ 0.3 | not measured | deferred to Day 17-18 |
| Trigger #7 effective n | ≥ 1,500 mapped | **2,530 mapped** | ✅ floor cleared |

**CAR signal directional PASS**:
| pivotal_shift | n | mean T+30 CAR vs SPY |
|---|---:|---:|
| **negative** | 6 | **-8.07%** |
| neutral | 30 | -0.82% |
| positive | 32 | +0.14% |
| unknown | 70 | -3.22% |
spread (pos−neg): **+8.21%**, welch_t **2.35**.

**F1-1 partial-dispatch caveat directly applied**: minority cohort (negative) n=6 < 20 floor → result is **tentative**, not locked. Full dispatch n=1,500 strategic sample (next turn) will scale minority class to ~30+, satisfy F1-1 + Bonferroni-18.

---

## What completed across this session (Day 8-14 partial)

### Day 8: 5y fetch expansion FY2020-FY2024
- 8,700 records (vs 3,500 at Day 5 close)
- 100% industry-sponsored Phase 2/3

### Day 11: sponsor → ticker expansion
- BIOTECH_R1000_SEED: 89 firms (+ partial-match)
- PARENT_ROLLUP: 20 entries (Janssen→JNJ, Genentech→ROG.SW, etc.)
- SEC company_tickers.json biotech subset: 562 firms
- **2,530 / 8,700 = 29% mapped (Phase 1 trigger #7 floor cleared)**

### Day 8-10: strategic n=100 dispatch (proof-of-concept)
- Stratified by (year × sponsor_size × phase)
- async parallelism (ThreadPoolExecutor 3-vendor) + parallel PDF download (curl_cffi)
- 164 LLM calls, $0.23 cost, ~10 min wall-clock
- "unknown" rate dropped 75% (Day 6) → **22%** (Day 14) thanks to amendment-aware excerpt

### Day 14: mid-checkpoint partial (3-metric)
- **Trigger #4**: 99.6% cross-LLM majority (PASS)
- **Trigger #3**: CAR T+30 t=2.35 / spread +8.21% (TENTATIVE PASS, Bonferroni-strict pending full sample)
- Trigger #1, #2: deferred (Day 12-13 + Day 17-18 work)

---

## What is BUILT but NOT YET RUN

### `phase_transition_labels.py` (Day 12-13 prerequisite)
- Logic: cluster CT.gov records by (sponsor_norm, drug_norm), find phase X → X+1 transitions within 60-month window, label `transitioned: bool` per Phase X trial
- Daemon-free (no Citeline / CSDD)
- **Run**: `python -m clinicaltrials_amendment_llm.phase_transition_labels`
- Note: requires fetching intervention names for ~8,700 NCTs (concurrent CT.gov v2 calls, ~20 min wall-clock)

### `cross_section_car.py` (full Phase 1 trigger #3 measurement)
- Logic: for each (NCT, ticker, event_date) with LLM labels → CAR vs SPY at T-1/T+5/T+30
- Already run at Day 14 partial (n=83 events). Re-run after full dispatch.

### `cross_llm_analyzer.py` (Phase 1 trigger #4)
- Pairwise + 2/3 majority + unanimous rates per axis
- Already run at Day 14 partial.

### `day14_midcheckpoint.py` (composite)
- Combines cross-LLM + axis distribution + CAR effect size
- Already run at Day 14 partial.

---

## Next-turn entry (when user types "계속" or "Day 13 시작")

### Priority 1 (most critical): Full Phase 1 dispatch (n=1500 stratified)
- Reuse `day8_dispatch_async.py --n 1500`
- Expected: 1,500 NCTs × 3 vendors = 4,500 calls × $0.003 = $13.50 (within $22 Phase 1 cap)
- Wall-clock: ~30-40 min with parallelism
- Closes F1-1 minority floor + provides Bonferroni-18 statistical power

### Priority 2: Day 12-13 phase transition labels
- `python -m clinicaltrials_amendment_llm.phase_transition_labels`
- Output: `manifest_phase_transition.jsonl` with binary `transitioned` per (NCT, target_phase)
- Enables Phase 1 trigger #1 (ROC-AUC ≥ 0.65)

### Priority 3: Day 13 CTP-LLM baseline replication (F6 핵심 prerequisite)
- arxiv 2408.10995 reproduction on our slice
- 3-vendor LLM scores phase transition probability from initial protocol text
- Compare predicted vs `transitioned` label → ROC-AUC measurement

### Priority 4: Day 15-16 vaccine cohort stratum (F1-4 lesson)
- Identify 2020-2022 COVID/RSV/influenza vaccine trials in dispatched sample
- Separate strata reporting on CAR

### Priority 5 (핵심 결정 gate): Day 17-18 CTP-LLM incremental Sharpe Δ
- Step 1 baseline: monthly cross-section Sharpe with CTP-LLM phase-transition feature only
- Step 2 full: CTP-LLM + LLM 3-axis pivotal-shift features
- Δ Sharpe ≥ 0.3 → PASS / < 0.3 → writeup-only freeze (negative incremental publishable)

### Priority 6: Day 19 rigor pass + Day 20 writeup + dashboard + Day 21 hard cap

---

## State files

| File | Status |
|---|---|
| `data/manifest_global.json` | phase=phase1, 30/38 done, current=day13_ctp_llm_baseline_replication |
| `data/manifest_amendment_fetch.jsonl` | 8,700 records (Day 8 5y) |
| `data/manifest_pdf_parse_audit.jsonl` | 40 records (2 samples, 100% yield) |
| `data/manifest_axis_classify.jsonl` | 307 records (60 Day 6 + 60 Day 7 oracle + 23 Day 7 dry-run + 164 Day 8 dispatch) |
| `data/manifest_oracle_kappa.json` | latest (n=26+ depending on includes) |
| `data/manifest_sponsor_map.jsonl` | 2,530 mapped records (Day 11 expansion) |
| `data/manifest_car.jsonl` | 71+ events with CAR computed |
| `data/cache/pdf/*.pdf` | ~245 cached protocol PDFs |
| `analysis/day14_midcheckpoint.json` | Day 14 partial mid-checkpoint output |
| `audits/self_audit_day{1,2,3,6,7,14}_*.md` | per-day self-audit |
| 14 modules | manifest, resume, ctgov_client, pdf_parser, biotech_universe, day2_fetch, day3_pdf_dryrun, day5_fetch_expand, day5_pdf_dryrun2, oracle_pilot, protocol_excerpt, day7_n10_dryrun, day8_fetch_expand_5y, sponsor_mapper, day8_dispatch, day8_dispatch_async, cross_section_car, cross_llm_analyzer, phase_transition_labels, day14_midcheckpoint |

---

## Spend

- Phase 0: **$0.17 / $8 cap** (2.07%)
- Phase 1 partial: **$0.25** ($0.41 total / $30 cap = 1.4%)
- Phase 1 full dispatch budget remaining: ~$21.6
- Day 13+ CTP-LLM replication budget: enough room

---

## Done (commits)

```
$ git log --oneline (7 expected after Day 14 commit)
<commit7> Day 8-14 partial: Phase 1 entry + 5y fetch + sponsor expansion + n=100 dispatch + Day 14 mid-checkpoint partial PASS
529c58e Day 7: Phase 0 EOD single kill gate 6/6 PASS
47a9a6b Day 5+6: trigger #1/#6 PASS + #3 TENTATIVE PASS
552c15a Day 4 partial: 3-axis schema + LLM prompt template
27c5a47 Day 3: PDF parser dry-run trigger #6 PASS
8bc3dc3 Day 2: CT.gov 403 resolved via curl_cffi
b6a07d7 Day 1: F6 Phase 0 launch
```
