---
name: abandon-criteria
description: 매 phase 시작 시 go 기준뿐 아니라 kill 기준 (abandon triggers) 을 최소 3개 명시적으로 선언하여, 프로젝트가 sunk-cost 로 연장되는 것을 차단한다. phase 진행 중 trigger 발화 여부를 모니터링하고, 발화 시 즉시 중단. v1.2 (2026-04-27): project-type-aware trigger selection (§3.5) — discovery-form vs functional-form vs hybrid 별 trigger archetype 분리.
license: MIT
version: 1.2.0
---

# Abandon Criteria

> 연구/프로덕트 프로젝트에서 Phase 를 거치며 go 기준 (이 신호 이상이면 진행) 은 보통 명시되지만, **kill 기준 (이 신호 이하면 중단)** 은 생략되기 쉽다. 그 결과 Phase 0→1→2→2.5 로 sunk cost 가 누적되고, 근본 premise 재질문은 외부 pressure 없이는 발생하지 않는다.
>
> 근거:
> - [audits/2026-04-25-mirosalmon-abandon-retrospective.md](../../audits/2026-04-25-mirosalmon-abandon-retrospective.md) §4.6 — output drift 실패
> - [audits/2026-04-26-activist-intent-llm-killed-postmortem.md](../../audits/2026-04-26-activist-intent-llm-killed-postmortem.md) — input drift 실패 (framework gap → data-validity category 추가)

## 언제 사용하는가

- **매 Phase 설계 직후, 실행 직전** 필수 invoke
- Pivot 제안 직전 — 새 방향의 abandon 기준도 같이 선언
- reference validation checklist 통과 직후 Phase 0 진입 전

## 선언 규칙

### 1. 최소 수량
Phase 당 **3개 이상**. 적으면 "실패 좁게 정의" 오류.

### 2. 각 trigger 는 아래 4요소 필수
```
1. Trigger name: 
2. Measurable condition (숫자 임계 or binary event): 
3. Data source (어디서 확인): 
4. On-fire action: 즉시 중단 / 교정 phase / scope 축소 / pivot
```

### 3. Trigger 유형 분배 (권장: 4 category 각 ≥ 1)
- **Mechanism trigger** 최소 1개: p-value / effect size / accuracy 같은 내부 지표
- **Product/market trigger** 최소 1개: user interview 결과, reference 사망, market 경쟁자 출현
- **Resource trigger** 최소 1개: 토큰 예산 초과, timeline 초과, attention 초과
- **Data-validity trigger** 최소 1개: input 자료의 가용성/품질 (sample 미달, rater 미확보, pipeline coverage 미달). output trigger 와 별개 — output 평가가 가능하기 *전* 발화 가능해야 함. (Y 2026-04-26 retrospective 후 추가)

### 3.5 Project-type-aware trigger selection (2026-04-27 신설, v1.2)

> 근거: [audits/2026-04-27-project-type-calibration-disclosure-decay-meta-tool.md](../../audits/2026-04-27-project-type-calibration-disclosure-decay-meta-tool.md). disclosure_decay_meta_tool Day 10/13 mechanical fire 가 spec mismatch 였음을 확인.

§3 의 trigger archetype 은 project-type 에 따라 다르게 선택한다 — 분류는 [templates/reference-validation-checklist.md §0.5](../../templates/reference-validation-checklist.md) 에서 수행.

- **Discovery-form 프로젝트**: 위 §3 의 4-category 그대로. Mechanism trigger 는 phenomenon-existence (Welch p / Sharpe / Fleiss κ / R²). 예: X / Y / Z / β2 / Factor / α / F1 / C2.
- **Functional-form 프로젝트**: Mechanism trigger 가 *tool actionability* 형태로 변형 — output differentiation / recommendation reproducibility / layer utility. **Phenomenon-existence trigger 는 upstream-verified component 에 적용 금지** (해당 phenomenon 은 이미 검증됐으므로 우리 trigger 가 발화하면 *우리* 데이터-handling 버그 means, not phenomenon 부재). [templates §4.6](../../templates/reference-validation-checklist.md) catalog 에서 ≥3 추출. 예: disclosure_decay_meta_tool 본체, quant-research-process.
- **Hybrid**: sub-task 별 분리 — discovery sub-task 는 §3 archetype, functional 본체는 §4.6. 예: disclosure_decay_meta_tool 의 LLM ensemble generalization sub-task 는 discovery (Fleiss κ ≥ 0.6 적용), 나머지 cohort matching + NPV calculator 는 functional.

