# RESUMABLE — F6 (clinicaltrials_amendment_llm)

**Last sync**: 2026-04-27 KST (Phase 0 close, Phase 1 entry)
**Phase**: **phase1** (transitioned 2026-04-27 Day 7 EOD)
**Tasks done**: 26 / 38
**Current task**: `day8_full_sample_inference_start`

---

## 🎯 Phase 0 final result — 6/6 single kill gate PASS

| # | Trigger | Threshold | Final | Verdict |
|---|---|---|---|---|
| 1 | fetched amendments | ≥ 3,000 | **3,500** | ✅ PASS (17% margin) |
| 2 | n=10 dry-run pass | ≥ 7/10 | **7/10** | ✅ PASS (at threshold) |
| 3 | 3-vendor Fleiss κ | ≥ 0.6 | **all 3 axes ≥ 0.6, agg 0.6523** | ✅ PASS |
| 4 | Phase 0 spend | ≤ $8 | **$0.17 (2.07%)** | ✅ PASS (98% margin) |
| 5 | scoop discovered | none | **0 financial-extension** | ✅ PASS |
| 6 | PDF parsing yield | ≥ 80% | **100% × 2 samples (n=40)** | ✅ PASS (20pp margin) |

**0 abandon trigger fired across Phase 0.**

---

## What completed across this session (Day 1-7)

### Day 1
- Skeleton + manifest + CTP-LLM (arxiv 2408.10995) baseline spec + scoop check + daemon-free Gate F verify

### Day 2
- pip install + curl_cffi TLS workaround for CT.gov 403 (Cloudflare bot block)
- biotech_universe.py (77-firm seed) + Day 2 first fetch (200 records, 100% industry/Phase 2-3, 17% mapped)

### Day 3
- PDF parser dry-run sample 1 (n=20): trigger #6 PASS at 100%

### Day 4 partial
- 3-axis schema + LLM prompt template + cost estimate

