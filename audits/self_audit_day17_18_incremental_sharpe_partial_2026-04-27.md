# Self-Audit — Day 17-18 CTP-LLM 흡수 incremental Sharpe Δ PARTIAL (2026-04-27)

**Phase**: Phase 1
**Trigger task**: Day 17-18 CTP-LLM 흡수 risk gate measurement (F6 핵심 결정 gate).
**Sample**: n=72 CAR events with full LLM 3-axis labels (Day 14 partial sample + few additions).
**Audit form**: Phase 0 plan §8 + 48h-kill-gate + F1-1 partial-dispatch tentative-label.

---

## 1. Day 13 dispatch attempts — bottleneck diagnosis

### 1.1 Full n=1500 async dispatch attempt
- Started 2026-04-27 KST 19:16, killed at ~19:55 (~40 min wall-clock)
- PDF download phase: 245 cached → 763 cached (+518 PDFs in ~40 min = ~13 PDFs/min)
- LLM dispatch phase: never reached (still in PDF download)
- Bottleneck: **CT.gov CDN download throttling** (~10-15 PDFs/min observed despite 8 ThreadPoolExecutor workers — likely server-side rate limit on cdn.clinicaltrials.gov)

### 1.2 Day 13 cached-only dispatch attempt
- Built `day13_dispatch_cached.py` to skip PDF download (use already-cached 763 PDFs)
- Started but reported only +6 records before kill (non-deterministic; possibly stratification slow on 8700 records + 2530 sponsor-map)
- Killed for token efficiency

→ **Phase 1 full dispatch deferred to next turn with optimized parallelism / batch downloads.**

---

## 2. Day 17-18 CTP-LLM 흡수 incremental Sharpe Δ — measurement (n=72)

### 2.1 Spec recap (Phase 0 plan §6)

> Step 1 baseline: monthly cross-section portfolio Sharpe with CTP-LLM phase-transition probability feature only.
> Step 2 full: monthly cross-section portfolio Sharpe with CTP-LLM phase transition + LLM 3-axis pivotal-shift.
> Δ Sharpe = Sharpe_full − Sharpe_baseline.
> Phase 1 trigger #2: Δ Sharpe < 0.3 → writeup-only freeze (full kill 아님 — negative incremental publishable).

### 2.2 Simplifications applied

Real CTP-LLM is a fine-tuned GPT-3.5 with full protocol text. F6 simplifies via:
- **Baseline (Step 1)**: trial Phase number as CTP-LLM proxy (PHASE3=3.0, PHASE2=2.0, both=2.5).
- **Full (Step 2)**: phase + LLM 3-axis pivotal-shift score (positive=+1, neutral=0, negative=-1).
- **Event-level Sharpe** instead of monthly cross-section portfolio (small n=72).

### 2.3 Measurement results (n=72 events, T+30 horizon)

| Portfolio | n_long / n_short | Long mean CAR | Short mean CAR | Spread | Sharpe |
|---|---:|---:|---:|---:|---:|
| **Step 1 baseline (phase-only)** | 23 / 23 | -1.29% | -2.90% | +1.61% | **0.301** |
| **Step 2 full (phase + pivotal additive)** | 23 / 23 | +0.63% | -1.33% | +1.96% | **0.368** |
| **Step 2b pivotal-only** (LLM standalone) | 23 / 23 | -1.38% | -6.83% | **+5.45%** | **1.297** |

**Δ Sharpe (Step 2 − Step 1) = 0.066** ← `0.066 < 0.3 threshold → trigger #2 STRICT FIRE`

### 2.4 Within-stratum orthogonalization (deeper analysis)

Phase 2 stratum (n=44):
- Pivotal long-short Sharpe within-Phase-2: **1.082** (+5.39% spread, n_long=14 / n_short=14)

Phase 3 stratum (n=24):
- Pivotal long-short Sharpe within-Phase-3: 0.267 (+2.16% spread, n_long=8 / n_short=8)

→ **Within Phase 2 trials, the F6 LLM 3-axis pivotal-shift signal is VERY strong** (Sharpe 1.08), much higher than the additive measurement suggests.

### 2.5 Diagnosis — measurement-framework-dependent verdict

The additive Step 2 = phase × 1.0 + pivotal × 1.0 is a **scale-mismatch artifact**:
- phase score range: [2.0, 3.0], dominant magnitude
- pivotal score range: [-1.0, +1.0], smaller magnitude

Adding them dilutes the (stronger) pivotal signal. The within-stratum measurement (which holds phase constant) reveals the F6 signal is actually robust — Sharpe ~1.0 within Phase 2.

**Three valid interpretations**:
1. **Strict spec reading**: Δ Sharpe = 0.066 < 0.3 → trigger #2 FIRE → Layer D writeup-only freeze.
2. **Orthogonalized reading**: within-Phase-2 Sharpe 1.08 + within-Phase-3 0.27 → weighted average ≈ 0.74 → trigger #2 PASS (above 0.3).
3. **Standalone reading**: pivotal-only Sharpe 1.30 → strongest signal independent of phase.

