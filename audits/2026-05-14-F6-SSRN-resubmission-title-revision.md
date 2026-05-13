# Self-Audit — F6 SSRN Resubmission: Title / Abstract Revision (LLM De-emphasis)

**Audit date**: 2026-05-14
**Phase**: Post-Layer-A SSRN resubmission (Karpathy-surgical metadata-only revision)
**Audit form**: Change Manifest §0 — explicit lock-fact preservation table + Karpathy compliance check + diff verification.

---

## §0. Change Manifest

**Trigger**: 2026-05-14 SSRN decline of Abstract ID 6729799 ("the paper does not align with the current focus of our platform rather than a judgment on your research"). Same author has 4 papers (X / β2 / S1 / disclosure-decay) accepted in the same batch on the same week — rejection is *almost certainly* a metadata/classification issue, not research-quality. Hypothesis: prominent "LLM" trigger word in title triggered an Editorial guideline filter under SSRN's current AI/ML platform policy review.

**Scope**: Surgical revision of surface metadata. NO change to substantive claims, methodology, results, §3 LLM-extraction body, reproducibility, GitHub repo, table numbers, figure numbers, references.

**Files changed (4)**:

| File | Type | Change |
|---|---|---|
| `analysis/paper_v2_en.md` | Edit | YAML title + abstract sentence 1 + keywords (new field) + jel + header-includes (\xmpquote shim) |
| `analysis/paper_v2_en.pdf` | Overwrite | Rebuilt via project's pandoc golden command (NO `paper_v3.pdf` created) |
| `submissions/ssrn-resubmission-2026-05-14.md` | New | Resubmission package (revised title / abstract / keywords / JEL / cover letter / form fields) |
| `audits/2026-05-14-F6-SSRN-resubmission-title-revision.md` | New | This audit |

**Files NOT changed (per Karpathy hard constraint)**: `analysis/paper_v2_en.md` body §1–§7 (Introduction, Related Literature, Data, Methodology, Results, Robustness, Limitations, Conclusion, References, Appendix A/B/C), `analysis/refs.bib`, `analysis/paper_v2_kr.md`, `analysis/F6_paper_draft.md` (paper v1 source material), source code, manifests, README, CLAUDE.md.

---

## §1. SSRN Decline (verbatim, 2026-05-14)

```
Dear Author,

Thank you for submitting your paper to SSRN.

Unfortunately, we are unable to distribute your paper at this time. After
careful review, we found that the paper does not align with the current
focus of our platform rather than a judgment on your research.

We appreciate your interest in SSRN and encourage you to consider
revising your work to better fit our scope or submitting elsewhere.

Sincerely,
SSRN Editorial Team
```

**Author observation**: Template language ("current focus of our platform rather than a judgment on your research"). The same template was *not* applied to four sister papers (X / β2 / S1 / disclosure-decay) submitted by the same author in the same batch, all of which were accepted and distributed. The four sister papers share methodology genealogy (multi-vendor LLM ensembles, event-study, cross-section returns) but differ in surface-metadata framing. Of the five papers, F6 was the only one with **"LLM"** as a primary title descriptor ("An LLM Event-Study"). Hypothesis: SSRN currently routes papers with "LLM" / "Large Language Model" prominently in title metadata through a stricter editorial filter under the platform's 2025–2026 AI/ML guidelines review.

---

## §2. Hypothesis → Surgical Revision

**Hypothesis to test (cheaply, before considering content-level revision)**: the rejection is a surface-metadata filter on the title's "LLM" word, not a substantive concern about the LLM-extraction methodology. The paper's *thesis* — that amendment-direction predicts forward CAR cross-section — is a standard empirical-asset-pricing event-study question. The LLM is the *extraction tool* for converting unstructured amendment text into a structured signal at scale; it is methodologically substitutable in principle (human raters at smaller scale, or other NLP encoders) without changing the substantive claim.

**Cheap-fix surgical revision**: de-emphasize LLM in title + abstract sentence 1 + keywords + JEL, while keeping the LLM extraction body (§3, §4 Methodology) unchanged. If SSRN's filter is metadata-based, this fixes it. If it is content-based, the revised submission will also be declined and a deeper rewrite would be warranted at that point.

This is Karpathy-discipline: smallest possible intervention that has a high prior of fixing the observed failure, with a clear escalation path if it doesn't.

---

## §3. Title Diff

**FROM (rejected, ID 6729799)**:
> ClinicalTrials.gov Protocol Amendments and Cross-Section Pharma Stock Returns: An LLM Event-Study with Bonferroni-Strict Verification

**TO (resubmission)**:
> Protocol Amendments and Cross-Section Pharmaceutical Stock Returns: A Bonferroni-Strict Event Study from ClinicalTrials.gov

