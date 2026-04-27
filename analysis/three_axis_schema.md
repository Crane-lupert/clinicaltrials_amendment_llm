# 3-Axis Pivotal-Shift Classification Schema (F6)

**작성일**: 2026-04-27 (Day 4)
**Source**: F6 reference-validation §1 (anchor) + Phase 0 plan §1 (Day 1-7 oracle pilot)
**Use**: n=20 oracle labeling (Day 4-5) + 3-vendor LLM ensemble Fleiss κ measurement (Day 6, trigger #3) + Phase 1 full sample inference (Day 8-12).

---

## Axis 1: Pivotal Shift Direction

The amendment's net effect on the trial's *commercial / regulatory pivotability*. Three values:

| Value | Definition | Examples |
|---|---|---|
| `positive` | Amendment expands the trial's reach toward registration / approval. | Dose escalation enabled; arm added (combination); enrollment cap raised; endpoint upgraded (e.g. surrogate → clinical); accelerated regulatory pathway invoked; OS / PFS extended; geography expanded. |
| `neutral` | Amendment is design-correction / clarification / housekeeping with no directional regulatory impact. | Typo / footnote fix; IRB list update; correlative biomarker added but not co-primary; protocol harmonization across countries; DMC charter update; statistical methods clarification (no Δ in α-spending). |
| `negative` | Amendment shrinks the trial's reach OR signals weakness. | Primary endpoint changed *post hoc*; sample size reduced; population narrowed (excluding subgroups); arm dropped due to toxicity / futility; trial paused / temporarily halted; regulatory hold; unblinding for safety. |

**Decision rule when ambiguous**: lean to `neutral` when the change is mechanically design-corrective with no directional bias on the company's commercial position. Lean to `negative` when the change reduces statistical power for the *original* primary endpoint, even if rationale is "interim safety review".

---

## Axis 2: Administrative vs Substantive

| Value | Definition |
|---|---|
| `admin` | Pure paperwork: typo, IRB additions/removals, contact-info, country-rollout sequencing, formatting. No design impact. |
| `substantive` | Anything that changes the protocol's design specification: endpoint, sample size, dose, eligibility, randomization, duration, SAP, follow-up window. |

**Decision rule**: if the amendment Modifies Inclusion/Exclusion Criteria, dose, endpoint, sample size, or duration — `substantive`. If it Adds investigator names, fixes typos, harmonizes formatting — `admin`. Borderline: country-list expansion → `substantive` if it materially changes recruitment composition; otherwise `admin`.

---

## Axis 3: DSMB-driven vs Sponsor-driven

The locus of decision-making behind the amendment.

| Value | Definition | Cues in text |
|---|---|---|
| `dsmb` | DSMB / DMC / Independent Data Monitoring Committee triggered the amendment after interim analysis or safety review. | "DSMB recommendation", "interim analysis triggered", "safety review", "futility analysis", "blinded interim assessment". |
| `regulator` | FDA / EMA / regulatory authority required the amendment. | "FDA request", "Type B meeting", "regulatory feedback", "responding to comments from Agency". |
| `sponsor` | Sponsor-initiated for strategic / operational / commercial reasons. | "sponsor decision", "in light of competitive landscape", "to align with marketing strategy", "operational efficiency", "responding to FDA but no formal requirement". |

**Decision rule**: prioritize the most upstream actor explicitly named. If text says "after DSMB recommendation, sponsor amends...", value is `dsmb`. If "sponsor amended the protocol" without DSMB / regulator mention, default to `sponsor`.

---

## 2-Axis Fallback (Phase 0 trigger #3 fallback)

If 3-vendor 3-axis Fleiss κ < 0.6, collapse to **pivotal-binary** (single axis):

| Value | Definition |
|---|---|
| `substantive_design_change` | Same as Axis 2 `substantive` AND Axis 1 ∈ {positive, negative} (i.e. the change is a real *pivot*, not noise). |
| `admin_or_neutral` | Axis 2 `admin` OR (Axis 2 `substantive` AND Axis 1 `neutral`). |

This collapses the 3 × 2 × 3 = 18-cell joint to a 2-cell binary. Expected to push κ toward 0.7+ at the cost of granularity.

---

## Notes for the labeler / LLM rater

1. **Read the full amendment narrative when available.** CT.gov v2 study record `protocolSection` / `descriptionModule` and the protocol PDF together provide context. The amendment-specific block (often in `History of Changes` on the website) is the authoritative source.
2. **Don't conflate enrollment with sample size.** A trial *enrolling slower than planned* is **not** an amendment. A trial whose *target sample size is reduced* is.
3. **Endpoint changes are the highest-stake signal.** Changing from OS to PFS as primary, post-hoc, is a `negative` `substantive` `sponsor` red flag.
4. **Vaccine cohort caveat (F1-4 lesson)**: 2020-2022 COVID/RSV/influenza vaccine trial amendments are often *positive substantive sponsor* (scope expansion as the EUA path opens) and require separate stratum reporting (Day 15-16 task).
5. **DSMB-driven negative is the most predictive for biotech equity downside.** Sponsor-driven positive may be optimism-priced; DSMB-driven negative tends to be surprise-relative-to-expectation.

---

## References

- F6 reference-validation §1.1 / §4.5.2 — schema objectivity argument
- F6 Phase 0 plan §1 (Day 4-6 oracle pilot)
- F1 frozen postmortem §9 Lesson F1-3 (surprise vs absolute classifier — F6 v1 absolute, v2 expectation-prior layer)
- F1 frozen postmortem §9 Lesson F1-4 (vaccine cohort stratum)
- DiMasi-Grabowski 2003 / 2016 (J Health Econ) — phase transition success rate baseline