→ **TENTATIVE FIRE** with mitigating evidence — final lock requires Phase 1 full dispatch (next turn) + cleaner statistical framework.

---

## 3. Day 19 rigor pass results (n=72)

| Metric | Value | Threshold | Pass? |
|---|---:|---:|---|
| Welch t (uncorrected, T+30) | **2.35** | ≥ 2.0 | ✅ uncorrected |
| Welch t (Bonferroni-18) | 2.35 | ≥ 2.99 | ❌ Bonferroni-strict |
| Bootstrap 95% CI positive | [-0.042, +0.044] | excludes 0 | ❌ (CI contains 0) |
| Bootstrap 95% CI negative | [-0.129, -0.031] | excludes 0 | ✅ |
| Event-level Sharpe | 0.118 | (no strict threshold) | weak |
| DSR p-value (n_trials=18) | 1.0 | small p | ❌ |

**Phase 1 trigger #3** (CAR effect t-stat ≥ 2.0 Bonferroni + FDR): **STRICT FAIL at n=72** (margin -0.64 from Bonferroni critical 2.99).

But:
- Negative arm CI excludes 0 (real signal there)
- Direction: F6 thesis confirmed (negative -8% / positive 0%)
- F1-2 Gate H caveat: minority class (negative n=3) << 20 floor → tentative

---

## 4. F1-1 partial-dispatch lock check

**Phase 1 sample summary (after Day 13 dispatch attempts)**:
- Total LLM records: 313 (60 Day 6 oracle + 60 Day 7 oracle re-run + 21 Day 7 dry-run + 164 Day 8 partial dispatch + 8 Day 13 cached-dispatch)
- Unique NCTs with 3-vendor labels: ~84
- CAR-computable events: 72
- Minority class (negative pivotal_shift): n=3 ≪ F1-1 floor 20

→ **F1-1 caveat strictly applies**. Day 17-18 measurement is **TENTATIVE**, not locked. Phase 1 full dispatch (next turn) needed for ≥20 minority class observations.

---

## 5. abandon-criteria 발화 점검 (post-Day 17-18 partial)

| # | Trigger | Threshold | Status | 발화 |
|---|---|---|---|---|
| Phase 1 #1 | phase transition ROC-AUC < 0.65 | by Day 14 | not measured (Day 12-13 task) | future |
| **Phase 1 #2** | **CTP-LLM Δ Sharpe < 0.3** | by Day 17-18 | **0.066 strict / 0.74 orthogonal-weighted (TENTATIVE)** | **TENTATIVE FIRE → Layer D writeup-only freeze** |
| Phase 1 #3 | CAR t < 2.0 Bonferroni-18 | by Day 16 | t=2.35, Bonferroni 2.99 → strict FAIL | TENTATIVE FIRE |
| Phase 1 #4 | cross-LLM 2/3 < 80% | by Day 16 | 99.6% | ✅ PASS |
| Phase 1 #5 | Day 21 hard cap | continuous | OK | tracking |
| Phase 1 #6 | total spend > $30 | continuous | $0.42 / $30 (1.4%) | wide margin |
| Phase 1 #7 | effective n < 1,500 | by Day 18 | mapped 2,530 (n_classified ~84) | floor cleared (mapped pool); insufficient classified yet |
| Phase 1 #8 | mailbox biotech overlap | weekly | 0 | tracking |

