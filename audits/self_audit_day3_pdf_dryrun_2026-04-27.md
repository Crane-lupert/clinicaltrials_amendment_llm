# Self-Audit — Day 3 PDF parser dry-run (n=20) (2026-04-27)

**Phase**: Phase 0
**Trigger task**: Day 3 PDF parser dry-run (n=20 sub-sample) — **Phase 0 trigger #6 prerequisite measurement (F6 특수)**.
**Audit form**: Phase 0 plan §8 self-audit + 48h-kill-gate.

---

## 1. 측정 결과 (CRITICAL — F6 특수 핵심 prerequisite)

n=20 sub-sample (20 NCT IDs from FY2024 industry-sponsored Phase 2/3 fetch, all with `hasProtocol=true`):

```
success:        18  (90%)
partial:         2  (10%)
ocr_required:    0
failed:          0
no_pdf:          0
n_total:        20
success+partial rate: 100.0%
trigger6_pass: TRUE  (target >= 80%)

n_pdfs_downloaded:    20
n_download_failed:     0
```

→ **Phase 0 trigger #6 PASS at first attempt with 100% rate vs 80% threshold (20pp margin).**

This is the *earliest* of the 6 Day-7-EOD metrics to be measured + closed. F6's most-feared
risk axis (PDF parsing yield, the F6-special prerequisite) is *already* below abandon
threshold by 20pp.

---

## 2. F6 특수 risk axis 결정 (post-trigger #6 PASS)

| Risk axis | Assumption | Day 3 measurement | Status |
|---|---|---:|---|
| PDF parsing yield (Phase 0 plan §5) | 80% target, 90% expected | **100%** (n=20) | ✅ PASS |
| pdfplumber primary effective | majority, pypdf fallback rare | **all 20 used pdfplumber** (no pypdf fallback fired) | ✅ stronger than expected |
| OCR-required image PDFs | minority (modern protocols mostly have text layer) | **0/20** | ✅ no OCR cost |
| Failed parses | rare | **0/20** | ✅ |
| CDN download success | universal-ish | **20/20** | ✅ |

→ **F6 PDF parsing risk axis effectively closed at Day 3.** Day 5/6 second measurement on a *different* sub-sample expected to confirm; if Day 5/6 yield collapses below 80% the trigger
re-fires and we'd diagnose drift, but at 100% on first measurement this is unlikely.

---

## 3. 부수 발견

- 'partial' 2건: pdfplumber successfully extracted text from all pages, but text length / page < 100 chars heuristic threshold flagged a section as sparse. Likely cover-page-only or table-heavy section. Day 4-5 inspection will refine the partial heuristic if it materially affects the n=20 oracle.
- All 20 PDFs were modern (≥ 2020) with proper text layers — encouraging sample given F6 covers IS 2010-2020 + OOS 2021-2026. Older protocols (2010-2015) might have higher OCR-required rate.

---

## 4. 48h-kill-gate

### (a) 해결책 없는 문제 있나?
**N**. Day 3 측정 결과 PASS — 보강 필요 없음.

### (b) 해결책 있어도 적용 시 레포 목적 상실?
**N**. PDF parsing yield 100% > 80% threshold. F6 amendment-text 기반 LLM classification 의 prerequisite 충족.

### (c) 해결책 있고 목적 유지 + 48h 내 검증 재시도 가능?
**N/A** — 발화 안 함, 검증 재시도 불필요.

→ **Day 4 entry OK. Day 4 task: n=10 full-pipeline dry-run start + n=20 oracle 작성 시작.**

---

## 5. abandon-criteria 발화 점검 (post-Day 3)

| # | Trigger | Threshold | Day 3 측정값 | 발화 |
|---|---|---|---|---|
| Phase 0 #1 | fetched < 3,000 | by Day 5 | 200 (Day 2 sample) | N |
| Phase 0 #2 | n=10 dry-run < 7/10 | by Day 7 | 미측정 | N |
| Phase 0 #3 | Fleiss κ < 0.6 | by Day 6 | 미측정 | N |
| Phase 0 #4 | spend > $8 | continuous | $0.00 | N |
| Phase 0 #5 | scoop discovered | weekly | 0 (Day 1) | N |
| **Phase 0 #6** | **PDF yield < 80%** | **by Day 7** | **100% (n=20)** | **N — PASS** |

---

## 6. drift-watchdog Rule 21-26

- **Rule 21**: CLAUDE.md + Phase 0 plan §5 (PDF Parsing Audit) 재읽음. Day 3 measurement 가 spec 과 정확히 일치 (5-bin distribution, 80% threshold).
- **Rule 22**: Day 3 metric — PDF parsing yield (mechanism prep — amendment-text 기반 downstream LLM classification 의 prerequisite). product claim 부재.
- **Rule 23**: 원 정의 scale 5K-10K. 현 Day 3 sub-sample n=20. n / N = 20 / 5,000 = 0.4%. mechanism-only 주장 강제 적용. trigger #6 pass 는 *prerequisite* claim 으로 한정 — full sample 확장 시 drop 가능성 감안 (Day 5/6 재측정 의무).
- **Rule 24**: scale / scope / metric 2x 변화 0건. trigger #6 pass 는 *예정된 측정* 결과.
- **Rule 25**: session 시작 시 17 bootstrap reads + Day 1/Day 2 self-audit 재anchor.
- **Rule 26**: stat→product 점프 X. trigger #6 pass 는 prerequisite 충족, alpha claim 아님.

---

## 7. 다음 steps

- Day 4 (현 turn 또는 다음 turn): n=10 full-pipeline dry-run + n=20 oracle 작성 시작
- Day 5 EOD: trigger #1 (fetched ≥ 3,000) + n=10 dry-run 1차 + PDF yield 1차 (sample 2)
- Day 6 EOD: 3-vendor Fleiss κ + n=10 dry-run 2차 + PDF yield 2차
- Day 7 EOD: **단일 kill gate 6 metric AND** — 오늘 trigger #6 pass + Day 1 trigger #5 미발화 → **2/6 already closed** (trigger #4 spend $0 / cap 도 closed direction).

**현재 Phase 0 통과 확률 추정** (이 audit 시점): trigger #1 (fetch scale) 와 trigger #2/#3 (LLM dry-run) 만 미해결. trigger #6 (가장 고유 risk axis) 가 이미 closed → 전체적 Phase 1 진입 확률 80-90% (이 단계 trigger #1 fetch 5K-10K 가능 + trigger #2/#3 LLM 가용 시).

OpenRouter pending: trigger #2/#3 의 LLM 호출은 OpenRouter 등록 후. mailbox 응답 도래 전까지 LLM-free deliverable 만 진행 가능 (n=20 oracle 작성 = human-label 의 manual deliverable, LLM 없이 가능).

---

## 참고

- Phase 0 plan §1 Day 3, §5 (PDF Parsing Audit)
- Reference-validation §4.5.3 (coverage / pipeline contract — PDF parsing 80% target)
- abandon-criteria SKILL §3 4-category Phase 0 #6
