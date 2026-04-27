# F6 — ClinicalTrials.gov Protocol Amendment LLM

ClinicalTrials.gov v2 amendment text × multi-vendor LLM ensemble × 3-axis *pivotal shift* classification → biotech sponsoring firm *phase transition probability* + 1m–1y forward CAR (XBI-hedged).

**Status**: Phase 0 (Day 1, 2026-04-27)
**Type**: discovery-form alpha-research, F1 frozen swap-queue 1순위 fill.
**Daemon**: PURE daemon-free (Gate F ✓) — ClinicalTrials.gov v2 API + yfinance + OpenRouter only. SEC EDGAR daemon 호출 차단.

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