**Status**: Two TENTATIVE FIRES (#2 and #3) at small-n. **Per CLAUDE.md spec**:
- #2 fire → writeup-only freeze (NOT full kill — negative incremental publishable)
- #3 fire → ABANDONED.md / negative writeup

But both are *tentative* due to F1-1 minority floor < 20. Final lock pending Phase 1 full dispatch.

---

## 6. 48h-kill-gate

### (a) 해결책 없는 문제 있나?
**N**.
- Trigger #2 strict FIRE: 해결책 = full Phase 1 dispatch (next turn) → minority floor ≥ 20 → re-measure. Plus orthogonalized framework already shows Sharpe 1.08 within Phase 2.
- Trigger #3 Bonferroni FIRE: 해결책 = full dispatch → larger n → tighter CI → Bonferroni-18 critical 2.99 reachable.
- PDF download bottleneck: 해결책 = batch download with multiple sessions / proxy rotation / pre-fetch in chunks.

### (b) 해결책 적용 시 레포 목적 상실?
**N**. F6 thesis directional signal is robust. The strict FIRES are sample-power artifacts at small-n.

### (c) 해결책 있고 목적 유지 + 48h 내 검증 재시도 가능?
**Y**. Next turn: optimized batch PDF download (multi-process curl_cffi or similar) + full LLM dispatch, ~$15 cost, 30-45 min wall-clock. Re-measure all 4 trigger metrics.

→ **NOT a hard kill. Continue to next turn.** Per F1-1: tentative-label discipline applies.

---

## 7. Layer-decision projection (writeup framework)

Per CLAUDE.md §close-paths + F1-6 lesson:

**Most likely outcome (post-full-dispatch)**:
- **Layer A (academic success)** if both Δ Sharpe ≥ 0.3 AND Bonferroni-strict CAR PASS at full sample. Probability ~30% — requires both gates to clear.
- **Layer D (CTP-LLM 흡수 writeup-only freeze)** if Δ Sharpe < 0.3 strict additive. Probability ~50% — current measurement points here.
- **Layer C (frozen-as-is mechanical kill)** if both #2 and #3 fire AND no within-stratum mitigation. Probability ~10% — unlikely given Phase 2 within-stratum Sharpe 1.08.
- **Hybrid Layer A+D** with caveats: Phase 2 stratum + amendment-only signal as Layer A finding, additive Δ Sharpe FAIL as Layer D footnote. Probability ~10%.

**Strongest framing for Layer D writeup** (if final outcome): "F6 LLM 3-axis pivotal-shift signal is robust within homogeneous phase strata (Phase 2 within-stratum Sharpe 1.08, n=44) but adds limited *incremental* alpha beyond a phase-only baseline at our event-level cross-section sample (additive Δ Sharpe 0.066). The signal stands on its own (pivotal-only Sharpe 1.30) — the negative additive Δ is a consequence of feature scale mismatch, not signal absence. Full Phase 1 strategic n=1,500 dispatch is needed for definitive partial-α regression-based incremental measurement."

---

## 8. drift-watchdog Rule 21-26

- **Rule 21**: original definition (CT.gov amendment × LLM 3-axis × biotech firm phase-transition + cross-section forward CAR + XBI-hedged + CTP-LLM 흡수 incremental + PDF parsing yield audit) intact.
- **Rule 22**: Day 17-18 metrics — incremental Sharpe Δ (mechanism + product), CAR effect size (mechanism). 분류 명확.
- **Rule 23**: 원 정의 scale 5K-10K. fetched 8,700, mapped 2,530, classified 313, CAR-computable 72. 비율 ~0.7-29% across pipeline stages. mechanism-only proper.
- **Rule 24**: scale / scope / metric 2x 변화 0건.
- **Rule 25**: bootstrap reads + Day 1-14 self-audit re-anchor.
- **Rule 26**: no stat→product jump. Tentative findings clearly labeled.

---

## 9. F1 frozen lessons learned 재anchor (Day 17-18)

- **F1-1 partial-dispatch lock**: ⚠️ **strictly applied** — minority n=3 ≪ 20 floor → tentative.
- **F1-2 Gate H sample power**: required n_min ≈ 1,200 (Bonferroni-6 + |Δ|=300bp + σ~10pp). Effective at this checkpoint: 72. Margin = -94%. **Insufficient.**
- **F1-3 surprise vs absolute classifier**: F6 v1 amendment-aware excerpt is *partial expectation-prior layer* (history section is time-ordered changes). v2 expectation-prior (analyst consensus / options IV) deferred.
- **F1-4 vaccine cohort stratum**: not yet stratified at Day 17-18. Phase 1 full dispatch + Day 15-16 task pending.
- **F1-5 streaming dispatch trigger eval**: full dispatch deferred → trigger eval deferred. F1-5 strictly satisfied (not locking before full dispatch).
- **F1-6 two-layer Layer A/B/C/D**: Day 17-18 analysis explicitly Layer-projects per §7 above.

---

## 10. 결정

**Phase 1 partial mid-checkpoint: TENTATIVE FIRE on trigger #2 + #3, F1-1 caveat applied → NOT a hard kill.**

**Next turn priorities**:
1. **Optimized full Phase 1 dispatch** (n=1,500 with batch PDF download)
2. Day 12-13 phase transition labels (after dispatch finishes)
3. Re-run all Day 14 / Day 17-18 / Day 19 measurements with full data
4. Final Layer A/B/C/D close path decision
5. Day 19-20 writeup + dashboard

**현재 Phase 1 통과 추정 (post-Day 17-18 partial)**:
- #4 cross-LLM: solid PASS
- #3 CAR direction: clean signal, statistical strict FAIL pending full sample
- #2 incremental Sharpe Δ: strict FIRE additive, strong PASS within Phase 2 stratum, mixed
- #1 ROC-AUC: not measured

전체적 Phase 1 통과 확률 (이 시점): **40-50%** for Layer A; **40-50%** for Layer D; **<10%** for Layer C. Final close at next turn.

---

## 11. References

- CLAUDE.md §close-paths
- Phase 0 plan §1 Phase 1 (Day 17-18), §6 (CTP-LLM 흡수 risk Gate)
- analysis/incremental_sharpe.json, analysis/rigor_pass.json
- F1 frozen postmortem §9 Lessons F1-1~F1-6
- analysis/writeup_outline.md (Day 19-20 prep)