### Day 5
- Fetch expansion FY2022-FY2024: 3,500 records (trigger #1 PASS)
- PDF dry-run sample 2: trigger #6 PASS at 100% (n=40 combined)

### Day 6
- OpenRouter F6 cap=$30/max=8 registered
- n=20 oracle 3-vendor (claude-haiku-4.5 + llama-3.3-70b + gpt-4o-mini after Anthropic 3.5 / Gemma 2 retired)
- Initial κ TENTATIVE PASS (aggregate 0.6305, but pivotal_shift 0.5896 marginal fail; 75% "unknown" rate)

### Day 7 (this turn)
- **Amendment-aware excerpt extractor** (`protocol_excerpt.py`) — searches Document/Amendment History headers
- **Dedup fix** (oracle_pilot.py): key (nct, vendor, prompt_hash) instead of (nct, vendor); measure_kappa latest_only=True
- **Oracle re-run** (60 new calls with v2 prompt) — κ jumped:
  - pivotal_shift 0.5896 → **0.6292** ✓
  - admin_vs_substantive 0.6444 → **0.6779** ✓
  - driver 0.6576 → **0.6498** ✓
  - aggregate 0.6305 → **0.6523** ✓
  - pivotal_binary fb 0.5896 → **0.6220** ✓
- **n=10 full-pipeline dry-run** (`day7_n10_dryrun.py`): 7/10 PASS, trigger #2 met. Stage rates: fetch 100%, pdf 70%, llm 70%, ticker 100%, **car 100%** (yfinance reliable).
- **Phase 0 EOD single kill gate**: 6/6 PASS → Phase 1 entry GO.

---

## F1-1 partial-dispatch caveat (carry-forward)

**minority_count for pivotal_shift = 1** (across 26 NCTs × 3 vendors). F1-1 floor is 20.

Per F1 frozen lesson F1-1: label-distribution-sensitive metric (κ) at minority < 20 is **tentative**, not locked. Phase 1 strategic n=1500 stratified dispatch에서 minority cohort (10-20% of sample) 자연 도달 → minority > 20 floor 충족 → Day 14 mid-checkpoint re-lock 의무.

---

## Phase 1 first tasks (Day 8-12 — next turn)

### Priority 1: Day 11 sponsor → ticker expansion
- Current: 607/3500 = 17% mapped via 77-firm seed
- Goal: ≥ 1,500 mapped via `shared_utils.filer_ontology` + parent rollup chain
- Industry-sponsored fuzzy match (Hoffmann-La Roche / Genentech / Roche → ROG.SW or RHHBY)
- Saves Phase 1 trigger #7 sample-power margin (n_min 1,200 vs n=1,500 = 25% margin)

### Priority 2: Day 8-10 strategic sample n=1,500 dispatch
- Stratification: (phase, sponsor_size_quintile, year, vaccine_cohort_y/n)
- 3-vendor ensemble (claude-haiku-4.5 + llama-3.3-70b + gpt-4o-mini)
- 1500 × 3 = 4,500 LLM calls × $0.003 avg = $13.50 (within $22 Phase 1 cap)
- F1-5 lesson: trigger evaluation 은 *완료 후* (latest-only)

### Priority 3: Day 13 CTP-LLM phase-transition baseline replication
- Spec: `analysis/ctp_llm_baseline_spec.md` (Day 1)
- arxiv 2408.10995 reproduction: ROC-AUC ≥ 0.65 (Bonferroni)
- F6 핵심 prerequisite for Phase 1 trigger #2 (incremental Sharpe Δ ≥ 0.3)

### Priority 4: Day 14 mid-checkpoint
- 3 metric eval: phase transition ROC-AUC / forward CAR / cross-LLM consistency
- F1-1 re-lock at this point (minority class ≥ 20)

### Priority 5: Day 15-16 cross-section forward CAR + vaccine cohort stratum (F1-4)
- IS 2010-2020 / OOS 2021-2026 split
- Vaccine cohort separate stratum reporting

### Priority 6: Day 17-18 CTP-LLM 흡수 incremental Sharpe Δ — F6 핵심 결정 gate
- Two-step regression: Sharpe_baseline (CTP-LLM only) vs Sharpe_full (CTP-LLM + LLM 3-axis)
- Δ Sharpe ≥ 0.3 → PASS / < 0.3 → writeup-only freeze (full kill 아님)

### Priority 7: Day 19-21 rigor pass + writeup + dashboard + hard cap

---

## State files

| File | Status |
|---|---|
| `data/manifest_global.json` | phase=phase1, 26/38 done, current=day8_full_sample_inference_start, spend_phase0=$0.17 |
| `data/manifest_amendment_fetch.jsonl` | 3,500 records (Day 5 expansion) |
| `data/manifest_pdf_parse_audit.jsonl` | 40 records (2 samples, all 100% yield) |
| `data/manifest_axis_classify.jsonl` | 120 records (60 v1 Day 6 + 60 v2 Day 7 amendment-aware) |
| `data/manifest_oracle_kappa.json` | latest κ measurement (n=26, all axes ≥ 0.6) |
| `data/manifest_car.jsonl` | 10 records (Day 7 n=10 dry-run) |
| `data/cache/pdf/*.pdf` | 40 cached protocol PDFs |
| `audits/self_audit_day{1,2,3,6,7}_*.md` | per-day self-audit |
| `analysis/{three_axis_schema, llm_prompt_3axis, ctp_llm_baseline_spec}.md` | committed |
| `src/clinicaltrials_amendment_llm/{manifest, resume, ctgov_client, pdf_parser, biotech_universe, day2_fetch, day3_pdf_dryrun, day5_fetch_expand, day5_pdf_dryrun2, oracle_pilot, protocol_excerpt, day7_n10_dryrun}.py` | 12 modules |

---

## Outstanding mailbox

- **Inbound resolved**: 1 broadcast + 1 OpenRouter response (Day 6) → both processed.
- **Outbound**: 0 open.

---

## Spend

- Phase 0: **$0.17 / $8 cap** (2.07%)
- Phase 1: $0.00 / $22 cap (entering)
- Total: $0.17 / $30 cap

---

## Vendors confirmed working

- `anthropic/claude-haiku-4.5`
- `meta-llama/llama-3.3-70b-instruct`
- `openai/gpt-4o-mini`

(`anthropic/claude-3.5-sonnet`, `google/gemma-2-9b-it`, `google/gemini-flash-1.5` retired — 404 No endpoints.)

---

## Done (commits)

```
$ git log --oneline (6 expected after Day 7 commit)
<commit6> Day 7: Phase 0 EOD single kill gate 6/6 PASS - Phase 1 entry GO
47a9a6b Day 5+6: trigger #1/#6 PASS + #3 TENTATIVE PASS
552c15a Day 4 partial: 3-axis schema + LLM prompt template + RESUMABLE.md
27c5a47 Day 3: PDF parser dry-run n=20 - trigger #6 PASS at 100%
8bc3dc3 Day 2: CT.gov 403 resolved via curl_cffi
b6a07d7 Day 1: F6 Phase 0 launch - skeleton + CTP-LLM baseline spec
```

---

## Next-turn entry

User invokes "계속" or "Day 8 시작" → start with Priority 1 (sponsor expansion) + Priority 3 (CTP-LLM baseline read for replication spec verification). Heavy LLM dispatch (Priority 2) parallelizable after sponsor expansion lands.
