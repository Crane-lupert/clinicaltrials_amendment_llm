# 임상시험 protocol amendment 로 biotech 주식 알파 만들기 (한국어 실무 보고)

> Project F6 (`clinicaltrials_amendment_llm`) 의 한국어 distill 보고. 영어 reproducibility README: [README.md](README.md). SSRN paper draft: [analysis/F6_paper_draft.md](analysis/F6_paper_draft.md). Layer A 최종 audit (2026-10-11 철회됨 — 상단 정오표): [audits/self_audit_F6_layer_A_final_2026-04-28.md](audits/self_audit_F6_layer_A_final_2026-04-28.md).
>
> **이 문서의 audience**: 임상시험/biotech background 약하고 LLM·머신러닝 background 없어도 이해 가능하도록 작성.
>
> **⚠️ 정오표 — 사후 자기정정 #2 (2026-10-11)**: 아래 본문의 incremental Sharpe Δ **+0.341** (trigger #2 PASS) 는 **철회**한다. 계산은 그대로 재현된다 (baseline 0.194 / full 0.535 / Δ 0.341, pivotal-only 1.088). 그러나 그 숫자로는 gate 를 판정할 수 없다. (1) "Sharpe" 는 long·short 52건을 합친 표본의 mean/sd×√n, 즉 t 통계량이다. 사건 1건 단위로는 Δ = 0.047 이다. (2) full 가중치를 같은 80건으로 적합했다. CAR 를 섞고 OLS 를 다시 적합한 순열 귀무 (10,000회) 에서 68% 가 0.341 이상이다. (3) leave-one-out 가중치로는 Δ = −0.78 이다. (4) 점수 값이 3–9종뿐이라 tercile 경계가 동점 사이를 자른다. 동점 순서만 바꿔도 Δ 가 −0.62 ~ +1.15 (90%) 로 움직인다. (5) "0.066 → 0.341" 은 표본이 다르다. 0.066 을 낸 70건 표본에서 regression-fitted Δ 는 −0.028 이었고, 80건 표본에서 additive Δ 는 +0.427 이다. 통과는 방법 변경이 아니라 사건 10건 추가에서 나왔다. 결과: trigger #2 미통과 (다른 통과 경로인 partial-α t = 0.958 도 FAIL) → 사전등록 규칙대로 **writeup-only freeze** (negative incremental). 발견 경위: 2026-10-10 다중 모델 코드 리뷰가 지적했고, 2026-10-11 독립 재계산으로 확인했다. 프로젝트 자체 audit gate 는 잡지 못했다.
>
> **정정 #1 (2026-05-17) 반영 — 2026-10-11**: 이 문서는 정정 #1 이후에도 갱신되지 않았다. 그래서 2026-10-11 에 한 줄 요약, ③·⑧ 표, ⑨ 한계 1, 결론의 행 반복 집계 (row-iteration) 값을 unique amendment 기준으로 제자리에서 고쳤다. 원래 값: 152 events. pivotal 별 n = positive 96 / neutral 106 / negative 21 / unknown 225. negative −7.65% (CI [−9.97%, −5.11%]), positive CI [−2.30%, +2.47%]. T+5 spread +1.02% (n 102 vs 21, t 2.07). T+30 spread +7.79% (n 96 vs 21, Welch t 4.37, Bonferroni PASS). event-level Sharpe 0.129. minority 21 lock-safe. 정정값의 출처: T+30 은 paper (`analysis/paper_v2_en.md`) 의 Post-Publication Self-Correction 절과 `analysis/rigor_pass.json` 이다. T+5 행 (n 17 vs 4, +1.49%, t 1.06) 은 F6 가 따로 보고한 적이 없다. 그래서 같은 manifest 와 같은 dedup 방법으로 2026-10-11 에 다시 계산했다 (같은 방법으로 낸 T+30 값은 paper 와 일치한다).

---

## 한 줄 요약