연동: `docs/portfolio-research-rules.md` Gate G + `templates/reference-validation-checklist.md` §0.5 / §4.6.

### 4. 금지 항목
- "결과가 안 좋으면 중단" 같은 subjective trigger 금지. 숫자나 binary event 로만.
- "충분히 해 보고 판단" 금지. trigger 는 선언 시점에 측정 가능해야 한다.
- "다음 phase 에서 재평가" 금지. trigger 는 **현 phase 내** 발화 가능해야 한다.
- **Functional-form 프로젝트의 phenomenon-existence trigger 금지** (위 §3.5). Hybrid 의 discovery sub-task 한정으로만 허용.

## Trigger 카탈로그 (카피 시작점)

### Mechanism triggers
- "effect size < X 에서 n=Y 이상 누적 관측 시 중단"
- "critical metric 의 p > 0.1 에서 Bonferroni 보정 후에도 유의하지 않으면 중단"
- "cross-LLM replication 2개 모델 중 1개라도 실패 시 중단"
- "baseline 이 우리 model 을 능가하면 (단일 조건 아닌 majority) 중단"

### Product/market triggers
- "reference 가 N 주 내 1개 이상의 negative signal 발생 (funding 철회, pivot 발표, 경쟁자 인수 등)"
- "customer interview 에서 '이 문제 해결에 지불 의사 없음' 답변 3/3"
- "경쟁자가 동일 product 를 더 빠르게 출시"
- "regulation/legal 환경 변화로 core assumption 무효화"

### Resource triggers
- "LLM 토큰 예산 $X 초과"
- "human-time N 일 초과"
- "특정 dependency 제거 불가능한 blocker 발견"
- "attention quality 2 세션 연속 저하"

### Data-validity triggers
- "Phase 0 EOD 까지 fetched sample < N" (sample availability — Y 가 이 trigger 사전 등록 안 함)
- "n=N pilot 에서 inter-rater κ < 0.6 또는 single-rater only" (rater methodology — multi-rater 미확보 자체가 trigger)
- "Week W EOD 까지 end-to-end pipeline coverage < X%" (예: CAR computable / output extractable 비율)
- "Critical input data source 의 deprecation / access loss"
- "Domain expert (labeler / annotator) 확보 실패 by deadline"
- "공유 daemon / queue 의 priority 미공개 + capacity probe 미달"

## Phase 감사 통합

모든 phase 감사 문서에 아래 섹션 포함:

```markdown
## Abandon Criteria (선언 + 점검)

### 선언된 triggers (phase 시작 시)
1. Trigger: {name}
   - Category: mechanism / product-market / resource / data-validity
   - Condition: 
   - Source: 
   - Action: 
2. ...
3. ...

### 이번 phase 중 trigger 발화 check
- [ ] Trigger 1 발화: Y / N. Y 면 증거: 
- [ ] Trigger 2 발화: Y / N. 
- [ ] Trigger 3 발화: Y / N.

### 발화 시 조치 실행 여부
- 실행했는가: [ ] Y / [ ] N
- 안 했다면 이유 (sunk cost rationalize 주의): 
```

## 조기 감지 의무

Trigger 발화는 **부정적** 이 아니라 **정보**. 발화했는데도 "그래도 한 번 더" 는 sunk cost 확장. MiroSalmon 에서 반복된 패턴.

- 발화 시 다음 phase 진입 금지
- 중단 / 교정 / pivot 중 **즉시** 선택
- 교정 시에도 새 phase 는 새 abandon criteria 선언 필수

또한 **trigger 가 발화 안 했어도** input 단계 (data validity) 가 깨졌다면 중단/scope 축소 고려. Y 사례: 5 trigger 중 mechanical 발화 0 이지만 sample/rater/coverage 셋 동시 위반으로 결과 평가 자체 무의미 — output-layer trigger 의 사각지대.

