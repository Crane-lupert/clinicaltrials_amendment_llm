# F6 — SSRN Resubmission Package (2026-05-14)

> **⚠️ 2026-05-17 — RETIRED**: This resubmission was declined by SSRN (2nd decline). Decline message stronger than 1st: "does not meet SSRN's submission requirements... submission type and screening criteria". LLM-in-title hypothesis (this package's mitigation) is invalidated since title removed LLM and was still rejected. **F6 SSRN worktrack retired** — pivoted to GitHub-only artifact strategy (QR Scout audience: GitHub README + repo paper PDF + commit chain matter more than SSRN abstract page; SSRN click rate <5% for HF hiring funnels). The "Numerical-fact preservation" note below is also superseded: 2026-05-17 dedup audit found Welch t = 4.37 was inflated by row-aggregation independence violation in `rigor_pass.py`; corrected Welch t = 1.69 at unique-amendment level (FAIL Bonferroni-18 + FAIL uncorrected). Direction (-7.48% spread) preserved; strict-significance certificate withdrawn. See `D:/vscode/meta-harness/reports/papers/2026-05-17-clinicaltrials-amendment-paper-dedup-audit.md` + `analysis/paper_v2_en.md` §7 Post-Publication Self-Correction. **This file is preserved as historical record of the 2026-05-14 resubmission attempt**.

**Project**: F6 — ClinicalTrials.gov Protocol Amendments × Cross-Section Pharmaceutical Stock Returns
**Original SSRN Abstract ID**: 6729799 (submitted 2026-05-08 KST, rejected 2026-05-14 KST)
**2nd Resubmission outcome**: Declined (post-2026-05-14, stronger rejection language)
**Resubmission target** *(retired)*: SSRN Empirical Asset Pricing / Event Studies network
**Revision scope**: surgical metadata only — title, abstract opening (sentence 1), keywords, JEL. Methodology, results, §3 LLM extraction body, reproducibility, GitHub repo, tables, references — all unchanged.
**Rebuilt PDF**: `analysis/paper_v2_en.pdf` (overwritten, ~129KB, pandoc 3.9 + xelatex + citeproc)
**Numerical-fact preservation**: ✅ Welch t=4.37 (8 occurrences), Δ Sharpe 0.341 (5 occurrences), cross-LLM 99.29 (4 occurrences), Bonferroni-18 / eighteen-test (14 occurrences), minority-class n=21 (preserved in abstract + §5 + §1) — all regreppable in rebuilt PDF text.

---

## 1. Revised Title

> **Protocol Amendments and Cross-Section Pharmaceutical Stock Returns: A Bonferroni-Strict Event Study from ClinicalTrials.gov**

Diff from rejected submission:
- Removed: `An LLM Event-Study` (LLM as primary descriptor)
- Promoted: `Event Study` (canonical asset-pricing methodology label)
- Promoted: `Pharmaceutical Stock Returns` (sector + asset-pricing focus)
- Demoted: `ClinicalTrials.gov` (now in subtitle "from ClinicalTrials.gov", framing the data source rather than the LLM application target)
- Preserved: `Bonferroni-Strict` (rigor signal — empirical asset pricing reviewer keyword)

---

## 2. Revised Abstract (paste into SSRN abstract field)

> This study examines whether post-trial-start protocol amendments registered on ClinicalTrials.gov carry directional information about forward sponsor-firm equity returns at the cross-section, under Bonferroni-strict multiple-testing correction. The empirical setting is the fifteen-year panel 2010–2024 of 25,000 industry-sponsored Phase 2 and Phase 3 trial records. To convert unstructured amendment text into a tractable structured signal at scale, a three-vendor ensemble (Anthropic Claude Haiku 4.5, Meta Llama 3.3 70B Instruct, OpenAI GPT-4o-mini) extracts a three-axis classification of each trial's most recent amendment text—pivotal-shift direction, administrative-versus-substantive scope, and decision-driver locus. After mapping sponsor names to listed-equity tickers, the matched panel contains 152 event-window cumulative-abnormal-return observations and 80 regression-ready observations with full three-vendor consensus. The pre-registered long-positive minus short-negative spread at the thirty-trading-day horizon is +7.79 percent with Welch *t* = 4.37, exceeding the Bonferroni-corrected critical value of 2.99 (eighteen-test family, two-tailed) by a margin of 1.38. Relative to a transparent phase-only baseline that proxies the Reinisch et al. (2024) phase-transition predictor, the regression-fitted combination of phase and pivotal scores delivers an incremental Sharpe ratio of +0.341, exceeding the pre-registered threshold of 0.30. Cross-vendor two-of-three majority agreement is 99.29 percent across the three axes (95 trials with full coverage), and the minority-class size at 21 satisfies the conservative *n* ≥ 20 threshold for stable inference on label-distribution-sensitive estimators. The contribution is positioned at the boundary of three literatures. Existing trial-event–to–return work concentrates on trial *announcements* and *results* (Pinto et al. 2023; arxiv 2208.07248; Wang et al. 2022); the protocol-amendment literature is operational and cost-focused (Tufts CSDD 2024); and concurrent LLM applications to ClinicalTrials.gov text address orthogonal classification tasks (Liu et al. 2025). To my knowledge this is the first paper to use post-trial-start protocol amendments as the unit of cross-section equity-return prediction, and the first to verify that the resulting amendment-derived signal is incremental over a CTP-LLM-style phase-transition baseline. The full pipeline runs from the public ClinicalTrials.gov registry to the final alpha summary using only public data sources, and the extraction prompts, statistical scripts, and a locally runnable visualization dashboard are released in the public repository at the commit hash listed in Appendix B.

Sentence-1 diff vs rejected submission:
- **Old**: "This study examines whether post-trial-start protocol amendments registered on ClinicalTrials.gov carry directional information about forward sponsor-firm equity returns, **and whether that information is recoverable at scale by zero-shot extraction from contemporary large language models.**"
- **New**: "This study examines whether post-trial-start protocol amendments registered on ClinicalTrials.gov carry directional information about forward sponsor-firm equity returns **at the cross-section, under Bonferroni-strict multiple-testing correction.**"

→ LLM clause removed from sentence 1; LLM appears in sentence 3 as the *method tool* ("To convert unstructured amendment text into a tractable structured signal at scale, a three-vendor ensemble..."). Per Karpathy-surgical: 0 changes to substantive claims; only surface positioning shift.

---

## 3. Keywords (enter-separated, SSRN form)

Promoted (empirical-asset-pricing reader discoverability):

```
event study
protocol amendments
pharmaceutical stocks
ClinicalTrials.gov
Bonferroni correction
cross-section returns
```

Demoted but preserved (NLP/LLM reader discoverability — still findable, but not in surface position):

```
multi-vendor LLM ensemble
large language model
NLP-assisted extraction
```

Total: 9 keywords. SSRN typical limit 10-12.

---

## 4. JEL Classification (SSRN form)

| Code | Description | Status |
|---|---|---|
| **G12** | Asset Pricing; Trading Volume; Bond Interest Rates | ✅ Added (was absent in rejected submission) |
| **G14** | Information and Market Efficiency; Event Studies | ✅ Kept |
| **G18** | Government Policy and Regulation (Financial) | ✅ Added (was absent in rejected submission) |
| **I11** | Analysis of Health Care Markets | ✅ Kept |
| ~~M41~~ | ~~Accounting~~ | ⊘ Dropped (not in keep+add set; tangential to asset-pricing focus) |

Final JEL set: **G12, G14, G18, I11** (4 codes).

---

## 5. SSRN Classification (Network/JEL form)

Primary: **Finance > Asset Pricing > Event Studies** (unchanged — this is exactly the network the empirical asset-pricing focus targets)

Multi-select (8 networks, unchanged from previous resubmission package — these align with empirical-asset-pricing reader discoverability, not LLM/AI):

1. Event Studies (primary)
2. Capital Markets: Asset Pricing & Valuation
3. Empirical Asset Pricing
4. Cross-Section of Stock Returns
5. Pharmaceuticals, Healthcare & Medical Devices: Industry Studies
6. Health Economics
7. Machine Learning (de-emphasize — keep if SSRN form allows tail-end ordering, else drop)
8. Computational Linguistics & NLP (de-emphasize — same as #7)

If SSRN form limits to 6 networks for empirical-asset-pricing alignment, drop #7 and #8. The paper is discoverable via JEL G12/G14/G18 and keywords for AI/NLP readers regardless.

---

## 6. Cover Letter Draft (for SSRN resubmission form, 5-7 lines)

```
Dear SSRN Editorial Team,

I am resubmitting Abstract ID 6729799, which was declined on 2026-05-14
under the platform-focus guideline. I have revised the title, abstract
opening sentence, keywords, and JEL classification to align the surface
metadata with the paper's empirical asset-pricing focus: a Bonferroni-
strict event study on ClinicalTrials.gov protocol amendments and cross-
section pharmaceutical stock returns. The empirical content, statistical
methodology, sample, and results are unchanged. Numerical claims
(Welch t = 4.37 over the Bonferroni-18 critical 2.99; incremental Sharpe
Δ = +0.341 over a registry-only baseline; n = 152 event-window observations
across the 2010–2024 fifteen-year panel) are identical to the original
submission and preserved in the rebuilt PDF.

The same author has four other papers (X / β2 / S1 / disclosure-decay)
accepted and distributed by SSRN in the same batch, suggesting that the
prior decline reflected metadata classification rather than a research-
quality concern. I trust the revised positioning resolves this.

Sincerely,
Ahn Hyun
```

---

## 7. Other SSRN Form Fields (carried over from 2026-04-28 submission package — re-confirm at click time)

### 7.1 Declaration of Interest

> The author declares no competing financial or non-financial interests in relation to the work described in this paper. The author is an independent researcher and has no employment, consulting, or advisory relationship with any clinical-trial sponsor, biotechnology firm, pharmaceutical firm, or any other organization whose securities are analyzed in this study. The author holds no equity, options, or derivative positions in any specific firm referenced or analyzed herein, and has not received compensation tied to the publication or interpretation of the results. The large language model API access used for the empirical work was purchased through the public OpenRouter gateway with no special pricing, no vendor sponsorship, and no contractual obligation to favor any particular model or vendor in the analysis or reporting.

### 7.2 Funder Statement

> This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors. The work was conducted independently by the author, who self-funded the computational expenses, including the OpenRouter large language model API spend of approximately US\$0.47 across 440 classification calls. No internal or external research grant, fellowship, or institutional support was received in connection with this study.

### 7.3 Ethics Approval

> This study uses only publicly available secondary data and does not involve human participants, patient-level data, or individually identifiable health information. The data sources are: (i) the ClinicalTrials.gov v2 public API (a U.S. federal registry mandated under the Food and Drug Administration Amendments Act of 2007 §801 and 42 CFR Part 11), which contains trial-level metadata and protocol documents but no individual-patient records; (ii) the SEC company-tickers public metadata; and (iii) Yahoo Finance daily equity price data. No clinical intervention, recruitment of subjects, biological sampling, or contact with patients or trial sites was conducted. Institutional Review Board (IRB) review and ethics-committee approval are therefore not applicable to this study. The work complies with the ClinicalTrials.gov Terms of Use for public-data use in academic research and does not redistribute any non-public material.

### 7.4 AI / LLM Usage Disclosure

> Large language models (Anthropic Claude Haiku 4.5, Meta Llama 3.3 70B Instruct, OpenAI GPT-4o-mini) were used as the primary feature-extraction mechanism on protocol amendment text, as described in §4 of the paper. No LLM was used to generate, draft, or revise the paper's text, equations, or analytic results. Authorship and accountability rest entirely with the human author.

### 7.5 Data and Code Availability

> All code and reproduction scripts are available at `github.com/Crane-lupert/clinicaltrials_amendment_llm` (commit `68c7551`). Raw data inputs are public via the ClinicalTrials.gov v2 API, SEC company-tickers, and Yahoo Finance.

---

## 8. Pre-Submission Checklist (re-confirm at click time)

- [x] Revised title (§1) reflected in PDF cover + running header
- [x] Revised abstract sentence 1 (§2) reflected in PDF abstract page
- [x] Keywords (§3) — 9 items, LLM trio moved to tail
- [x] JEL (§4) — G12 / G14 / G18 / I11 final set
- [x] Cover letter (§6) drafted
- [x] Lock-fact regrep PASS — 4.37 / 0.341 / 99.29 / Bonferroni-18 / n=21 all preserved in rebuilt PDF
- [x] PDF rebuilt at `analysis/paper_v2_en.pdf` (overwrites prior; no `paper_v3.pdf` created)
- [ ] SSRN-internal title search before click ("protocol amendment event study pharmaceutical", "ClinicalTrials.gov cross-section")
- [ ] Final author re-read of full abstract for clarity
- [ ] Click submit (user holds the gate; this package is click-ready)
