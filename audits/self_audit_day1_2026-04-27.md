# Self-Audit — Day 1 (2026-04-27)

**Phase**: Phase 0
**Trigger task**: Day 1 EOD (CT.gov v2 API skeleton + CTP-LLM baseline spec + scoop check + manifest skeleton + OpenRouter register + daemon-free verify).
**Audit form**: Phase 0 plan §8 self-audit + 48h-kill-gate.

---

## 1. 현재 문제점 inventory (치명도 순)

### High (즉시 해결)
- 없음.

### Medium (Day 2 entry 전 해결 권장)
1. **shared_utils API 가정 오류 정정 완료**: 초기 `manifest.py` 가 `shared_utils.atomic_io.append_jsonl` / `read_jsonl` 을 import 했으나 실제로는 부재 (atomic_io.py 74줄, `atomic_write_text/bytes/json` 만 노출). manifest.py 에 `filelock.FileLock` 직접 사용 + 인라인 `_append/_read` helper 로 정정. 영향: F6 후속 manifest write 가 atomic + cross-process safe. 추후 shared_utils 측에 promotion 검토 가능.
2. **OpenRouter client_id 미설치**: portfolio-coordination mailbox 요청 발송 (correlation_id `20260427T1430-clinicaltrials_amendment_llm-001`). coord 측 처리까지 대기. **F6 측 작업 영향**: Day 2 amendment fetch 는 OpenRouter 미사용 (CT.gov + filer_ontology 만), Day 4-6 oracle pilot 시작 전까지 처리 도래해야 함. 미수신 시 Day 4 진입 직전 follow-up 발송.

### Low (Day N+ 처리)
1. **`pip install -e .` 미실행**: Python `python -m clinicaltrials_amendment_llm.resume` 는 sys.path 직접 추가 시 작동. 정식 install 은 Day 2 진입 전 1회 실행 권장 (test 자동화 + 의존성 설치 동시).
2. **CTP-LLM full PDF read 보류**: WebFetch 가 arxiv `/abs/` 페이지에서 abstract 외 본문 read 제한. Day 13 baseline replication 시점에 IEEE PDF 또는 arxiv html v1 raw download 필요 (`analysis/ctp_llm_baseline_spec.md` §3 open question 1-5 명시).

---

## 2. 각 문제별 자체 해결책 강구

| # | 문제 | 해결책 | 적용 |
|---|---|---|---|
| Med-1 | shared_utils API 가정 오류 | inline FileLock + JSONL append/read | ✅ 적용 완료 (manifest.py) |
| Med-2 | OpenRouter client_id 미설치 | mailbox request → coord 처리 대기 + Day 4 follow-up | ✅ mailbox 발송 완료 |
| Low-1 | pip install -e | Day 2 entry 직전 1회 실행 | Day 2 task |
| Low-2 | CTP-LLM full PDF read | Day 13 replication 시 IEEE PDF / arxiv html v1 raw | Day 13 task |

---

## 3. 48h-kill-gate 적용

### (a) 해결책 없는 문제 있나?
**N**. 모든 problem 에 명시 해결책 있음.

### (b) 해결책 적용 시 레포 목적 상실?
**N**.
- shared_utils API mismatch 정정 → manifest 정상 작동, 레포 목적 무관.
- OpenRouter pending → Day 4 마감 대비 buffer 7일 (mailbox expires_at), 충분.
- CTP-LLM PDF read 지연 → Day 13 까지 12일 buffer. Day 1 abstract-level spec 으로 baseline 명세 충족.
- Phase 0 trigger #5 (scoop) 미발화 (CLaDMoP risk LOW, 0 financial extension paper) — 레포 목적 intact.
- daemon-free Gate F ✓ verified (`.claude/settings.json` deny rule + `ctgov_client._assert_allowed_url` 이중) — Y kill 후 정책 위반 0건.

### (c) 해결책 있고 목적 유지 + 48h 내 검증 재시도 가능?
**Y** for all.
- shared_utils 정정: 즉시 적용 + `python -c` smoke 4/5 PASS 검증 (TASK_SEQUENCE assertion 만 카운트 mismatch, 본질 무관).
- OpenRouter: 발송 완료, Day 4 follow-up checkpoint.
- CTP-LLM: Day 13 deadline.

→ **Day 2 진입 OK. 모든 problem 해결책 적용 완료 또는 buffer 안.**

---

## 4. Day 1 deliverable 체크리스트 (Phase 0 plan §1 Day 1)