## 설치

- 이 파일: `d:\vscode\meta-harness\skills\abandon-criteria\SKILL.md`
- 신규 repo 에 `<repo>/.claude/skills/abandon-criteria/SKILL.md` 로 복사
- `templates/reference-validation-checklist.md` §4 (Phase 별 abandon criteria) + §4.5 (data validity contracts) 와 연동

## Worked Examples

### ✅ 성공 사례 — sin-controversy-pilot (Project α, 2026-04-25)
2일 sacrificial pilot. CLAUDE.md 작성 시점에 단일 metric kill gate 사전 등록:
"in-sample Sharpe > 0.3 → 생존, ≤ 0.3 → 즉시 폐기". n=43 firms · 95 months 측정 결과
Sharpe = -0.490 (가설 부호 반대). **48h 내** 폐기 결정 + ABANDONED.md 작성 + agent 해제.
sign-flip / 조건 변경 / scope 확장 유혹 차단됨.
- 효과 요인:
  - 단일 metric (Sharpe) → 발화 여부 binary
  - 사전 통계적 정당화 ("Sharpe 0.3 미달 시 OOS 검정력 거의 없음")
  - 통과/폐기 양 경로의 산출물 사전 명시 (Y appendix merge / ABANDONED.md retrospective)
  - timebox (2 일) 가 sunk-cost 누적 자체를 차단
- retrospective: `audits/2026-04-25-sin-controversy-pilot-abandon-retrospective.md`

### ❌ 실패 사례 (output drift) — mirosalmon (2026-04-25 retrospective)
Phase 0 → 0.5 → 1 → 2 → 2.5 까지 11일 누적. Go 기준은 명시됐지만 Kill 기준 약함.
Phase 0 말 Stage 3 시점에 "이 결과가 product-valuable 한가?" 질문이 발화돼야 했지만
sunk-cost 합리화로 한 단계씩 더. 결과적으로 thesis 근본 오류는 phase 2.5 에 가서야 표면화.
- retrospective: `audits/2026-04-25-mirosalmon-abandon-retrospective.md` §4.6

### ❌ 실패 사례 (input drift / framework gap) — activist-intent-llm (Project Y, 2026-04-26)
18 시간 single-burst execution. CLAUDE.md 에 abandon criteria 5개 선언했으나 모두 *output
layer*: n<3000, κ<0.5, CI∋0+regime null, budget>$25, short-side infeasible. 실제 실패는
*input layer* — sample availability (20K → 257 = 1.3%), rater methodology (single
non-expert labeler κ=0.52 vs 0.7 target), CAR coverage (100% → 25%). 셋 다 발화 안 한 이유:
선언된 trigger 가 *결과 평가 시점* (κ < 0.5 / CI / regime null) 또는 *절대값 floor* (n<3000)
이라 *target 으로부터의 gap* + *input prerequisite* 을 못 잡음. n=257 < 3000 인데도 "Day 2
EOD" 평가 시점이 모호해 명시 발화 X, κ=0.52 ≥ 0.5 라 #2 발화 X.

- 교훈: data-validity trigger 가 abandon criteria 의 별도 category 여야 함 (위 §3 분배에
  추가됨). Y 는 framework 의 필요 조건 검증 사례 — 사전 등록한 trigger 만으로는 input
  invalidation 사각지대 발생.
- retrospective: `audits/2026-04-26-activist-intent-llm-killed-postmortem.md`

### ⚠️ Mid-success negative result — eight_k_non_reliance_llm (β2, 2026-04-27)

Phase 0 4-AND gate 모든 trigger PASS (schema 객관성 mechanical 검증, error_type κ 0.89 ×
3-vendor + 100% cross-LLM majority + KL 0.019). Phase 1 진입 후 §1 trigger #2 mechanical
fire — `|Δ|=210bp` 부호 정합 (Hennes-Leone-Miller 1.14× asymmetry direction OK) but
`|t|=0.567 ≪ Bonferroni-9 critical 2.773` (4.9× miss) → CLAUDE.md spec C-strict path
"negative result writeup, repo freeze". sin-pilot 패턴 (Project α) 의 alpha-research 영역
일반화 입증의 두 번째 사례 (Z 후속).