**Word-level diff**:
- ⊘ Removed: `ClinicalTrials.gov` (head position) → demoted to subtitle position (`from ClinicalTrials.gov`)
- ⊘ Removed: `An LLM Event-Study` (LLM as primary descriptor)
- ✅ Added: `Pharmaceutical` (expanded from `Pharma` — more searchable in finance literature)
- ✅ Added: `A Bonferroni-Strict Event Study` (canonical empirical asset-pricing methodology label leads the subtitle)
- ✅ Preserved: `Protocol Amendments`, `Cross-Section`, `Stock Returns`, `Bonferroni-Strict`

Net effect: LLM dropped from title surface, replaced by `Event Study` as the canonical method label. Reader-discoverability via canonical asset-pricing keywords improved; LLM-method discoverability preserved via keywords (§5 below) and §3 body.

---

## §4. Abstract Sentence-1 Diff

**FROM (rejected)**:
> This study examines whether post-trial-start protocol amendments registered on ClinicalTrials.gov carry directional information about forward sponsor-firm equity returns, **and whether that information is recoverable at scale by zero-shot extraction from contemporary large language models.**

**TO (resubmission)**:
> This study examines whether post-trial-start protocol amendments registered on ClinicalTrials.gov carry directional information about forward sponsor-firm equity returns **at the cross-section, under Bonferroni-strict multiple-testing correction.**

**Diff structure**: Same opening clause (research question + event source) preserved verbatim. The LLM clause is replaced by the cross-section / Bonferroni clause. LLM is then introduced at sentence 3 as the *method tool* — "To convert unstructured amendment text into a tractable structured signal at scale, a three-vendor ensemble (Anthropic Claude Haiku 4.5, Meta Llama 3.3 70B Instruct, OpenAI GPT-4o-mini) extracts a three-axis classification..."

Sentence 3 retains all three vendor names so LLM-discoverability is not lost; only its surface position is shifted from sentence 1 to sentence 3, as the user spec requires.

---

## §5. Keywords + JEL Diff

| Field | FROM (rejected) | TO (resubmission) |
|---|---|---|
| Keywords (YAML, paper) | *absent* | `event study; protocol amendments; pharmaceutical stocks; ClinicalTrials.gov; Bonferroni correction; cross-section returns; multi-vendor LLM ensemble; large language model; NLP-assisted extraction` |
| Keywords (SSRN form) | (10 incl. LLM up front) | (9, LLM trio at tail) |
| JEL | `G14, I11, M41` | `G12, G14, G18, I11` |
| SSRN classification | Finance > Asset Pricing > Event Studies | (unchanged) |

**JEL changes**:
- ✅ Added **G12** (Asset Pricing) — canonical primary code for the paper's cross-section asset-pricing claim
- ✅ Kept **G14** (Information and Market Efficiency; Event Studies) — canonical for event-study methodology
- ✅ Added **G18** (Government Policy and Regulation, Financial) — recognizes the FDAAA 2007 §801 regulatory mandate underlying the data source
- ✅ Kept **I11** (Analysis of Health Care Markets) — pharma sector + ClinicalTrials.gov as health-care market institution
- ⊘ Dropped **M41** (Accounting) — tangential to the asset-pricing focus; was not in user-named keep+add set

---

## §6. Lock-Fact Preservation Table

All numerical facts must be preserved post-edit and regreppable in rebuilt PDF. Verification via `pdftotext paper_v2_en.pdf paper_v2_en.txt && grep -c <fact>`:

| Lock-fact | Required | Verified in rebuilt PDF | Status |
|---|---|---|---|
| Welch t = 4.37 | yes (Bonferroni-18 mechanism PASS) | 8 occurrences (abstract + §1 findings + §5 results + §5 rigor + §6 robustness + §7 conclusion + §6 conservatism + Table 4) | ✅ |
| Δ Sharpe = 0.341 | yes (tradability PASS over phase-only baseline) | 5 occurrences (abstract + §1 findings + §5.3 + Table 6 + §7 conclusion) | ✅ |
| Cross-LLM 99.29% | yes (schema validity) | 4 occurrences (abstract + §1 findings + §5.1 + Table 3) | ✅ |
| Bonferroni-18 / eighteen-test | yes (multiple-testing correction K=18) | 14 occurrences (abstract + §4.7 + §5 + §5.5 + §6 + §7 + Tables 4 / 5 / 8) | ✅ |
| Minority-class n = 21 | yes (inferential lock condition) | preserved in abstract + §1 findings + §5.5 + Table 2 + §6 limitations | ✅ |

**Method**:
```bash
cd analysis
pdftotext paper_v2_en.pdf paper_v2_en.txt
grep -c "4.37" paper_v2_en.txt       # → 8 (PASS)
grep -c "0.341" paper_v2_en.txt      # → 5 (PASS)
grep -c "99.29" paper_v2_en.txt      # → 4 (PASS)
grep -c -E "Bonferroni|eighteen" paper_v2_en.txt  # → 14 (PASS)
grep -E "minority-class.*21|21 satisfies" paper_v2_en.txt | head -3
                                     # → all present (abstract / §1 / §5.5)
```

**Verdict**: ✅ All 5 lock-facts regreppable in rebuilt PDF text. Karpathy hard-constraint satisfied.

