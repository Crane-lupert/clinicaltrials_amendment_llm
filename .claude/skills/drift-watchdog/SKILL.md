---
name: drift-watchdog
description: Research/product 프로젝트가 Phase 를 진행하면서 원래 product 정의로부터 scope/scale/metric 이 점진 이탈하는 것을 시스템적으로 감지하고 차단한다. MiroSalmon 사태에서 도출된 Rule 21-26 의 운영 skill 형태. 매 phase 감사 시작 시 invoke.
license: MIT
version: 1.0.0
---

# Drift Watchdog

> 모든 실험/연구 project 는 Phase 를 거치며 원 정의에서 조용히 멀어진다. 매 phase 끝날 때는 "이번 결과로부터 다음 단계 설계" 로 사고가 쏠려서 **원 정의 re-anchor 가 0회** 가 되기 쉽다. 이 skill 은 그 구조적 약점을 시스템적으로 counteract 한다.
>
> 근거: [audits/2026-04-25-mirosalmon-abandon-retrospective.md](../../audits/2026-04-25-mirosalmon-abandon-retrospective.md) §4. MiroSalmon 은 원 정의가 "N=1000 agents × 수년 timeline × 집단 현상" 이었으나 실제는 n=30 × mechanism metric 만 측정. scale 전체 3%. drift 실시간 감지 실패.

## 언제 사용하는가

- **매 phase 감사 문서 작성 시 필수 invoke** (audit template §Drift-watchdog 섹션)
- 새 Phase 설계 직전
- "이번 결과 좋네, 다음 실험은..." 으로 논의가 옮겨가려 할 때 **먼저**
- session 시작 시 (Rule 25 — Claude 가 priming 없이 시작하는 특성)
- Pivot 제안이 나왔을 때

## Rule Set (Rule 21-26, MiroSalmon 산출물)

### Rule 21 — Product-vision anchoring
매 phase 시작·종료 시 **원 product 정의 문서** 를 재읽는다. 재읽지 않은 phase 는 drift 축적 기본값이다.

- **How to apply**: 감사 문서 §1 에 "원 정의 요약 (변경 금지 원본 인용)" 필수 섹션. 요약이 원본과 다르면 drift 증거.

### Rule 22 — Mechanism vs Product metric 강제 분류
모든 metric 을 **mechanism** (p-value, effect size, accuracy, BLEU) 또는 **product** (user action, retention, revenue, ship/abandon decision) 둘 중 하나로 명시 label.

- **How to apply**: 결과 테이블 각 행에 `type: mechanism | product` column 강제. mechanism 결과 만으로 product claim 금지.

### Rule 23 — Scale check
원 정의의 scale 대비 현재 실제 scale 비율 계산. 10% 미만이면 "product-level emergence 증명" 주장 금지.

- **How to apply**: 감사 문서 §2 에 
  - 원 정의 scale: N=__
  - 현재 실행 scale: n=__
  - 비율: __% 
  - 명시 행 필수. 10% 이하면 mechanism-only 주장 강제.

### Rule 24 — Drift watchdog (자동 교정 phase)
scale/scope/metric 의 변화가 **누적 2x** 이상이면 자동 교정 phase 를 강제 삽입. "원 정의로 돌아가기" 또는 "정의 공식 수정 + 재서명" 중 하나.

- **How to apply**: 
  - scale 2x 변화 예: 원래 agents=1000 → 실제 n=5 (200x 축소, 트리거)
  - scope 2x 변화 예: "시간 누적 학습" → "counterfactual specificity" (도메인 이동)
  - metric 2x 변화 예: product metric → mechanism metric 으로 교체
  - 트리거 발화 시 다음 phase 진입 전 교정 감사 필수.

### Rule 25 — 세션 재각인
새 Claude 세션 (또는 long gap 후 재개) 시작 시 **원 product 정의 + 직전 phase 결과 + 다음 phase 설계** 3자를 함께 재로드. Claude 는 직전 대화로 priming 되지 않는다.

- **How to apply**: session 시작 시 첫 read 3종:
  1. `CLAUDE.md` (또는 project 정의 문서)
  2. 최신 phase 감사 문서
  3. reference-validation-checklist 결과

### Rule 26 — stat ≠ product 주기 확인
"p=10⁻¹² 이면 증명됨" 가정 금지. 통계 유의성 ≠ 제품 가치.

- **How to apply**: product claim 을 할 때 "이 metric 이 변하면 사용자 행동이 실제로 바뀌는가?" 답 없으면 claim 철회.

