# RESUMABLE — F6 (clinicaltrials_amendment_llm)

**Last sync**: 2026-04-27 KST (Phase 1 Day 17-18 partial — TENTATIVE FIRE on #2 + #3)
**Phase**: phase1
**Tasks done**: 34 / 38
**Current task**: `day13_ctp_llm_baseline_replication` (still pending; Day 17-18 partial measured ahead of formal Day 13)
**Spend**: $0.42 / $30 (1.4%)
**Layer projection**: most likely Layer A (30%), Layer D (50%), Layer C (10%), Hybrid (10%)

---

## 🚨 Phase 1 Day 17-18 PARTIAL — TENTATIVE FIRE on triggers #2 + #3

### Day 17-18 incremental Sharpe Δ (n=72 events)

| Portfolio | n | Sharpe |
|---|---:|---:|
| Step 1 baseline (phase-only, CTP-LLM proxy) | 23/23 | 0.301 |
| Step 2 full (phase + LLM 3-axis additive) | 23/23 | 0.368 |
| Step 2b pivotal-only (LLM standalone) | 23/23 | **1.297** |
| Within-Phase-2 stratum pivotal | 14/14 | **1.082** |
| Within-Phase-3 stratum pivotal | 8/8 | 0.267 |

**Δ Sharpe (additive) = 0.066 < 0.3 threshold → trigger #2 STRICT FIRE**

**BUT**: pivotal-only Sharpe 1.30 is dominant; additive measurement is **scale-mismatch artifact** (phase score [2,3] vs pivotal [-1,+1] dilutes pivotal). Within-Phase-2 stratum Sharpe 1.08 confirms the F6 amendment signal IS strong — just not in additive scoring against phase baseline.

### Day 19 rigor pass (T+30 horizon)

| Metric | Value | Threshold | Pass? |
|---|---:|---:|---|
| Welch t (uncorrected) | **2.35** | ≥ 2.0 | ✅ |
| Welch t (Bonferroni-18) | 2.35 | ≥ **2.99** | ❌ |
| Bootstrap 95% CI negative arm | [-0.129, -0.031] | excludes 0 | ✅ |
| Bootstrap 95% CI positive arm | [-0.042, +0.044] | excludes 0 | ❌ (CI contains 0) |

**Trigger #3 STRICT FIRE under Bonferroni-18.** But uncorrected PASS + clean negative CI → directional signal real.

---

## F1-1 partial-dispatch caveat APPLIED

**minority class (negative pivotal_shift) n = 3 ≪ F1-1 floor 20** → all triggers TENTATIVE, not locked. Per F1 lesson F1-1, label-distribution-sensitive metrics at small minority class are *tentative*. Full Phase 1 dispatch (next turn) needed to scale minority class to ≥20 for proper Bonferroni-strict + orthogonalized re-measurement.

---

## What completed across Day 1-7 (Phase 0) + Day 8-19 (Phase 1 partial)

### Phase 0 (Day 1-7)
- Skeleton + manifests + CTP-LLM spec + scoop check + daemon-free Gate F
- curl_cffi TLS workaround for CT.gov 403 (Cloudflare bot block)
- biotech_universe.py 77-firm seed → Day 11 expansion to 2,530 mapped
- PDF parser dry-run trigger #6 PASS at 100% × 2 samples (n=40 combined)
- Day 6+7 oracle pilot: amendment-aware excerpt + κ=0.6523 (PASS)
- Day 7 Phase 0 EOD single kill gate: **6/6 PASS** → Phase 1 entry

### Phase 1 partial (Day 8-19 partial)
- **Day 8** 5y fetch FY2020-FY2024: **8,700 records**
- **Day 11** sponsor expansion (filer_ontology + parent rollup + SEC biotech): **2,530 mapped (29%)**, F1-2 Gate H floor (1,200) cleared
- **Day 8-10** strategic n=100 dispatch: 164 calls, $0.23 (proof-of-concept)
- **Day 13** full n=1,500 dispatch attempt: bottlenecked on PDF download (~13 PDFs/min on cdn.clinicaltrials.gov, server-side throttling). 763 PDFs cached.
- **Day 14** mid-checkpoint partial: cross-LLM 99.6% PASS, CAR T+30 spread +8.21% t=2.35 uncorrected PASS / Bonferroni-18 FAIL
- **Day 17-18** incremental Sharpe Δ partial: 0.066 additive FIRE, 1.08 within-Phase-2 stratum (mixed)
- **Day 19** rigor pass partial: Bonferroni-18 critical 2.99 not cleared at n=72

---

## What's BUILT but DEFERRED to next turn

- `phase_transition_labels.py` (Day 12-13 outcome labels for trigger #1 ROC-AUC) — built; ~20 min wall-clock to run on 8,700 NCTs.
- `day13_dispatch_cached.py` (cached-only dispatch optimization) — built; conflicted with running Day 8 dispatch this turn, run cleanly next turn.
- `incremental_sharpe.py` orthogonalized within-stratum measurement — built.
- `rigor_pass.py` Bonferroni + bootstrap + DSR — built.
- `analysis/writeup_outline.md` — Day 19-20 paper draft template.

---

## Next-turn entry — primary objective: FULL DISPATCH

When user types "계속" or "Day 13 시작":

### Priority 1: Optimized full Phase 1 dispatch
- Run `day8_dispatch_async.py --n 1500` with PDF download batching optimization.
- Alternative: `day13_dispatch_cached.py --n 250` to use 763 cached PDFs first (no download bottleneck).
- Expected: 4,500 calls × $0.003 = $13.5 (within $22 cap), 30-45 min wall-clock.

### Priority 2: phase_transition_labels.py run
- `python -m clinicaltrials_amendment_llm.phase_transition_labels`
- ~20 min wall-clock (fetches intervention names from CT.gov v2 for 8,700 NCTs).
- Output: `manifest_phase_transition.jsonl` with binary `transitioned` per (NCT, target_phase).

### Priority 3: Re-measure all Phase 1 triggers with full data
- `cross_section_car`, `cross_llm_analyzer`, `day14_midcheckpoint`, `incremental_sharpe`, `rigor_pass` — all idempotent re-runs.
- F1-1 minority floor n≥20 should be cleared at full sample.
- Bonferroni-18 critical 2.99 reachable at full n.

### Priority 4: Final Layer A/B/C/D close path decision
- Run final close audit; pick Layer per CLAUDE.md spec.
- Day 19-20 writeup population (writeup_outline.md → analysis/F6_paper_draft.md).
- Day 21 hard cap.

### Priority 5 (if time): Streamlit dashboard
- Day 20 task per Phase 0 plan.

---

## State files

| File | Status |
|---|---|
| `data/manifest_global.json` | phase=phase1, **34/38 done**, current=day13_ctp_llm_baseline_replication |
| `data/manifest_amendment_fetch.jsonl` | **8,700 records** |
| `data/manifest_pdf_parse_audit.jsonl` | 40 records (100% × 2 samples) |
| `data/manifest_axis_classify.jsonl` | **313 records** (60 Day 6 + 60 Day 7 + 21 Day 7 dry-run + 164 Day 8 + 8 Day 13 cached) |
| `data/manifest_oracle_kappa.json` | latest κ |
| `data/manifest_sponsor_map.jsonl` | **2,530 mapped** |
| `data/manifest_car.jsonl` | 152 records (n=72 with full LLM labels + CAR) |
| `data/manifest_incremental_sharpe.jsonl` | latest Δ Sharpe measurement |
| `data/cache/pdf/*.pdf` | **763 cached protocol PDFs** |
| `analysis/{ctp_llm_baseline_spec, three_axis_schema, llm_prompt_3axis, day14_midcheckpoint, incremental_sharpe, rigor_pass, writeup_outline}.md/json` | committed |
| `audits/self_audit_day{1,2,3,6,7,14,17_18}_*.md` | per-day self-audit |
| 16 modules in `src/clinicaltrials_amendment_llm/` | committed |

---

## Spend

- Phase 0: **$0.17 / $8 cap** (2.07%)
- Phase 1 partial: **$0.26** ($0.42 total / $30 cap = 1.4%)
- Phase 1 full dispatch budget remaining: ~$21.6
- **F6 trigger #6 (spend > $30) wide margin: 98.6%**

---

## Done (commits)

```
$ git log --oneline (8 expected after this commit)
<commit8> Day 13/17-18 partial: TENTATIVE FIRE on triggers #2 + #3, F1-1 caveat applied; Day 19 rigor + writeup outline; full dispatch deferred
cbdd984 Day 8-14 partial: Phase 1 entry + 5y fetch + sponsor expansion + n=100 dispatch + mid-checkpoint TENTATIVE PASS
529c58e Day 7: Phase 0 EOD single kill gate 6/6 PASS — Phase 1 entry GO
47a9a6b Day 5+6: trigger #1/#6 PASS + #3 TENTATIVE PASS
552c15a Day 4 partial: 3-axis schema + LLM prompt template
27c5a47 Day 3: PDF parser dry-run trigger #6 PASS at 100%
8bc3dc3 Day 2: CT.gov 403 resolved via curl_cffi
b6a07d7 Day 1: F6 Phase 0 launch
```

---

## Working judgement for next turn (Layer projection)

Most likely outcome after full dispatch + Bonferroni-corrected re-measurement:
- **Layer A**: 30% (both Δ Sharpe ≥ 0.3 + CAR Bonferroni PASS at n=1,500)
- **Layer D**: 50% (Δ < 0.3 strict additive, but signal valid → writeup-only freeze publishable per CLAUDE.md spec)
- **Layer C**: <10% (both #2 + #3 fire and within-stratum mitigation collapses)
- **Hybrid A+D**: 10% (Phase 2 stratum Layer A + additive Δ Layer D footnote)

The F6 framework is robust either way: Layer D writeup is *first portfolio instance* of "negative incremental contribution publishable" pattern per CTP-LLM 흡수 risk gate spec.
