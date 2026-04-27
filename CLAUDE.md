# Project F6 — ClinicalTrials.gov Protocol Amendment LLM

> ClinicalTrials.gov protocol amendment text × multi-vendor LLM ensemble × *pivotal shift* 분류 → biotech sponsoring firm *phase transition probability* 사전 예측 + forward CAR. **F1 frozen 후 swap 1순위 launch 2026-04-27**. **PURE daemon-free** (Gate F ✓), **discovery-form** (Gate G ✓). CTP-LLM (arxiv 2408.10995) financial extension.
>
> Reference validation: `d:/vscode/meta-harness/audits/2026-04-27-clinicaltrials-amendment-reference-validation.md` (522줄). Phase 0 plan: `d:/vscode/meta-harness/audits/2026-04-27-project-clinicaltrials-amendment-phase0-plan.md` (393줄). Overnight prompt v4: `d:/vscode/meta-harness/audits/2026-04-27-project-clinicaltrials-amendment-overnight-start-prompt.md` (216줄).

---

## Purpose

ClinicalTrials.gov API 의 protocol amendment text (시험 design 변경 — endpoint / sample size / dose / population) → 3-vendor LLM ensemble *pivotal shift* 3-axis 분류 (positive: dose escalation / scope expansion / accelerated timeline / negative: endpoint shrink / sample size 축소 / population narrowing) → biotech sponsoring firm *phase transition probability* 사전 예측 → forward CAR (1m-1y holding).

**핵심 가설**: amendment 의 pivotal shift type 이 시험 진행 상황의 leading indicator. positive amendment biotech long, negative short → cross-section forward CAR alpha.

**기여**: CTP-LLM (arxiv 2408.10995) "Clinical Trial Phase Transition Prediction with LLM" 의 *financial extension* — phase transition prediction → equity alpha cross-section. **CTP-LLM 흡수 risk**: incremental Sharpe ≥0.3 미달 시 → writeup-only freeze (full kill 아님, negative incremental publishable).

**F1 frozen lessons learned 적용**: partial-dispatch lock-and-revise 회피 + Gate H sample power pre-registration + vaccine cohort stratum + two-layer reporting (Layer A/B/C/D).

---

## Dependencies (공유 인프라)

- ClinicalTrials.gov API v2 무료 (2007-2026, 매년 수만 amendment, biotech sponsoring R1000 firm subset)
- sponsor → ticker mapping (drugs@FDA + Orange Book + filer_ontology fallback chain — F1 패턴 reuse)
- biotech price (yfinance, 1m-1y horizon)
- OpenRouter: `shared_utils.openrouter_client.OpenRouterClient(project="clinicaltrials_amendment")`, project cap=$25
- Atomic IO: `shared_utils.atomic_io.atomic_write_json + FileLock`
- **SEC daemon 사용 X** (Gate F ✓)
- 체크포인트: 매일 `portfolio-coordination/checkpoints/<date>/clinicaltrials.md`
- Mailbox: `D:/vscode/portfolio-coordination/mailbox/clinicaltrials_amendment_llm/`

---

## Phase Scope

### Phase 0 — Week 1 (Day 1-7)
- Day 1: repo init + manifest skeleton + ClinicalTrials.gov API client skeleton + CTP-LLM (arxiv 2408.10995) full read + arxiv/SSRN 신규 paper 사전 조사 + Gate F 재확인
- Day 2-3: small sample fetch (biotech R1000 sponsoring firm × 1y = ~5K-10K amendments) + **PDF parsing yield 측정 (F6 특수, pdfplumber + pypdf fallback)**
- Day 4: 3-vendor LLM ensemble n=20 oracle pilot (3-axis schema)
- Day 5: Fleiss κ ≥0.6 verify
- Day 6: n=10 full-pipeline dry-run + sponsor→ticker mapping coverage 측정
- **Day 7 EOD 단일 kill gate (6 AND)**: fetched ≥3,000 + n=10 dry-run ≥7/10 + 3-axis Fleiss κ ≥0.6 + spend ≤$8 + scoop 미발견 + **PDF parsing yield ≥80%** (F6 특수)