Y kill 과 다른 pattern:

| | Y (killed) | β2 (frozen-negative) |
|---|---|---|
| Trigger 발화 | input invalidation (sample 1.3% / κ=0.52 / coverage 25%) — 사전 등록 5 trigger 모두 output-layer 라 mechanical fire X | output statistical insignificance after methodology validation PASS — output-layer trigger #2 mechanical fire ✓ |
| Fail layer | input | output (sample power) |
| Path | ABANDONED.md + retrospective | negative result paper (PAPER.md 8-12p) + repo freeze + 5분 demo |
| Recovery 조건 | 없음 (re-design 필요) | CRSP-licensed replication (expected n ≈ 7,400-9,000 → recover) |
| 학술 기여 | postmortem audit (input invalidation framework) | negative result paper + reusable methodology (multi-vendor LLM ensemble framework + schema validation + KL + survivorship quantification) |
| 인터뷰 demo 가능 | 없음 (failure 자체가 evidence) | 5분 demo + paper + 12 timestamped audits |

추가 lesson — Sample power pre-registration gap:
- β2 trigger spec: `|Δ| < 100bp OR |t| < 2.0 (Bonferroni-9)` — 사후 metric threshold 만 명시.
- 가용 sample (free-tier yfinance 30% × 8,811 cached × 19.7% subset) → n=305 으로
  required n_min ≈ 7,400 의 4% 만 확보. **사전 측정 가능했지만 spec 안 했음**.
- 권고: trigger 가 t-stat / Sharpe / DSR 등 sample-size-dependent metric 을 쓸 때
  required n_min 사전 등록 + data environment 의 effective n 사전 검증 의무.
- 연동: `docs/portfolio-research-rules.md` Gate H (2026-04-27 신설).

추가 lesson — Robustness spec 의 t-stat 의무:
- β2 Day 16-18 held-out subset 의 misleading PASS (sign + magnitude_ratio 7.72 → spec PASS,
  but n=23 net_income subset 의 +21.42% mean 이 outlier-dominated, |t|=-1.35 < Bonferroni-9
  critical → 실제로는 noise).
- 권고: 모든 held-out subset robustness 검정에 `|t| ≥ Bonferroni` term 추가 의무.

교훈 종합: trigger 발화는 *정보*. abandon vs frozen-negative 구분은 *fail layer + recovery
조건* 에 따라 결정. Negative result 도 academic 가치 있음 — 단 *pre-registered* trigger
mechanical fire + audit trail 동반 시. β2 는 21-day plan 을 ~3시간 wall-clock 으로 compress
(4-rule async workflow) + 12 timestamped self-audits + $2.06 cost (cap 의 8.2%) 로 portfolio
discipline 입증.

- retrospective: `audits/2026-04-27-eight-k-non-reliance-frozen-postmortem.md`
- 외부 deliverable: `reports/2026-04-27-eight-k-non-reliance-llm-postmortem.md`

### ✅ Project-type calibration 사례 — disclosure-decay-meta-tool (2026-04-27)

v1 reference-validation 작성 시 sub-agent 가 QR Scout 표준 (discovery-form) trigger 를
functional-form repo 에 그대로 적용 → 두 건의 mechanical fire:

- **Day 10 #3 (hyperbolic α(t)=K/(1+λt) R² ≥ 0.3)**: R² 0.046–0.131 STRICT FAIL.
  진단: arxiv 2512.11913 의 short-horizon crowding 모델을 long-horizon
  publication-decay 에 over-apply 한 spec error. Welch p=0.003 로 phenomenon
  자체는 verified — wrong model form, not absent phenomenon. **Drop from gate
  set → exploratory only.**