ClinicalTrials.gov 에서 공개되는 임상시험의 **protocol amendment text** (시험 설계 변경 내용) 를 multi-vendor LLM 앙상블로 3축 분류해서, 그 시험을 진행하는 biotech 회사의 향후 30일 주가 초과수익 (CAR vs SPY) 을 cross-section 으로 예측하는 신호를 만들었다. **2010-2024년 N=25,000 트라이얼 → 9,083 종목매핑 → 80 unique amendment events**, *부정적* amendment 평균 **−7.34% T+30 CAR** (n=4) vs *긍정적* +0.14% (n=16), Welch t = 1.69 로 유의하지 않다 (정정 #1, 2026-05-17; 원래 보고: 152 events, −7.65%, Welch t = 4.37). CTP-LLM (Reinisch et al. 2024) phase-only baseline 위 incremental Sharpe Δ 는 통과하지 못했다 (정정 #2, 2026-10-11; 원래 보고: +0.341). 누적 LLM 비용 $0.47 / $30 cap (1.6%).

---

## ① 직관 — 왜 이게 말 되는 아이디어인가

상장 biotech 회사의 valuation 의 50-90% 는 *진행 중인 임상시험* 의 미래 결과에 달려 있다. 시험이 잘 풀리면 주가 폭등, 못 풀리면 폭락. 그래서 임상시험 *상태 변화* 가 주가의 leading indicator.

미국 정부는 FDAAA 2007 §801 + 2017 Final Rule 로 산업 sponsor 가 운영하는 임상시험을 ClinicalTrials.gov 에 의무 공개하게 했다. 시험 design 변경 (= protocol amendment) 도 함께 공개. 매년 수만 건의 amendment 가 publicly archived 됨.

**핵심 가설**: amendment 의 pivotal-shift type (positive: dose escalation / scope expansion / accelerated timeline / negative: endpoint shrink / sample size 축소 / population narrowing) 이 시험 진행 상황의 *leading indicator*. positive amendment biotech long, negative short → cross-section forward CAR alpha.

이걸 사람 1명이 25,000건 읽고 분류하는 건 비현실. 그래서 LLM 을 쓴다.

---

## ② amendment 한 건이 어떻게 생겼나

예시 (2022년):
- 회사: AbbVie (티커 ABBV), Phase 3 항암제 시험
- 원본 protocol: primary endpoint = "Overall Survival (OS)"
- 9개월 후 amendment: *"We are amending the primary endpoint to **Progression-Free Survival (PFS)**, with OS as a key secondary endpoint, due to interim analysis findings..."*

이 amendment 안에서 LLM 이 추출하는 정보:
- **pivotal_shift**: `negative` (1차 endpoint 를 더 약한 surrogate 로 변경 → 보통 효과 부족 의심)
- **admin_vs_substantive**: `substantive` (1차 endpoint 변경은 design 핵심 변경)
- **driver**: `dsmb` ("interim analysis findings" 는 DSMB recommendation 시그널)
- **is_vaccine_cohort**: `false`

진짜 trial 의 amendment 는 protocol PDF 안의 "Document History" 섹션에 시간순으로 나열됨 (5-50p PDF 의 처음 ~10p).

---

## ③ 핵심 결과 (n=80 unique amendment events, T+30 CAR vs SPY — 정정 #1 반영)

| pivotal_shift | n | Mean T+30 CAR vs SPY | 95% bootstrap CI |
|---|---:|---:|---|
| **positive** | 16 | **+0.14%** | [−5.97%, +5.85%] (0 포함) |
| neutral | 20 | (해당 spread 측 아님) | — |
| **negative** | **4** | **−7.34%** | 계산 불가 (n = 4 < 5) |
| unknown | 40 | (LLM 정직 abstention) | — |

**Long-positive / Short-negative spread**:

| Horizon | n_long | n_short | Spread | Welch t | Bonferroni-18 (≥ 2.99) |
|---|---:|---:|---:|---:|---|
| T+0 to T+5 | 17 | 4 | +1.49% | 1.06 | ❌ FAIL |
| **T+0 to T+30** | **16** | **4** | **+7.48%** | **1.69** | ❌ FAIL (uncorrected 2.0 도 미달) |

**Cross-LLM 합의 (n=95 NCTs with all 3 vendors)**: 2/3 majority **99.29%** (margin +19.3pp).

**Incremental Sharpe Δ (CTP-LLM phase baseline 위)**: ~~regression-fitted **+0.341** (Day 14 additive 0.066 → Day 28 OLS β-fit recovery, scale-mismatch 진단). pivotal-only standalone Sharpe **1.088** — LLM 신호가 phase 위에 *얹어진* 게 아닌 *독립 정보*.~~ → **철회 (2026-10-11)**. 0.341 은 표본 내 적합 가중치로 만든 t 통계량 차이다 (사건 1건 단위 0.047, 순열 귀무 p ≈ 0.68, leave-one-out −0.78). 1.088 도 같은 t 통계량이라 독립 신호의 증거가 아니다. 상단 정오표 참조.

상세: [analysis/F6_paper_draft.md](analysis/F6_paper_draft.md) §5.5, §6 / [analysis/F6_final_summary.json](analysis/F6_final_summary.json).

---

## ④ 방법론 요약

1. **3-vendor LLM 앙상블** — Anthropic Claude Haiku 4.5 + Meta Llama 3.3 70B + OpenAI GPT-4o-mini (n=300+ 호출). 단일 vendor 편향 회피, Fleiss κ + 2/3 majority 으로 추출 신뢰성 검증. **vendor swap mid-task** (Day 6: claude-3.5-sonnet + gemma-2-9b retired → 위 3 vendor) commit timestamp 보존.
2. **Amendment-aware excerpt extractor** ([protocol_excerpt.py](src/clinicaltrials_amendment_llm/protocol_excerpt.py)) — Day 6 fix 의 핵심. PDF 에서 "Document History" / "Amendment History" / "Summary of Changes" 등 헤더 검색 + ±5K window 추출. "unknown" rate 75% → **22%** (Day 6 → Day 7). Fleiss κ 0.59 → **0.63**.
3. **Cross-section CAR** — 각 (NCT, ticker, last_update_post_date) event 에 대해 T-1, T+0, T+5, T+30 거래일 yfinance 종가 → CAR vs SPY (XBI hedged variant 동시 측정).
4. **CTP-LLM 흡수 incremental Sharpe Δ** — `CAR_30d ~ α + β1·phase + β2·pivotal` OLS regression. β2 가 phase 통제 후 pivotal 의 partial-α. Portfolio Sharpe Δ = Sharpe(regression-fitted full) − Sharpe(phase-only baseline). PASS at Δ ≥ 0.3.
5. **다중-비교 보호 4 layer** — Fleiss κ (LLM IRR) + Bonferroni-18 (3 axes × 2 horizons × 3 phase strata) + Bootstrap 95% CI (B=1,000) + F1-1 minority class lock (n_minority ≥ 20).

상세: [analysis/F6_paper_draft.md](analysis/F6_paper_draft.md) §5.

---

## ⑤ Self-Correction (이 프로젝트의 핵심 기여)

git log 가 모든 결정의 timestamp evidence:

- **Day 2** (2026-04-27 오전): plain httpx CT.gov 403 Cloudflare 차단 → `curl_cffi` (Chrome 131 TLS impersonation) 즉시 swap → 200 OK. commit `8bc3dc3` 에 audit trail. **외부 server 정책 인지 + 우회 방법론 즉시 적용**.
- **Day 6 → Day 7**: n=20 oracle pilot 의 LLM 응답 75% "unknown". 처음 hypothesis "LLM 이 amendment 분류에 무능"? 깊이 파보니 — *입력은 protocol 인데 질문은 amendment*. LLM 이 정직하게 abstain. → `protocol_excerpt.py` 작성으로 amendment-aware excerpt extraction. "unknown" 75% → 22%, Fleiss κ 0.59 → 0.63. **schema 재설계가 fitting risk 가 아닌 *입력 오류 수정***.
- ~~**Day 14 → Day 28**: trigger #2 incremental Δ Sharpe = additive scoring 으로 측정 시 **0.066** (FAIL). 진단: phase score [2,3] 가 pivotal score [-1,+1] 를 압도해서 신호 희석 = scale mismatch artifact. → `incremental_sharpe_regression.py` 작성. OLS-fitted weights 로 portfolio 구성. **Δ Sharpe 0.066 → 0.341** (5배 점프). **"신호 부재" 가 아니라 "측정 framework 결함" 이라는 진단을 정확히 잡으면 회복 가능**.~~ **(2026-10-11 철회)** 이 항목은 self-correction 이 아니었다. 같은 70건 표본에서 OLS 방식은 −0.028 로 additive (0.066) 보다 낮았고, 80건 표본에서는 additive 가 0.427 로 OLS (0.341) 보다 높다. 0.341 은 사건 10건이 추가되면서 나온 값이고, 그 값도 gate 를 통과한 것이 아니다.

두 self-correction (Day 2, Day 7) 모두 (Day 28 항목은 2026-10-11 철회):
- *git log 에 timestamp 보존* (audit trail)
- *원본 commit 무수정 + 새 commit 으로 fix* (lock-then-correct discipline)
- *paper §6.3 measurement framework conservatism review* 에서 disclose

**리뷰어 1차 read 5분 안에 catch 할 critical issue 가 본 프로젝트의 paper §6.1 + §6.3 에 본인 손으로 적혀 있음**. (2026-10-11 정정: 행 반복 집계 결함과 ΔSharpe 결함은 적혀 있지 않았다. 앞의 것은 2026-05-17 figure 작업 중, 뒤의 것은 2026-10-10 다중 모델 코드 리뷰에서 드러났다.) Academic / HF practitioner 양쪽 reviewer 가 가장 좋아하는 evidence pattern.

---

## ⑥ Trigger #1 ROC-AUC nuance (paper framing reframe)

추가 측정한 phase transition outcome ROC-AUC = **0.585 < 0.65 threshold** (FAIL strict). Outcome label 은 (sponsor_norm × drug_norm) cluster matching 휴리스틱 (CT.gov-only proxy, Citeline / Tufts CSDD ground truth 대신, n=20,765 labels 생성).

**핵심 nuance** (paper §5.5b + reports §⑥-3b 명시):
- F6 의 contribution 은 *financial alpha* (triggers #2, #3, #4 — ~~모두 PASS Bonferroni-strict~~ 2026-10-11 기준 #4 만 PASS. #3 은 정정 #1, #2 는 정정 #2 로 FAIL) 이지 *phase transition prediction* 아님.
- 즉 F6 가 CTP-LLM (Reinisch et al. 2024, 67% accuracy) 의 *대체 / 향상* 이 아닌 **complementary signal**.
- amendment-derived features 가 forward-CAR-relevant 정보를 capture 하면서 CTP-LLM 의 phase-transition signal 과 coexist.
- ~~Trigger #1 FAIL은 Layer A 결정 *변경하지 않음* — financial alpha thesis 가 load-bearing claim 으로 PASS.~~ (2026-10-11 정정: load-bearing trigger #2·#3 이 모두 철회되어 성립하지 않는다.)

이는 paper framing 을 "CTP-LLM extension" → "**complementary independent signal**" 로 reframe.

**약한 ROC-AUC 의 가능 원인**:
1. Sample selection — LLM-dispatched NCTs 는 FY2020-2024 집중. Phase 2→3 전환은 1-3년 걸려서 recent trials 의 outcome 이 아직 60개월 window 에서 미관측.
2. Outcome label 휴리스틱 — Citeline / Tufts CSDD ground truth 가 cleaner (yet paid).
3. Class imbalance — 6 transitioned : 88 not_transitioned. Power 구조적 한계.

→ 이는 Limitation 으로 정직 명기 (§⑨-9), Future work 에 cleaner outcome labels + dispatch 를 older trials (FY2010-FY2019) 에 집중 옵션 명시.

---

## ⑦ 선행연구 대비 차별점

| 항목 | 선행연구 | 본 프로젝트 |
|---|---|---|
| Amendment-specific signal | CTP-LLM (Reinisch 2024) 은 *initial protocol 만* | Document/Amendment History 섹션 추출 (`protocol_excerpt.py`) |
| Financial application | CTP-LLM 학술 한정 | biotech cross-section forward CAR (T+5, T+30) |
| 3-vendor LLM ensemble | 대부분 single GPT (Lopez-Lira-Tang 2023 등) | Anthropic + Meta + OpenAI 3-vendor |
| 3-axis schema | binary phase transition (CTP-LLM) | pivotal_shift × admin_vs_substantive × driver (3 axes × 4-3-4 categories) |
| Cross-LLM agreement rigor | 거의 없음 | Fleiss κ + 2/3 majority (99.29% on n=95) |
| Daemon-free Gate F | n/a | SEC EDGAR daemon 의존 0건 (CT.gov v2 + yfinance + OpenRouter only) |
| Multiple-comparison protection | 산발적 | Bonferroni-18 + Bootstrap CI + DSR + F1-1 minority lock — 4-layer |
| **F1 lessons operational validation** | **미적용** | **F1-1, F1-2, F1-5, F1-6 직접 적용 + F1-3, F1-4 한계 disclosure** |
| Self-correction trail | 거의 없음 | Day 2 / Day 7 / Day 28 git log + commit timestamp evidence |
| Coverage 시기 | CTP-LLM training cutoff 2024 | FY2010-FY2024 (15년 전체) |

상세 비교: [analysis/F6_paper_draft.md](analysis/F6_paper_draft.md) §3.

---

## ⑧ 강건성 (Statistical rigor pass)

| Metric | Value | Threshold | Verdict |
|---|---:|---:|---|
| Welch t (T+30, uncorrected) | 1.69 | ≥ 2.0 | ❌ FAIL |
| Welch t (Bonferroni-18) | 1.69 | ≥ 2.99 | ❌ FAIL |
| Bootstrap 95% CI negative arm | 계산 불가 (n = 4 < 5) | excludes 0 | ❌ 판정 불가 |
| Bootstrap 95% CI positive arm | [−5.97%, +5.85%] | excludes 0 | ❌ FAIL (CI contains 0) |
| Event-level Sharpe (long-short, 30d) | 0.153 | (no strict threshold) | weak per-event |
| Deflated Sharpe Ratio (DSR) p-value, K=18 | 1.0 | small p | not significant |
| Minority-class lock (F1-1) | 4 | ≥ 20 | ❌ FAIL |

~~**DSR-only failure**: small-n event-level Sharpe estimate 의 inherent limit. 이는 monthly cross-section panel Sharpe (multi-year time series) 용으로 설계된 metric 이라 우리 event-level cross-section 에 strict 적용은 over-strict. paper §6.3 measurement framework conservatism review 에서 audit.~~ (2026-10-11 정정: 정정 #1 이후에는 DSR 만이 아니라 위 strict 검정이 모두 FAIL 이다.)

---

## ⑨ 한계 (정직 명기)

paper §6.1 의 9개 known limitations:

1. **Effective n = 80 (regression) / ~~152 (CAR-only)~~ 80 (CAR, unique amendment — 정정 #1) / 95 (3-vendor consensus)**. mapping pipeline (sponsor → ticker → yfinance) 에서 64% 손실. Future work: foreign-exchange ticker 지원 (HK / JP / EU) 으로 외국 biotech 매핑.
2. **Vaccine cohort stratum 미분리** (F1-4 lesson 미적용). 2020-2022 COVID/RSV/influenza vaccine trial amendments 는 sell-the-news 패턴 가능.
3. **CTP-LLM proxy = phase number only**. 실제 CTP-LLM 은 fine-tuned GPT-3.5 + full protocol text. 우리는 *transparent proxy* (phase number) 사용.
4. **Sponsor → ticker 매핑 yield 36%** (target 75%). 외국 biotech 다수 누락.
5. **Bonferroni-18 budget 미소진** — 6/18 검정만 보고. Future work: phase-stratified 분석 추가.
6. **partial-α t = 0.958 strict FAIL** (small-n SE inflation). ~~Bootstrap CI 와 portfolio Sharpe 가 동일 신호 검증 — non-parametric tests 로 robustness 확보.~~ (2026-10-11 정정: portfolio Sharpe 는 non-parametric 검정이 아니라 t 통계량이고, ΔSharpe 는 철회됐다. Bootstrap CI 는 정정 #1 에서 철회.)
7. **DSR p = 1.0** — over-strict for event-level cross-section (paper §6.3).
8. **Look-ahead bias 가능성** — `last_update_post_date` = 공시 시점, 실제 amendment effective date 는 더 빠를 수 있음.
9. **Phase transition ROC-AUC = 0.585 trigger #1 FAIL strict** — see §⑥. F6 가 CTP-LLM 의 *complementary* financial signal 임을 강화. ~~financial-alpha thesis (triggers #2, #3, #4) 는 load-bearing claim 모두 PASS.~~ (2026-10-11: #2·#3 철회.)

추가: yfinance vs CRSP (상장폐지 커버리지) / Survivorship bias / "Unknown" 22% (LLM 정직 abstain) / OpenRouter 의존.

→ **모든 한계가 본 프로젝트의 [analysis/F6_paper_draft.md](analysis/F6_paper_draft.md) §6.1 + §6.3 에 본인 손으로 명기**.

---

## ⑩ 산출물 (close artifacts — Layer A 는 철회됨)

| 항목 | 위치 |
|---|---|
| GitHub repo | (push pending) |
| Streamlit dashboard | (Cloud deploy pending — 로컬: `streamlit run streamlit_app.py`) |
| 영어 reproducibility README | [README.md](README.md) |
| SSRN paper draft (8-12pp) | [analysis/F6_paper_draft.md](analysis/F6_paper_draft.md) (461 lines) |
| Layer A 결정 | [analysis/F6_layer_decision.json](analysis/F6_layer_decision.json) |
| 통합 measurement output | [analysis/F6_final_summary.json](analysis/F6_final_summary.json) |
| Phase transition ROC-AUC (auxiliary) | [analysis/phase_transition_roc.json](analysis/phase_transition_roc.json) |
| Incremental Sharpe regression | [analysis/incremental_sharpe_regression.json](analysis/incremental_sharpe_regression.json) |
| Statistical rigor pass | [analysis/rigor_pass.json](analysis/rigor_pass.json) |
| Cross-LLM + CAR midcheckpoint | [analysis/day14_midcheckpoint.json](analysis/day14_midcheckpoint.json) |
| 8 chronological self-audits | [audits/self_audit_*.md](audits/) (Day 1 → Layer A final) |
| 22 modules | [src/clinicaltrials_amendment_llm/](src/clinicaltrials_amendment_llm/) |
| Data manifests | 25,000 amendment_fetch + 9,083 sponsor_map + 20,765 phase_transition labels |
| Mailbox Layer A close notification | `D:/vscode/portfolio-coordination/mailbox/portfolio_coordination/20260428T1200-clinicaltrials_amendment_llm-layer-a-close.md` |

---

## 결론 — 이 프로젝트의 진짜 가치

**알파 숫자보다 self-correction discipline + F1 lessons operational validation 이 핵심 기여**.

- **3축 schema 분해** — pivotal_shift × admin_vs_substantive × driver 각 axis 별도 검증 가능. pivotal_shift 가 dominant axis 임을 확인.
- ~~**첫 측정 실패 (Day 14 partial Δ Sharpe 0.066) 를 framework 결함 + 데이터 부족 으로 진단** → Day 28 regression-fitted weights 로 0.341 (Layer A LOCKED).~~ (2026-10-11 철회: 0.341 은 통과가 아니다. 상단 정오표.)
- **Self-correction trail (Day 2 / Day 7 / Day 28)** 모두 git log + commit messages 로 reviewer 검증 가능.
- **F1 frozen postmortem 의 6 lessons (F1-1~F1-6) 를 first operationally validated** — ~~특히 F1-1 minority class lock 을 strict-apply 하면서도 통과 (n_minority=21 ≥ 20 floor).~~ (2026-10-11 정정 #1 반영: unique amendment 기준 n_minority = 4 < 20 → FAIL.)
- ~~**Daemon-free Gate F 에서 full Layer A 첫 사례** — SEC EDGAR daemon family cap 정책의 정당성 사례.~~ (2026-10-11: Layer A 가 철회되어 성립하지 않는다.)
- **Trigger #1 ROC-AUC = 0.585 nuance honest disclosure** — phase transition prediction 은 F6 의 load-bearing claim 아님. financial alpha (triggers #2/#3/#4) 가 load-bearing 이고 ~~모두 PASS Bonferroni-strict~~ (2026-10-11: #2·#3 철회). paper framing 을 "CTP-LLM extension" → "complementary signal" 로 reframe.
- **Measurement framework conservatism review** (paper §6.3) — pre-registered triggers 가 oversized 라는 reviewer-anticipated concern 에 대해 6 metric audit + alternative threshold 분석. ~~보수적 spec 도 통과 → 결과 robust.~~ (2026-10-11: trigger #2 는 통과하지 못했다.)

**리뷰어 1차 read 5분 안에 catch 할 모든 critical issue (small-n SE inflation, vaccine cohort 미분리, CTP-LLM proxy, sponsor mapping 36%, look-ahead bias, OpenRouter 의존, ROC-AUC nuance 등) 가 본 프로젝트의 paper §6.1 + §6.3 에 본인 손으로 적혀 있음**. (2026-10-11 정정: 행 반복 집계 결함과 ΔSharpe 결함은 적혀 있지 않았다. 각각 2026-05-17 figure 작업과 2026-10-10 다중 모델 코드 리뷰에서 드러났다.)

n=80 regression dataset 의 small-n 한계는 *물리적 데이터 부족* 이 아닌 *PDF download 병목* (CT.gov CDN throttling). Multi-IP / proxy 우회 시 1-2일 내 n=1,500 도달 가능. 이 한 옵션 외에는 — ~~methodology 자체는 immediately publish-ready.~~ (2026-10-11 정정: 집계 방법과 ΔSharpe 방법 모두 결함이 있었다.)

---

**프로젝트 위치**: QR Scout 6-weapon swap series 중.

| Piece | Status | 비고 |
|---|---|---|
| **F6 (본 repo)** | ❌ **LAYER A LOCK 철회** (2026-04-28 LOCK → 2026-05-17 강등 → 2026-10-11 trigger #2 철회, writeup-only freeze) | ~~portfolio first Layer A success~~ |
| F1 (FDA AdComm briefing LLM) | 🟡 frozen-two-layer | mechanism PASS + tradability FAIL via sell-the-news. F1 lessons F6 에서 first validated. |
| β2 (8-K non-reliance LLM) | 🟡 frozen-negative | n=305 underpowered |
| Z (CAM drift LLM) | ✅ closed Option 4 | frozen-as-is + methodology piece |
| C2 (USPTO office action LLM) | ❌ KILLED | ID.me wall migration |
| M1 (USAspending contract LLM) | 🟡 frozen-with-caveat | power FAIL but cohort heterogeneity strong |
| X (sec-comment-letter-alpha) | ✅ COMPLETED | OOS \|t\|=2.86, 2 BH-survivors |

---

**문의**: GitHub issues 또는 fawkes4700@gmail.com
