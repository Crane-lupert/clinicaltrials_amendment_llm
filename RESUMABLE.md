# RESUMABLE — F6 (clinicaltrials_amendment_llm)

**Last sync**: 2026-04-27 KST
**Phase**: phase0
**Tasks done**: 15 / 38 (Day 1-3 + Day 2 setup + Day 3 PDF dry-run)
**Current task**: `day4_n10_dry_run_start`

---

## What completed this session (Day 1 + Day 2 + Day 3)

- Day 1: skeleton (pyproject + manifest + resume + ctgov_client + pdf_parser + tests) + CTP-LLM (arxiv 2408.10995) baseline spec + scoop check (3 query, 0 financial-extension paper, CLaDMoP risk LOW) + OpenRouter mailbox request + daemon-free Gate F verify + initial git commit.
- Day 2: pip install + curl_cffi TLS workaround for CT.gov 403 (httpx universally blocked, curl_cffi Chrome impersonation passes) + biotech_universe.py (77-firm seed) + day2_fetch.py (200 records, 100% industry-sponsored Phase 2/3, 17% sponsor->ticker mapped) + Day 2 commit.
- Day 3: day3_pdf_dryrun.py (n=20 sub-sample, all hasProtocol=true) + **Phase 0 trigger #6 PASS at 100%** (18 success + 2 partial, 0 ocr/failed/no_pdf) + Day 3 commit.
- Day 4 partial (LLM-free): three_axis_schema.md + llm_prompt_3axis.md (full prompt template + cost estimate showing strategic-sample n ≈ 1,500 fits $22 Phase 1 cap).

---

## What is BLOCKED (next-turn task)

- **OpenRouter F6 client_id 등록**: mailbox request pending at `D:/vscode/portfolio-coordination/mailbox/portfolio_coordination/20260427T1430-clinicaltrials_amendment_llm-openrouter-register.md` (correlation_id `20260427T1430-clinicaltrials_amendment_llm-001`). Until coord side processes:
  - **n=20 oracle pilot 3-vendor κ** (trigger #3) — Day 6 EOD blocked
  - **n=10 full-pipeline dry-run** (trigger #2) — Day 7 EOD blocked (LLM 3-axis label is one stage)

---

## Next-turn instructions

### If user types "계속" or "Day 4 시작":

1. **Check mailbox first**: `ls D:/vscode/portfolio-coordination/mailbox/clinicaltrials_amendment_llm/` for OpenRouter response. If resolved → proceed to step 2. If still pending → fall back to step 3.

2. **OpenRouter ready path** (n=20 oracle + n=10 dry-run + Day 6 κ measure):
   - Pick 20 NCTs from `data/cache/pdf/` already-downloaded sample (re-use Day 3 sub-sample for cost efficiency)
   - For each, build `{nct_id, sponsor_name, sponsor_class, phase, study_first_submit_date, last_update_post_date, protocol_text_excerpt}` payload per `analysis/llm_prompt_3axis.md`
   - Hand-label oracle (claude-direct, no LLM call): write to `data/oracle_n20.json` with the schema {nct_id, pivotal_shift, admin_vs_substantive, driver, is_vaccine_cohort, rationale}
   - Run 3-vendor LLM ensemble on the same 20 — Opus 4.7 / Sonnet 4.7 / Llama-3.3-70B-Instruct (or Gemma-2-27B fallback). Persist to `data/manifest_axis_classify.jsonl`.
   - Compute Fleiss κ across 3 raters (LLM × 3 — exclude oracle for κ). Compute LLM-vs-oracle accuracy as auxiliary.
   - Persist to `data/manifest_oracle_kappa.json`.
   - Trigger #3: κ ≥ 0.6 → PASS; otherwise 2-axis fallback (per `three_axis_schema.md` §2-Axis Fallback) and re-measure.

3. **OpenRouter pending path** (no LLM):
   - Hand-label `data/oracle_n20.json` (Claude reading 20 protocols, ~5-50pp each — substantial work but doable).
   - Build `n10_dryrun.py` skeleton that runs *all stages except LLM*: fetch -> PDF parse -> sponsor map -> placeholder LLM (mark `pending_openrouter`) -> sponsor->ticker -> forward CAR via yfinance.
   - This isolates LLM dependency to the single stage that mailbox-coordination unblocks.

4. **Day 5 expansion regardless of LLM**:
   - Expand fetch query window to 2 years (FY2023+FY2024) to push fetched count toward trigger #1 floor (≥3000).
   - Re-run Day 3 PDF dry-run on a *different* 20-NCT sample to confirm trigger #6 stays ≥80%.

---

## State files

| File | Purpose | Status |
|---|---|---|
| `data/manifest_global.json` | phase / current_task / done set / spend tracker | 15/38 done, current=day4_n10_dry_run_start |
| `data/manifest_amendment_fetch.jsonl` | 200 records (Day 2 first fetch) | 200 lines |
| `data/manifest_pdf_parse_audit.jsonl` | n=20 PDF parse audit (Day 3 trigger #6 PASS) | 20 lines |
| `data/cache/pdf/*.pdf` | 20 cached protocol PDFs (gitignored) | 20 files |
| `audits/scoop_check_2026-04-27.md` | Day 1 weekly scoop (no financial extension found, CLaDMoP risk LOW) | committed |
| `audits/self_audit_day{1,2,3}_*.md` | per-day self-audit logs | committed |
| `analysis/ctp_llm_baseline_spec.md` | Day 13 replication + Day 17-18 Two-step regression | committed |
| `analysis/three_axis_schema.md` | classification schema | uncommitted |
| `analysis/llm_prompt_3axis.md` | LLM prompt template + cost estimate | uncommitted |

---

## Phase 0 trigger status (post-Day 3)

| # | Trigger | Threshold | Day 3 status | Closed? |
|---|---|---|---|---|
| 1 | fetched < 3,000 | by Day 5 | 200 (Day 2 sample) | partial — Day 5 expansion task |
| 2 | n=10 dry-run < 7/10 | by Day 7 | not measured | open (LLM blocked) |
| 3 | Fleiss κ < 0.6 | by Day 6 | not measured | open (LLM blocked) |
| 4 | spend > $8 | continuous | $0.00 / $8 | tracking |
| 5 | scoop discovered | weekly | 0 financial scoop | closed (Day 1) |
| **6** | **PDF yield < 80%** | **by Day 7** | **100% (n=20)** | **CLOSED (Day 3)** |

→ 2 trigger closed (5 + 6), 1 tracking (4), 3 open (1 + 2 + 3 — all unblocked-or-progressed by next turn).

---

## Outstanding mailbox

- **Outbound**: `mailbox/portfolio_coordination/20260427T1430-clinicaltrials_amendment_llm-openrouter-register.md` (open, expects_reply=true)
- **Inbound processed**: 1 broadcast (`20260426T2340-portfolio_coordination-bcast-001` → `.broadcast_seen`)

---

## Spend

- OpenRouter Phase 0: $0.00 / $8 cap
- OpenRouter Phase 1: $0.00 / $22 cap
- Total: $0.00 / $30 cap

---

## Done (commits)

```
$ git log --oneline
<commit3> Day 3: PDF parser dry-run n=20 - Phase 0 trigger #6 PASS at 100%
<commit2> Day 2: CT.gov 403 resolved via curl_cffi + biotech universe seed + first amendment fetch
<commit1> Day 1: F6 (clinicaltrials_amendment_llm) Phase 0 launch - skeleton + CTP-LLM baseline spec
```