- **Day 13 #2 (PnL-vs-LLM Pearson ρ ≥ 0.3)**: max ARI 0.11 / NMI 0.23 / phi 0.11
  STRICT FAIL. 진단: PnL cluster (HOW) ≠ LLM mechanism (WHY) — 두 layer 가 같은
  것을 측정한다고 가정한 것이 spec error. Orthogonality 가 feature, not bug.
  **Reposition as functional gate "F2 PnL layer utility"**: PnL similarity layer 가
  ≥1 downstream functional component (NPV capacity haircut, dashboard
  orthogonality page) 에 non-trivial 변동을 공급하면 PASS. → PASS.

사용자 진단으로 project-type mismatch 표면화. v1.2 가 spec 분리 + 본 레포는
functional-form 으로 재정의 + 7 trigger 중 #1/#2/#3 재분류 (#1 sanity gate /
#2 reposition F2 / #3 dropped → exploratory) → **fire count 0/12 corrected**.

대비 포인트:
| | discovery-form (잘못 적용) | functional-form (정정) |
|---|---|---|
| Trigger #2 fire 조건 | ρ < 0.3 (phenomenon agreement) | layer utility (downstream consumer 존재) |
| Trigger #3 fire 조건 | hyperbolic R² < 0.3 (model fit) | dropped (exploratory only) |
| 발화 시 결정 | scope 축소 또는 kill | spec 보정 + 진행 |
| 근본 원인 | template 의 implicit discovery-only 가정 | type 명시 의무 (§0.5) + functional catalog (§4.6) |

retrospective: `D:\vscode\disclosure_decay_meta_tool\audits\project_type_calibration_2026-04-27.md` (source) /
`audits/2026-04-27-project-type-calibration-disclosure-decay-meta-tool.md` (meta-side handover)

대비 포인트 (전체):
| | sin-controversy-pilot | mirosalmon | activist-intent-llm (Y) | disclosure-decay-meta-tool |
|---|---|---|---|---|
| Kill 기준 사전 명시 | 단일 metric, 숫자 임계 | 약하게 정의 | 5 trigger, 모두 output-layer | 7 trigger, 2개 type-mismatch |
| Project type | discovery (sacrificial) | discovery (research) | discovery (alpha) | **functional + 1 discovery sub-task** |
| Timebox | 2 일 hard | 없음 (phase-by-phase) | 2 weeks scope, 18h burst | 21-day Phase 1 |
| 실제 실패 layer | output (Sharpe sign-flip) | product thesis (reference) | input (data validity) | **spec mismatch (template gap)** |
| 발화 메커니즘 | 사전 등록 mechanical 발화 | sunk-cost 합리화 누적 | mechanical 발화 X (output 사각지대) | mechanical 발화 ✓ but spec 자체가 mis-fit |
| 발화 시 행동 | 즉시 폐기 + ABANDONED.md | "한 번 더" 합리화 누적 | meta-harness 외부 트리거로 kill | type-aware spec 정정 + 진행 (사용자 진단) |
| 결과 | abandon framework 시연 성공 | 11일 + $25 sunk | framework gap (data-validity 추가) | framework gap (project-type 추가) |

### ⚠️ Mid-success two-layer result — fda_adcomm_briefing_llm (F1, 2026-04-27)

Phase 0 6-AND gate 통과 (4-axis κ=0.21 FAIL → §4 fallback 으로 2-axis κ=0.6731 PASS, scope-reduced
178<200 fetch acceptance 등). Phase 1 진입 후 **trigger 다층 발화** — portfolio first
**mechanism PASS + tradability FAIL** 카테고리:

- **Phase 1 #1 (vote prediction ROC-AUC ≥ 0.65)**: **PASS** at 0.7222 (n=11). LLM concern
  density 라벨이 vote outcome 정보 carry. Mechanism layer 작동.
- **Phase 1 #2 (CAR spread t ≥ 2.0)**: **FIRE with directional REVERSAL** — t=−1.372,
  spread −7.81% (XBI-hedged), thesis 정반대. CLAUDE.md spec C-strict path 자동 진입.
- **Phase 1 #7 (final analyzable n ≥ 300)**: **FIRE** — n=28 (CAR) / n=11 (vote), 10×/27× miss.