## Phase 감사 통합 (template 섹션)

모든 phase 감사 문서에 아래 섹션을 포함한다 (audit `_TEMPLATE.md` 참조):

```markdown
## Drift-Watchdog Check

### Rule 21 (vision anchoring)
- 원 정의 문서 경로: 
- 이번 phase 시작 시 재읽음: [ ] Y / [ ] N
- 원 정의 vs 현 실행 차이: 

### Rule 22 (metric type)
- 이번 phase metric: 
- type: mechanism / product
- product claim 을 했다면 product metric 로 뒷받침됐는가? 

### Rule 23 (scale)
- 원 정의 scale: N=
- 현 scale: n=
- 비율: __%
- 10% 미만이면 mechanism-only 주장 강제됐는가? [ ] Y

### Rule 24 (drift trigger)
- scale 2x 변화: [ ] Y / [ ] N
- scope 2x 변화: [ ] Y / [ ] N
- metric 2x 변화: [ ] Y / [ ] N
- 하나라도 Y 면 교정 phase 삽입 결정: 

### Rule 25 (session re-anchor)
- 세션 시작 시 3종 재로드 완료: [ ] Y

### Rule 26 (stat vs product)
- stat 유의성 → product claim 점프 있었는가: [ ] Y / [ ] N
- Y 면 철회 조치: 
```

## 설치

- 이 파일은 `d:\vscode\meta-harness\skills\drift-watchdog\SKILL.md` 에 위치.
- 신규 research/product repo 생성 시 `<repo>/.claude/skills/drift-watchdog/SKILL.md` 로 복사 OR `@import` 로 reference.
- audit `_TEMPLATE.md` 에 위 Phase 감사 통합 블록이 포함돼야 한다.

## Worked Examples

### ✅ Day-by-Day audit pattern — eight_k_non_reliance_llm (β2, 2026-04-27)

β2 21-day Phase 0+1 plan 의 12 timestamped self-audits (`audits/self_audit_*_YYYYMMDDTHHMM.md`):

```
Day 1   self_audit_day1_eod_20260427T0010.md
Day 2   self_audit_smoke_test / first_batch_yield / search_route_yield / fleiss_kappa / uncertainty_binary
Day 3   self_audit_extended_kappa_n40 / phase0_to_phase1_transition / correction_held_out
Day 10  self_audit_day10_12_compute_car
Day 11  self_audit_day10_12_retry_optionA
Day 13  self_audit_day6_15_classify_asymmetry
Day 16  self_audit_day16_18_robustness
Day 19  self_audit_day19_20_paper
Day 21  self_audit_phase1_final_retrospect
```

각 day 의 verification task 후 self-audit 의무 (memory rule). **drift 누적 0건** — 모든
deviation 즉시 self-audit + 사용자 보고 + commit:

- **held-out 측정 오류 자가-catch (commit `0c9432a`)**: Day 3 Phase 0→1 transition 직후
  "all 8-K count" → "4.02-verified count" stratification 정정. held-out 2,423 → 364.
  *PASS 잘못 보고 → coord cross-check 후 정정* 의 정직 트레일.
- **trigger #1 fail (Day 10-12, commit `9b51570` + `6585ca2`)**: SchroderJ baseline replication
  envelope 미달 즉시 self-audit + Yahoo fuzzy fallback (Option A) 1회 시도 + +24bp shift
  측정 + 미달 인정 + Phase 1 진행.
- **trigger #2 fail (Day 13-15, commit `70ee07d`)**: cross-section asymmetry test |t|=0.57
  ≪ Bonferroni-9 critical 즉시 self-audit + C-strict path "negative result writeup, repo
  freeze" 자동 진입 — sunk-cost 합리화 0건.