### Phase 1 — Week 2-3 (Day 8-21)
- Day 8-12: full sample LLM inference + sponsor→ticker mapping
- Day 13-15: cross-section biotech CAR + phase transition probability 측정
- Day 16-17: rigor pass (FDR, DSR, bootstrap, contamination, vaccine cohort stratum)
- **Day 17-18: CTP-LLM incremental Sharpe ≥0.3 verify** (Phase 1 #2 핵심 gate)
- Day 19-20: Streamlit dashboard + writeup
- Day 21: hard cap

---

## Day-by-Day Gate (요약)

- Day 1 EOD: API skeleton + CTP-LLM paper read + scoop 사전 조사
- Day 5 EOD: PDF parsing yield ≥80% (F6 특수)
- **Day 7 EOD: 단일 kill gate 6 AND**
- Day 14 EOD: cross-section CAR initial measure
- **Day 17-18: CTP-LLM incremental Sharpe gate** (Phase 1 #2)
- Day 21 EOD: hard cap

Y kill 의 18시간 single-burst 패턴 + F1 frozen partial-dispatch lock-and-revise 패턴 회피 — daily checkpoint + self-audit + abandon mechanical + 4중 안전망.

---

## Abandon Criteria (4-category, Phase 별 ≥3)

상세: reference-validation §4.

### Phase 0
1. **[Data-validity]** Day 5 EOD fetched < 3,000 → fetch retry / R&D quartile→quintile 1회만, 미달 시 중단
2. **[Mechanism]** Day 6 n=20 pilot Fleiss κ < 0.6 → 3-axis → 2-axis fallback (positive vs negative binary) 1회만, 재미달 시 중단
3. **[Data-validity]** Day 5 PDF parsing yield < 80% → pdfplumber → pypdf fallback chain 1회만, 재미달 시 중단 (F6 특수)
4. **[Resource]** Phase 0 spend > $8 → Phase 1 진입 보류
5. **[Product-market]** **arxiv/SSRN "ClinicalTrials amendment LLM stock returns", "CTP-LLM financial extension biotech alpha" 신규 paper 출현** → 즉시 중단

### Phase 1
1. **[Mechanism]** Day 14 cross-section spread Sharpe < 0.3 OR FDR-adjusted alpha |t| < 2.0 → negative writeup
2. **[Mechanism]** **Day 17-18 CTP-LLM incremental Sharpe < 0.3 → writeup-only freeze (full kill 아님 — negative incremental publishable)**
3. **[Resource]** Day 21 EOD hard cap
4. **[Data-validity]** Final analyzable sample < 1,500 → power 부족 (F1 lesson learned: required n_min ≈ 1,200 vs effective n ~1,500 margin 25% — unsafe 영역 회피)
5. **[Product-market]** mailbox 통한 portfolio overlap signal → orthogonality test

---

## F1 Frozen Lessons Learned 적용

F1 frozen-postmortem 의 핵심 lesson 4 적용:

1. **Partial-dispatch lock-and-revise 회피**: trigger eval 은 dispatch ≥95% 도달 후 시행 (Day 5 PDF parsing → Day 7 kill gate, dispatch 부분 시 trigger 평가 X)
2. **Gate H sample power pre-registration**: required n_min ≈ 1,200 (Phase 1 #4) vs effective n ~1,500 margin 25% — F1/β2 unsafe 영역 회피
3. **Vaccine cohort stratum**: 2020-2022 COVID/RSV/influenza 별도 stratum 처리 (regime-specific noise 흡수)
4. **Two-layer reporting**: Layer A (academic) / B (production) / C (frozen-as-is) / D (kill) 사전 등록 close 경로

---

## Inter-Repo Mailbox

QR Scout 멤버 간 파일 메시지 버스. 가입 사유: shared-utils + buy-side weapon + biotech overlap test (F1 frozen 자산 학습).

- Inbox: `D:/vscode/portfolio-coordination/mailbox/clinicaltrials_amendment_llm/`
- 절차: `D:/vscode/portfolio-coordination/mailbox/SCHEMA.md`
- 자동 감지: SessionStart + UserPromptSubmit hook
- 가입 5단계: `d:/vscode/meta-harness/templates/qr-scout-mailbox-onboarding.md`

처리: 응답 도입부 "📬 처리: N건" (0건 생략). 발신: `mailbox/<target>/<ISO>-clinicaltrials_amendment_llm-<slug>.md`. **금지**: secret / .env / API key.

---

## 통계 Rigor Checklist

- [ ] IS/OOS: 2007-2018 IS, 2019-2026 OOS (frozen)
- [ ] FDR (3-axis × 3-horizon × phase = ~12 검정)
- [ ] Deflated Sharpe Ratio
- [ ] Bootstrap CI B=1000, cluster by sponsor
- [ ] Newey-West 표준오차
- [ ] FF5+momentum 직교화
- [ ] Vaccine cohort stratum (2020-2022 COVID/RSV/influenza 별도)
- [ ] **CTP-LLM incremental Sharpe ≥0.3** verify (Phase 1 #2 의무)
- [ ] Contamination audit (LLM cutoff vs amendment date + drug-name masking + sponsor-name masking)

---

## Skill Harness

- `.claude/skills/abandon-criteria/SKILL.md` v1.1
- `.claude/skills/drift-watchdog/SKILL.md`
- `.claude/skills/karpathy-guidelines/SKILL.md`
- `.claude/skills/repo-autonomy-overnight/SKILL.md`

---

## Deliverables

**공통**:
- [ ] GitHub public repo + README
- [ ] Streamlit dashboard URL
- [ ] Paper draft 8-12p (SSRN, CTP-LLM financial extension positioning)
- [ ] Interview demo 5분 + CV/LinkedIn 1-line

**close 경로별** (`d:/vscode/meta-harness/reports/`):
- Layer A success → `{{YYYY-MM-DD}}-clinicaltrials-amendment-paper-practical.md`
- Layer B production-grade → 별도 deployment audit
- Layer C frozen-as-is (mechanical kill) → `{{YYYY-MM-DD}}-clinicaltrials-amendment-postmortem.md`
- Layer D CTP-LLM 흡수 (Phase 1 #2 incremental Sharpe <0.3) → `{{YYYY-MM-DD}}-clinicaltrials-amendment-ctp-llm-absorbed.md` (writeup-only, paper publishable as negative incremental)

---

## 핵심 차별화

- vs **F1 (frozen)**: same biotech event-driven pod 단 source 다름 (FDA briefing vs ClinicalTrials.gov amendment) — F1 lessons learned 4 항목 적용
- vs **β2 (frozen)**: event-driven 단 SEC vs ClinicalTrials.gov source. daemon-free 정합.
- vs **C2** (USPTO): cross-section R&D vs event biotech — orthogonal
- vs **M1** (USAspending): event-driven defense/IT vs event biotech — sector orthogonal
- vs **disclosure_decay** (advisor): direct alpha vs meta-tool