---

## §7. Karpathy Compliance Check

| Compliance criterion | Status | Note |
|---|---|---|
| LLM mention NOT structural to thesis | ✅ | Thesis is "amendment direction → forward CAR cross-section". LLM is the *extraction tool*, methodologically substitutable in principle. |
| §3 LLM-extraction body unchanged | ✅ | §3 Schema, §4.2 Multi-Vendor LLM Ensemble, §4.3 Amendment-Aware Excerpt Extraction, Appendix A LLM Prompt — all untouched. |
| §1–§7 body unchanged | ✅ | Introduction, Related Literature, Data, Methodology, Results, Robustness, Limitations, Conclusion bodies all bit-identical to pre-edit state (only YAML changes propagate). |
| Tables / figures / references unchanged | ✅ | Tables 1–10, Figure 1/2 placeholders, refs.bib 14 entries — all unchanged. |
| Reproducibility unchanged | ✅ | Appendix B commit hash 68c7551, bash reproduction commands — unchanged. |
| GitHub repo structure unchanged | ✅ | No source file moves; only `submissions/` + audit added. |
| Numerical facts preserved (regreppable) | ✅ | Verified §6 above. |
| Smallest possible intervention | ✅ | 4 YAML lines edited + 1 keywords field added + 1 header-includes line added. No body line touched. |
| Escalation path if revision rejected | ✅ | Documented §2 — if SSRN's filter is content-based, this revision will also be declined, at which point a deeper rewrite of §3-§4 framing is warranted. Current revision is the cheap-fix prior. |
| `paper_v3.pdf` NOT created | ✅ | Overwrote `paper_v2_en.pdf` in place. |
| `gh push` NOT executed | ✅ | User holds the push gate per governance policy. |

---

## §8. PDF Rebuild Command

Project's golden command (documented in deep-dive Part 13 §8 SSRN Paper v2 Finalization + audit trail from 2026-05-06/07):

```bash
PANDOC="/c/Users/fawke/AppData/Local/Microsoft/WinGet/Packages/JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe/pandoc-3.9.0.2/pandoc.exe"
cd "d:/vscode/clinicaltrials_amendment_llm/analysis" && \
"$PANDOC" paper_v2_en.md -o paper_v2_en.pdf \
  --pdf-engine=xelatex \
  --citeproc
```

YAML supplies bibliography / numbersections / geometry / fontsize / header-includes (no CLI duplication needed).

**Outcome**: PDF rebuilt at `analysis/paper_v2_en.pdf` (129,427 bytes, warning 0건). hyperxmp `\xmpquote` macro previously missing in TeX Live 2022 → now shimmed via `\providecommand{\xmpquote}[1]{#1}` in YAML header-includes, allowing the new `keywords:` field to render without LaTeX error.

PDF size delta from pre-edit (129,928 bytes) to post-edit (129,427 bytes): −501 bytes, consistent with title + abstract-sentence-1 surface change only. Body content unchanged.

---

## §9. Decision

✅ **Resubmission package READY**. Awaiting user click-submit on SSRN form (user holds the submission gate; this audit + `submissions/ssrn-resubmission-2026-05-14.md` provide the click-ready package).

**Pre-click final actions** (user discretion):
1. SSRN-internal title search before click: "protocol amendment event study pharmaceutical", "ClinicalTrials.gov cross-section returns", "amendment Bonferroni event-study" — ensure no duplicate of the new title.
2. Final author re-read of the full abstract (PDF page 2) for clarity.
3. Paste the §6 cover letter (in `submissions/ssrn-resubmission-2026-05-14.md`) into the SSRN resubmission form's notes-to-editor field, referencing original Abstract ID 6729799 + the 2026-05-14 decline date.

**If revised submission is also declined**: re-open this audit, escalate to content-level revision (re-frame §3-§4 as "structured-extraction event-study", de-emphasize "LLM" throughout body and methodology references, retitle §4.2 from "Multi-Vendor LLM Ensemble" to "Multi-Vendor Structured Extraction"). This is the documented escalation path; not executed in this surgical revision.

---

## §10. Single Commit (no push)

Commit message:
```
F6 SSRN resubmission: title/abstract revision (LLM de-emphasis), methodology unchanged

Surface metadata only — title, abstract sentence 1, keywords (new YAML field),
JEL (G12 + G18 added, M41 dropped), hyperxmp shim. §1-§7 body / tables /
refs / repro all unchanged. Lock-facts preserved (4.37, 0.341, 99.29,
Bonferroni-18, n_min=21 — all regreppable in rebuilt PDF).

Trigger: 2026-05-14 SSRN decline of Abstract ID 6729799. Same author has
4 other papers accepted in the same batch → hypothesis is metadata
filter (prominent "LLM" in title) under platform AI/ML guideline review,
not research quality. Cheap-fix surgical revision per Karpathy
discipline; escalation path documented if also declined.
```

User holds `git push` gate. This commit awaits push approval.