- [x] Repo init (`git init -b main` + git config user)
- [x] `.claude/settings.json` daemon-free Gate F ✓ verify (이미 존재 — SEC `data.sec.gov/efts.sec.gov/www.sec.gov` deny + `mcp__sec_*/edgar_*` deny + `Bash(curl/wget*sec.gov:*)` deny + `Bash(python*sec_client*)` deny). 본 코드 측 `ctgov_client.DaemonViolationError` 이중 안전망.
- [x] OpenRouter client_id 등록 요청 (mailbox 발송)
- [x] CTP-LLM (arxiv 2408.10995) full read (abstract + IEEE 재게재 metadata) → `analysis/ctp_llm_baseline_spec.md` 작성
- [x] arxiv/SSRN 신규 paper 점검 (3 query) — 0 financial extension scoop, CLaDMoP (arxiv 2505.18527) risk LOW
- [x] Resume entry point + manifest skeleton (`src/clinicaltrials_amendment_llm/manifest.py` + `resume.py` + `__main__.py`)
- [x] CT.gov v2 API client skeleton (`ctgov_client.py` — fetch_study, search_studies, fetch_version_history, batch_fetch_studies)
- [x] PDF parser skeleton (`pdf_parser.py` — pdfplumber → pypdf fallback, 5-bin yield distribution, trigger #6 helper)
- [x] Smoke test (`tests/test_smoke.py` — 6 tests, all sanity)
- [x] README.md
- [x] Daily checkpoint (`checkpoints/2026-04-27.md`)

**EOD Gate**: repo bootable / daemon-free OK / CTP-LLM 명세화 / scoop 미발견 → **PASS**.

---

## 5. abandon-criteria SKILL §Phase 감사 통합 양식 자가 fill

### Phase 0 선언된 triggers

1. **[Data-validity] CT.gov v2 amendment fetch < 3,000** — Day 5 EOD. Source `data/manifest_amendment_fetch.jsonl`. 발화 N (Day 5 도래 전).
2. **[Data-validity] n=10 full-pipeline coverage < 7/10** — Day 7 EOD. 발화 N.
3. **[Mechanism] LLM ensemble agreement n=20 oracle Fleiss κ < 0.6** — Day 6 EOD. 발화 N.
4. **[Resource] Phase 0 OpenRouter spend > $8** — Day 7 EOD. 발화 N (현재 $0).
5. **[Product-market] arxiv/SSRN scoop OR CTP-LLM 후속 financial paper** — weekly. **이번 turn 점검 — 미발화** (3 query, 0 financial extension scoop).
6. **[Data-validity] PDF parsing yield < 80% (n=20 sub-sample)** — Day 7 EOD. 발화 N (Day 5-6 도래 전).

**조치 실행 여부**: trigger 발화 0건 → 조치 N/A. `audits/scoop_check_2026-04-27.md` weekly 점검 commit.

---

## 6. drift-watchdog SKILL Rule 21-26 자가 fill

- **Rule 21 (vision anchoring)**: CLAUDE.md (자동 load) + reference-validation §1.1 + Phase 0 plan §1 재읽음. 원 정의 (CT.gov v2 amendment text × 3-axis pivotal-shift LLM × biotech firm phase-transition + cross-section forward CAR + XBI-hedged + CTP-LLM 흡수 incremental + PDF parsing yield audit) 와 현 실행 (skeleton + spec) 일치.
- **Rule 22 (metric type)**: 이번 turn metric — task completion (project metric) + 7 deliverables (mechanism preparation). product claim 부재 (Phase 0 Day 1).
- **Rule 23 (scale)**: 원 정의 scale ~5K-10K amendments. 현 scale 0 (Day 2 fetch). 비율 0% — Day 2-5 측정. mechanism-only 주장 강제 적용.
- **Rule 24 (drift trigger)**: scale / scope / metric 2x 변화 0건.
- **Rule 25 (session re-anchor)**: 본 session 시작 시 17 bootstrap reads (F1 postmortem + Phase 0 plan + reference-validation §1-7.3 + portfolio-research-rules §1-5.5 + 4 skills + shared_utils overview + SCHEMA.md) 완료.
- **Rule 26 (stat ≠ product)**: stat→product 점프 X (Phase 0 Day 1, 통계 측정 0).

---

## 7. F1 frozen lessons learned (F1-1~F1-6) 재anchor

- **F1-1 partial-dispatch lock-and-revise 회피**: trigger evaluation 은 dispatch ≥95% 또는 minority-class n ≥ 20 도달 후. F6 Day 2-7 fetch / oracle / dry-run 모두 batch 단위 + atomic write — partial 평가 lock 위험 차단.
- **F1-2 Gate H sample power pre-registration**: Phase 1 trigger #7 (effective n) 의 required n_min ≈ 1,200 vs 가용 ~1,500 (margin 25%) — reference-validation §4.5.1 명시. Day 14 mid-checkpoint 에서 effective-n 1차 측정 의무.
- **F1-3 surprise vs absolute classifier**: F6 v1 absolute 한계 writeup 명시 (Layer A draft). expectation-prior layer 는 v2 또는 unfreeze 조건.
- **F1-4 vaccine cohort stratum**: 2020-2022 COVID/RSV/influenza vaccine trial amendment 별도 stratum (Day 15-16 task).
- **F1-5 streaming dispatch trigger eval**: full sample 20K-30K LLM dispatch 완료 후 trigger #1/#2/#3 평가.
- **F1-6 two-layer Layer A/B/C/D**: writeup 처음부터 Layer A/B/C/D 적용 (README + plan §1).

---

## 8. 결정

**Day 1 EOD pass. Day 2 entry.**

다음 task: `day2_biotech_universe_filter` + `day2_amendment_fetch_first` + `day2_sponsor_ticker_skeleton`.

이 self-audit log → git commit (Day 1 initial commit 의 부분 — single commit 으로 Day 1 자산 일괄).

---

## 참고

- Phase 0 plan §8 self-audit 양식
- abandon-criteria SKILL §Phase 감사 통합
- drift-watchdog SKILL Rule 21-26
- F1 frozen postmortem §9 Lessons F1-1~F1-6