진단: **briefing-day CAR 는 absolute concern level 이 아니라 *surprise-relative-to-expectation* 이
결정**. low-concern 7 cluster 중 3개 (PFE Comirnaty 2020-12-10, MRNA 2020-12-17, NVAX
2022-06-07) 이 textbook sell-the-news (사전 200-500% runup → briefing 공개 = 차익실현 매도).

| | β2 (frozen-negative) | F1 (frozen-two-layer) |
|---|---|---|
| Trigger 발화 | output statistical insignificance (#2 fire, mechanism layer fail) | mechanism PASS (#1) + tradability FAIL (#2 reversal) + sample power FAIL (#7) |
| Fail layer | output (sample power) | **mixed — tradability + sample power, mechanism intact** |
| Path | negative result paper + repo freeze | two-layer paper + repo freeze |
| Recovery 조건 | CRSP-licensed replication (n recovery) | F2 expectation-prior layer (analyst consensus / options IV / prior runup) — absolute → surprise 변환 |
| 학술 기여 | negative result + LLM ensemble methodology | **mechanism PASS + tradability FAIL + sell-the-news 패턴 정량화** (COVID 백신 cohort) |
| 인터뷰 demo | 5분 + paper + 12 audits | 9-section writeup + dashboard + 12 audits |

추가 lesson — **Gate H retroactive evidence (Lesson F1-2)**:
- F1 reference-validation §4.5.1 sample availability contract 는 fetch 상한 480 events 등록.
  단 *post-LLM-classification × vote-match × ticker-map effective n* 의 power-curve 사전 계산 누락.
- 178 briefings × 21% LLM-drug yield × 30-name ticker dict × 50-entry HISTORICAL_OUTCOMES strict
  match → effective 11-28 events. Required `n_min ≈ 1,800` for `|Δ|=700bp at Bonferroni-12
  critical 2.96`. **사전 측정 가능했음** — Gate H 가 *등록되어 있었음에도* F1 launch 시 적용 누락
  (meta-harness governance gap).
- 권고: reference-validation 통과 조건에 effective-n 역산 명시 의무 (`docs/portfolio-research-rules.md`
  §5 Gate H 강화).

추가 lesson — **Partial-dispatch lock-and-revise (Lesson F1-1)**:
- 부분 dispatch (~56%) 시점 commits `e5214a3` + `cc2802c` 에 trigger #1 ROC-AUC=0.50 (n_intersection=2)
  기준 FIRE 표명 → 1-2시간 후 full dispatch (commit `df30130`) 결과 0.7222 (n_intersection=11)
  로 회복 + tentative-label 정정.
- 원인: minority-class (low-concern) 표본 너무 작아 vote-intersection 1-2개 → ROC-AUC 의미
  없음. Full dispatch 후 86%/14% 분포에서 정상 작동.
- 권고: label-distribution-sensitive metric (ROC-AUC / κ / confusion matrix) 의 trigger
  evaluation 은 dispatch ≥95% 또는 minority-class n ≥ 20 도달 후. 부분 dispatch 의 fire 는
  자동 lock 금지 — *tentative* 라벨링.

교훈 종합: **mechanism PASS + tradability FAIL** 은 portfolio 의 새 카테고리 (Y/Z/β2 flat null
외). regulator-mandated text 의 absolute LLM classifier 단독은 surprise-relative-to-expectation
을 못 잡음 — 다음 event-driven biotech weapon 은 expectation-prior layer 의무 (analyst consensus
/ options IV / prior price runup).

- retrospective: `audits/2026-04-27-fda-adcomm-frozen-postmortem.md`
- 외부 deliverable: `reports/2026-04-27-fda-adcomm-postmortem.md`

## 관련

- `templates/reference-validation-checklist.md` §4, §4.5
- `skills/drift-watchdog/SKILL.md` — Rule 24 (drift 2x 자동 교정 phase) 과 결합
- `audits/2026-04-25-mirosalmon-abandon-retrospective.md` §4.6 — output drift 실패
- `audits/2026-04-26-activist-intent-llm-killed-postmortem.md` — input drift 실패 + framework gap
- `audits/2026-04-25-sin-controversy-pilot-abandon-retrospective.md` — 성공 사례
- `docs/principles.md` §6.8 (Data Validity Contracts)