대비 — Y (activist-intent-llm, 2026-04-26 abandoned) 의 18-hour single-burst 패턴:
| | Y (18h burst) | β2 (Day-by-Day) |
|---|---|---|
| Self-audit count | 1 (postmortem only) | 12 (timestamped) |
| Deviation 인지 시점 | 18h 후 | 즉시 (각 day) |
| Drift 누적 | sample 1.3% / κ=0.52 / coverage 25% 동시 | 0건 |
| Trigger 작동 | mechanical fire X | mechanical fire ✓ (#1, #2) |
| Sunk cost | 18h + $3.25 | ~3h wall-clock + $2.06 |

**핵심 패턴**: **micro-feedback loops** (≤1 day cadence) 가 drift 차단. session-끝
self-audit + commit 의무 + 사용자 보고 의무 — 세 lock 이 결합되면 18h-burst 같은
silent drift 부재.

연동:
- `skills/abandon-criteria/SKILL.md` Worked Example §β2 — mechanical kill trigger 작동.
- `audits/2026-04-27-eight-k-non-reliance-frozen-postmortem.md` §6.2 (self-audit timestamped
  trail) + §9 Lesson β2-6.

### ✅ Partial-dispatch lock-and-revise self-correction — fda_adcomm_briefing_llm (F1, 2026-04-27)

F1 의 Phase 1 streaming dispatch (145 briefings × 3 vendors = 435 LLM calls, long-running
background process) 중 ~56% partial 시점 commits `e5214a3` + `cc2802c` 가 trigger #1
(vote prediction ROC-AUC ≥ 0.65) FIRE 표명 — ROC-AUC=0.50 (n_intersection=2). 1-2시간 후
full dispatch (commit `df30130`) 후 ROC-AUC=0.7222 (n_intersection=11) 로 PASS 회복.

원인 진단:
- partial dispatch 시점 concern_density 분포가 ~95% high / ~5% low 극단 skew → low-concern
  표본 너무 작아 vote-intersection 1-2개로 제한 → ROC-AUC 의미 없음.
- full dispatch 후 86%/14% 분포 균형 복귀 — Mechanism layer 정상 작동.

self-correction trail (drift-watchdog 작동 evidence):
- 부분 dispatch fire commits 의 audit (`cc2802c`) 가 Day 11+ 정식 trigger fire 로 기록.
- full dispatch 후 frozen postmortem (`df30130`) 가 audit-trail 정직 명기 — partial 시점 결론
  lock 의 잘못 + tentative-label 권고.
- postmortem (`reports/2026-04-27-fda-adcomm-postmortem.md`) + memory note 모두 full-dispatch
  결과 reflecting two-layer framing 으로 갱신.

대비 — β2 single-batch dispatch 와 차이:
| | β2 (Day-by-Day single-batch) | F1 (streaming long-running) |
|---|---|---|
| Dispatch pattern | record-level parallelism + counting semaphore (한 번에 batch) | streaming background long-running (>30 min) |
| Trigger evaluation 시점 | batch 완료 즉시 | partial 시점 lock 위험 |
| drift 위험 | 낮음 (batch atomic) | 높음 (label-distribution skew time-varying) |
| F1 specific lesson | — | partial-dispatch 의 trigger fire 는 *tentative* lock 금지 |

**핵심 패턴**: streaming dispatch (>30 min long-running) 의 경우 label-distribution-sensitive
metric (ROC-AUC / κ / confusion matrix) 의 trigger evaluation 은 *완료 알림 후* 시행 의무.
부분 dispatch 의 fire 는 자동 lock 금지 — *tentative* 라벨링 + minority-class n ≥ 20 도달
또는 dispatch ≥95% 후 재평가.

연동:
- `templates/llm-event-study-CLAUDE.md.template` §1 강제 규칙 11 (partial-dispatch tentative)
  + §1 강제 규칙 13 (streaming dispatch trigger evaluation rule).
- `skills/abandon-criteria/SKILL.md` Worked Example §F1 (mid-success two-layer + Lesson F1-1).
- `audits/2026-04-27-fda-adcomm-frozen-postmortem.md` §3.3 (interim mistake) + §9 Lesson F1-1.

### ❌ 18-hour single-burst — activist-intent-llm (Y, 2026-04-26)

기존 abandon 사례. drift-watchdog 의 micro-feedback loop 부재 → 18h 안에 sample / rater /
coverage 셋 동시 drift 누적 → output-layer trigger 사각지대 발생. β2 Day-by-Day 패턴이
정반대 — 비교가 lesson 의 핵심.

retrospective: `audits/2026-04-26-activist-intent-llm-killed-postmortem.md`

## 관련

- `templates/reference-validation-checklist.md` — Phase 0 진입 전
- `skills/abandon-criteria/` — kill trigger 생성
- `audits/2026-04-25-mirosalmon-abandon-retrospective.md` — 원 사태
- `audits/2026-04-27-eight-k-non-reliance-frozen-postmortem.md` — Day-by-Day audit pattern 입증
- `audits/2026-04-26-activist-intent-llm-killed-postmortem.md` — 18h-burst anti-pattern
