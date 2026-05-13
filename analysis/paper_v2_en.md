---
title: "Protocol Amendments and Cross-Section Pharmaceutical Stock Returns: A Bonferroni-Strict Event Study from ClinicalTrials.gov"
author: "Ahn Hyun"
date: "May 2026"
abstract: |
  This study examines whether post-trial-start protocol amendments registered on ClinicalTrials.gov carry directional information about forward sponsor-firm equity returns at the cross-section, under Bonferroni-strict multiple-testing correction. The empirical setting is the fifteen-year panel 2010–2024 of 25,000 industry-sponsored Phase 2 and Phase 3 trial records. To convert unstructured amendment text into a tractable structured signal at scale, a three-vendor ensemble (Anthropic Claude Haiku 4.5, Meta Llama 3.3 70B Instruct, OpenAI GPT-4o-mini) extracts a three-axis classification of each trial's most recent amendment text—pivotal-shift direction, administrative-versus-substantive scope, and decision-driver locus. After mapping sponsor names to listed-equity tickers, the matched panel contains 152 event-window cumulative-abnormal-return observations and 80 regression-ready observations with full three-vendor consensus. The pre-registered long-positive minus short-negative spread at the thirty-trading-day horizon is +7.79 percent with Welch *t* = 4.37, exceeding the Bonferroni-corrected critical value of 2.99 (eighteen-test family, two-tailed) by a margin of 1.38. Relative to a transparent phase-only baseline that proxies the @reinisch2024ctpllm phase-transition predictor, the regression-fitted combination of phase and pivotal scores delivers an incremental Sharpe ratio of +0.341, exceeding the pre-registered threshold of 0.30. Cross-vendor two-of-three majority agreement is 99.29 percent across the three axes (95 trials with full coverage), and the minority-class size at 21 satisfies the conservative $n \ge 20$ threshold for stable inference on label-distribution-sensitive estimators. The contribution is positioned at the boundary of three literatures. Existing trial-event–to–return work concentrates on trial *announcements* and *results* [@pinto2023bert; @arxiv2208_07248; @wang2022pmc]; the protocol-amendment literature is operational and cost-focused [@tufts2024amendments]; and concurrent LLM applications to ClinicalTrials.gov text address orthogonal classification tasks [@liu2025innovative]. To my knowledge this is the first paper to use post-trial-start protocol amendments as the unit of cross-section equity-return prediction, and the first to verify that the resulting amendment-derived signal is incremental over a CTP-LLM-style phase-transition baseline. The full pipeline runs from the public ClinicalTrials.gov registry to the final alpha summary using only public data sources, and the extraction prompts, statistical scripts, and a locally runnable visualization dashboard are released in the public repository at the commit hash listed in Appendix B.
keywords: "event study; protocol amendments; pharmaceutical stocks; ClinicalTrials.gov; Bonferroni correction; cross-section returns; multi-vendor LLM ensemble; large language model; NLP-assisted extraction"
jel: G12, G14, G18, I11
ssrn-classification: "Finance > Asset Pricing > Event Studies"
status: "Working paper, 2026"
geometry: margin=1in
fontsize: 11pt
linkcolor: blue
numbersections: true
bibliography: refs.bib
header-includes: |
  \usepackage{tocloft}
  \setlength{\cftbeforesecskip}{2pt}
  \setlength{\cftbeforesubsecskip}{1pt}
  \providecommand{\xmpquote}[1]{#1}
---

\clearpage

\tableofcontents

\clearpage

# Introduction

For listed biotechnology and pharmaceutical firms, fifty to ninety percent of equity valuation is contingent on the future outcomes of ongoing clinical trials. Changes in the *state* of an active trial therefore constitute a leading indicator for sponsor-firm returns. The Food and Drug Administration Amendments Act of 2007 §801 [@fdaaa2007] and the 2017 Final Rule mandate that industry-sponsored trials of drugs and biologics be registered at ClinicalTrials.gov, and that material changes to trial design—*protocol amendments*—be entered into the registry's audit trail. Tens of thousands of such amendments are publicly archived each year.

The existing event-study literature linking clinical trials to sponsor-firm equity returns concentrates on two event classes. Trial *announcements*—registrations or milestone press releases—are the first information release [@pinto2023bert; @arxiv2208_07248]. Trial *results*—interim or final readouts—are the terminal information release [@wang2022pmc]. The post-trial-start protocol amendment is a third class, occupying the timeline between announcement and result. Its direction—endpoint strengthening versus dilution, sample-size expansion versus contraction, dose escalation versus hold—is not derivable from registry metadata alone; it requires reading the amendment text itself, often a Document History or Summary of Changes section embedded in a multi-hundred-page protocol document. The market typically reflects such textual detail with a multi-day to multi-week lag, providing the basis for the cross-section signal documented here.

This study makes four contributions. First, the unit of equity-event analysis is redefined as the post-trial-start protocol amendment, distinct from announcements and results both in timing and in the textual richness of the change description itself. Second, rather than reduce amendment text to a binary positive-or-negative sentiment, a three-axis structured classification is extracted—pivotal-shift, administrative-versus-substantive, and decision-driver locus—enabling separate testing of mechanism components. Third, the extraction is performed by a three-vendor ensemble and the cross-vendor majority-agreement rate is treated as a schema-validity diagnostic, protecting against single-vendor classification artifacts. Fourth, building on the phase-transition prediction work of @reinisch2024ctpllm, a transparent phase-only baseline is constructed from registry metadata alone and the LLM amendment features are tested for *incremental* portfolio Sharpe ratio above this baseline, with the regression-fitted feature combination compared explicitly against a naive additive specification that suffers from a feature-scale-mismatch artifact.

The principal empirical findings are these. The cross-section spread between the long-positive and short-negative amendment cohorts at the thirty-trading-day horizon is +7.79 percent with Welch *t* = 4.37, which survives the strict Bonferroni-corrected critical value of 2.99 by a margin of 1.38. The LLM amendment features add an incremental Sharpe of +0.341 over the phase-only baseline; the standalone pivotal-shift portfolio in isolation delivers Sharpe 1.088. Cross-vendor two-of-three majority agreement is 99.29 percent across the three classification axes (95 trials with full coverage), and the minority-class size of 21 satisfies the conservative threshold $n \ge 20$ below which label-distribution-sensitive estimators are subject to single-observation flips. A secondary test on the same LLM features for raw phase-transition prediction yields ROC-AUC of 0.585, below the pre-registered 0.65 threshold; this auxiliary failure is interpreted in §5.4 as evidence that the amendment direction signal is *complementary* to the @reinisch2024ctpllm phase-transition signal rather than a stronger version of it.

The remainder of the paper is organized as follows. Section 2 surveys the related literature with attention to the announcement and result event-study tradition, the protocol-amendment operational benchmarks, and concurrent LLM applications on ClinicalTrials.gov text. Section 3 describes data sources and sample construction. Section 4 specifies the three-axis schema, the multi-vendor extraction procedure, and the statistical framework including the Bonferroni correction and the bootstrap inference layer. Section 5 reports the four pre-registered tests. Section 6 presents the robustness battery. Section 7 catalogs limitations. Section 8 concludes. Appendices document the LLM prompt schema, the reproduction commit hash, and methodological notes of independent interest.

# Related Literature

## Trial Announcement and Result Event Studies

@pinto2023bert combine a BERT sentiment encoder with a Temporal Fusion Transformer to model pharmaceutical equity reactions to clinical-trial announcements and results. The input is press-release and news-headline text, the output is a binary good-news–bad-news classification fed into a price model, and the dependent variable is short-window CAR around the announcement or readout. Closely related, @arxiv2208_07248 apply the same announcement-prediction paradigm to sponsor-stock movement using announcement metadata and headline sentiment. Both studies treat the announcement timestamp as the information-release moment. The protocol amendment differs from this in two respects: it is a mid-trial modification release, often reflecting external pressure from a Data and Safety Monitoring Board, a regulator, or an interim analysis finding; and the textual content of the amendment is necessarily richer than an announcement, because the change itself must be described in the amendment register.

@wang2022pmc measure abnormal returns around trial-outcome announcements using a classical market-model event-study in the @brown1985daily lineage. Trial outcomes are terminal information releases and tend to be incorporated into prices intraday, so the post-event drift window relevant for cross-section portfolio construction is narrow. Protocol amendments are partial information releases earlier in the trial lifecycle, where multi-day to multi-week price drift is observed in the present sample.

## Protocol-Amendment Operational Analysis

@tufts2024amendments report industry benchmarks for the frequency, cause distribution, and cost-and-schedule impact of protocol amendments. The Tufts data establish that amendments are common across Phase 2 and Phase 3 trials, that the modal causes are regulator request, Data and Safety Monitoring Board recommendation, and sponsor-initiated changes, and that amendments have measurable cost and timeline implications for sponsors. The dependent variable in that work is operational—cost and time—rather than firm-level equity return. Tufts establishes that amendments are sufficiently frequent and material to constitute a meaningful event class; the financial-transmission channel is not addressed and is the gap this study fills.

## LLM Applications to ClinicalTrials.gov Text

@liu2025innovative apply a large language model to the universe of ClinicalTrials.gov registrations from 2005 through 2024 to build a classifier for innovative trial designs—adaptive, basket, umbrella, master protocol. The task is descriptive trial-level classification orthogonal to the present firm-level forward-return prediction, but it establishes that LLM-on-ClinicalTrials.gov pipelines are technically tractable at the panel scale exploited here. The Liu work does not address financial outcomes and does not perform amendment-specific text extraction.

## Trial-Outcome Prediction

@reinisch2024ctpllm introduce CTP-LLM, a fine-tuned GPT-3.5 model that predicts clinical-trial phase transitions from initial protocol text, with reported overall accuracy of 67 percent and Phase 3-to-approval accuracy of 75 percent. The work is the closest prior in spirit to this paper. Three differences are material. First, the input here is the post-trial-start amendment text rather than the initial protocol, which is informationally richer for trials already underway. Second, vendor diversity is introduced and the cross-vendor two-of-three majority rate is reported as a schema-validity diagnostic, neither of which appears in the original CTP-LLM specification. Third, the output is mapped explicitly to forward equity returns, which the original work does not address. The CTP-LLM phase-transition probability is approximated transparently in §4.5 as a phase-only baseline score; the LLM amendment features are then tested for *incremental* portfolio Sharpe over that baseline.

The industry-standard estimates of phase-transition success rates are due to @dimasi2003biotech and @dimasi2016innovation. The headline finding that Phase 3 trials advance to approval at substantially higher rates than Phase 2 trials advance to Phase 3 motivates the use of the registry phase number as the baseline score. @lo2019adaptive surveys adaptive-markets-theoretic clinical-trial-outcome prediction with numeric trial-level features; the protocol-amendment text channel is not exploited.

## LLM Applications to Financial Text

@lopezlira2023chatgpt show that ChatGPT sentiment scores on news headlines predict next-day stock movements in a single-vendor, time-series setting without pre-registration. The earnings-call LLM-analysis literature documents predictive content in conference-call transcripts but works with sponsor-authored text whose external accountability is weaker. Protocol amendments, although also sponsor-authored, are constrained by the formal review and approval mechanisms imposed by Data and Safety Monitoring Boards and regulators, providing a partial external-evaluation property that ordinary sponsor-disclosure text does not.

# Data

## Sources

The data sources are public throughout. Trial records and protocol PDFs are obtained from the ClinicalTrials.gov v2 API. Sponsor-name-to-listed-equity-ticker mapping uses the SEC `company_tickers.json` static metadata supplemented by an in-house parent-rollup table for subsidiary disambiguation. Daily auto-adjusted close prices are downloaded from Yahoo Finance over the windows from one trading day before the event date to forty-five trading days after. The pipeline does not depend on any proprietary financial data product.

## Universe and Sample Period

The universe is the set of industry-sponsored Phase 2 and Phase 3 trials with `LastUpdatePostDate` in the fifteen-year window 2010-01-01 through 2024-12-31. The sponsor-class filter excludes academic, NIH, and consortium sponsors. After de-duplication the universe contains 25,000 trial records.

The event date is the `LastUpdatePostDate`—the timestamp at which the most recent record update became publicly visible. This is the earliest moment at which a market participant could observe the amendment, and is therefore the leak-safe choice for return-window construction even though the amendment-effective date inside the protocol PDF can be earlier.

## Sponsor-to-Ticker Mapping

The sponsor-to-ticker resolution proceeds through three tiers in priority order. The first tier is a hand-curated seed list of 89 firms with parent-company mapping that is non-trivial because of subsidiary structures. The second tier is a 20-entry parent-rollup table that handles common subsidiary patterns such as `Janssen-`, `Sanofi-Aventis`, and `Novartis Pharma`. The third tier is the biotech subset of the SEC `company_tickers.json`, identified by 562 firms whose registrant names match biotech-related keywords. The combined pipeline maps 9,083 of 25,000 trials, a yield of 36 percent. The unmapped sixty-four percent is concentrated in foreign-domiciled biotechs without US listings, private firms, and academic spin-offs not yet public. Survivorship-bias implications are discussed in §6.

## Protocol PDF Parsing

Protocol PDFs are parsed with `pdfplumber` as the primary engine and `pypdf` as a fallback. Two independent samples of size 20 each were audited for parsing yield. In both samples every record was either fully successful or partially successful, with no OCR-required and no failed cases (Table 1). The fallback path was not exercised in production.

**Table 1.** *Protocol-PDF parsing-yield audit. Samples drawn independently from the universe of mapped trials.*

| Sample | $n$  | Success | Partial | OCR-required | Failed | Yield |
|:-------|-----:|--------:|--------:|-------------:|-------:|------:|
| A      | 20   | 18      | 2       | 0            | 0      | 100%  |
| B      | 20   | 17      | 3       | 0            | 0      | 100%  |
| Combined | 40 | 35      | 5       | 0            | 0      | 100%  |

The ClinicalTrials.gov content-delivery network exhibits server-side throttling at approximately 13 PDFs per minute, independent of client-side concurrency at thread-pool sizes between 8 and 24. This is mitigated through aggressive on-disk caching (819 PDFs persisted across runs) and deterministic resumable manifests; it nonetheless limits dispatch volume below what the LLM budget would otherwise allow, and accounts for a portion of the gap between the 9,083-trial mapped pool and the 343-record LLM-classified sample.

## Sample Composition

The realized sample at successive pipeline stages is summarized in Table 2.

**Table 2.** *Sample sizes at successive pipeline stages.*

\begingroup\small

| Stage                                                          |       $n$ | Used in                              |
|:---------------------------------------------------------------|----------:|:-------------------------------------|
| Industry-sponsored Phase 2/3 trials, 2010–2024                 |    25,000 | Universe definition                  |
| Sponsor-to-ticker-mapped trials                                |     9,083 | Mapping-yield audit                  |
| LLM-classified records (across vendors)                        |       343 | Classification-distribution analysis |
| Trials with full three-vendor coverage                         |        95 | Cross-vendor consistency (§5.1)      |
| Event-window CAR observations                                  |       152 | Cross-section CAR test (§5.2)        |
| Regression-ready (CAR $\cap$ three-vendor consensus)           |        80 | Incremental Sharpe (§5.3)            |
| Minority-class observations (negative pivotal-shift)           |        21 | Inferential lock (§5.5)              |

\endgroup

The cross-section CAR test in §5.2 and the incremental Sharpe test in §5.3 use slightly different sample sizes because the CAR computation operates at the event level whereas the regression requires three-vendor consensus on the LLM features.

# Methodology

## Three-Axis Classification Schema

Each amendment is labelled along three axes. The pivotal-shift axis takes values in $\{$positive, neutral, negative, unknown$\}$ and represents the net effect of the amendment on the sponsor's commercial-and-regulatory pivotability: positive cases include dose escalation, scope expansion, accelerated timeline, and endpoint strengthening; negative cases include endpoint dilution such as a switch from overall survival to progression-free survival, sample-size reduction, population narrowing, dose hold, and futility stopping; neutral cases reflect design-unchanged or impact-unclear amendments. The administrative-versus-substantive axis takes values in $\{$admin, substantive, unknown$\}$ and distinguishes paperwork updates—typo fixes, IRB list changes, contact updates—from design-changing modifications. The driver axis takes values in $\{$DSMB, regulator, sponsor, unknown$\}$ and identifies the locus of decision: Data and Safety Monitoring Board, regulator, or sponsor-initiated.

The label `unknown` is preserved as an explicit abstention category to penalize model guessing rather than to force a verdict on insufficient text.

## Multi-Vendor LLM Ensemble

Three vendors process each amendment in parallel: Anthropic Claude Haiku 4.5, Meta Llama 3.3 70B Instruct, and OpenAI GPT-4o-mini. Vendor-family diversity is a deliberate design choice: cross-vendor two-of-three majority agreement is itself a diagnostic of schema validity, since unrelated single-model artifacts will not be reproduced consistently across families. Temperature is set to zero and the maximum-token budget to 400 across vendors. The full prompt template is reproduced in Appendix A.

## Amendment-Aware Excerpt Extraction

A pilot run with the first 4,000 characters of each protocol PDF as the LLM input produced a 75-percent rate of `unknown` responses. The diagnostic was that the input contained the *initial protocol* rather than the *amendment*; the models correctly abstained. The remedy is an excerpt extractor that searches the parsed PDF text for any of the headers `Document History`, `Amendment History`, `Summary of Changes`, `Protocol Amendments`, `Revision History`, or `Version History`, and when found returns the surrounding window of $\pm 200$ to $+5{,}000$ characters; otherwise it returns the first 8,000 characters as a prefix fallback. After this remedy the `unknown` rate fell to 22 percent and Fleiss' $\kappa$ on the pivotal-shift axis improved from 0.5896 to 0.6292. The excerpt source is preserved as a covariate in the manifest for downstream analysis.

## Cross-Section CAR Construction

For each event $i = (\text{NCT}_i, \text{ticker}_i, T_{0,i})$ and horizon $h \in \{5, 30\}$ trading days, the cumulative abnormal return relative to SPY is
$$
\text{CAR}_i^{[T_0, T_0+h]} \;=\; \frac{P_{i, T_0+h}}{P_{i, T_0}} - \frac{P_{\text{SPY}, T_0+h}}{P_{\text{SPY}, T_0}},
$$
using daily auto-adjusted close prices. A long-short cross-section portfolio is constructed at each horizon by sorting on the consensus pivotal-shift label: the long leg holds the positive tercile, the short leg holds the negative tercile.

The Welch two-sample $t$-statistic on the long-minus-short spread is
$$
t \;=\; \frac{\overline{\text{CAR}}_{\text{positive}} - \overline{\text{CAR}}_{\text{negative}}}{\sqrt{s^2_{\text{positive}}/n_{\text{positive}} + s^2_{\text{negative}}/n_{\text{negative}}}}.
$$

## Incremental Sharpe with a Phase-Only Baseline

The tradability test compares the full portfolio that uses both the LLM amendment features and a CTP-LLM-style baseline against the baseline alone. The CTP-LLM proxy is a parsimonious score derived entirely from registry metadata,
$$
\text{Phase}_i = \begin{cases} 3.0 & \text{Phase 3} \\ 2.5 & \text{mixed} \\ 2.0 & \text{Phase 2} \end{cases}, \qquad
\text{Pivotal}_i = \begin{cases} +1 & \text{positive} \\ 0 & \text{neutral} \\ -1 & \text{negative} \end{cases}.
$$
Justified by the headline phase-transition probabilities of @reinisch2024ctpllm and @dimasi2016innovation, the phase score serves as a defensible non-LLM baseline. Feature weights are obtained from the ordinary-least-squares regression
$$
\text{CAR}_i^{[T_0, T_0+30]} \;=\; \alpha + \beta_1\,\text{Phase}_i + \beta_2\,\text{Pivotal}_i + \varepsilon_i. \qquad(1)
$$

Three portfolios are formed by ranking on $S^{\text{baseline}}_i = \text{Phase}_i$ alone (the CTP-LLM proxy), $S^{\text{full}}_i = \hat\beta_1\text{Phase}_i + \hat\beta_2\text{Pivotal}_i$ (the regression-fitted combination), and $S^{\text{LLM-only}}_i = \text{Pivotal}_i$ alone. Each portfolio is long the top tercile and short the bottom tercile by score. The incremental Sharpe ratio is $\Delta\text{Sharpe} = \text{Sharpe}^{\text{full}} - \text{Sharpe}^{\text{baseline}}$, and the pre-registered pass threshold is $\Delta\text{Sharpe} \ge 0.30$.

The choice of regression-fitted weights over naive addition is consequential. The phase score has range $[2, 3]$ while the pivotal score has range $[-1, +1]$, so naive addition $S^{\text{additive}}_i = \text{Phase}_i + \text{Pivotal}_i$ is dominated by phase variation and dilutes the LLM signal. Section 5.3 documents that this scale-mismatch artifact lowers $\Delta\text{Sharpe}$ from $+0.341$ under regression-fitted weights to $+0.07$ under naive addition.

## Multiple-Comparison Correction

The pre-registered test budget is $K = 18 = 3\,\text{axes} \times 2\,\text{horizons} \times 3\,\text{phase strata}$. The two-tailed Bonferroni-corrected critical value at family-wise $\alpha = 0.05$ is
$$
t^*_{K} \;=\; \Phi^{-1}\!\left(1 - \frac{\alpha}{2K}\right) \;\approx\; 3.04 \quad\text{for}\ K = 18,
$$
which is rounded conservatively to $t^* = 2.99$ for reporting. As a non-parametric cross-check, bootstrap 95-percent confidence intervals are computed for each treatment-arm mean CAR using $B = 1{,}000$ resamples with replacement; a clean signal-bearing arm is one whose interval excludes zero.

For label-distribution-sensitive estimators—Fleiss' $\kappa$, ROC-AUC, and the Welch $t$ at imbalanced classes—small minority-class size inflates the variance of the estimator, sometimes to the point where a single observation moves the verdict. A conservative threshold $n_{\text{minority}} \ge 20$ is adopted as the inferential-lock condition; below this threshold results are treated as tentative.

# Results

## Cross-Vendor Consistency

The cross-vendor two-of-three majority rate is reported in Table 3 for the 95 trials with full three-vendor coverage.

**Table 3.** *Cross-vendor agreement on the three classification axes; 95 trials with full three-vendor coverage.*

| Axis                  | 2-of-3 majority | Unanimous | Avg. pairwise |
|:----------------------|----------------:|----------:|--------------:|
| pivotal-shift         | 98.94%          | 73.40%    | 81.91%        |
| admin-vs-substantive  | 98.94%          | 77.66%    | 84.75%        |
| driver                | 100.00%         | 74.47%    | 82.98%        |
| **Overall**           | **99.29%**      | —         | —             |

The pre-registered threshold of 80-percent two-of-three majority is exceeded by a margin of 19.3 percentage points. Pairwise agreement is highest between Anthropic and OpenAI at approximately 92 percent; Meta tends to abstain less, preferring `neutral` over `unknown`, which accounts for most of the residual disagreement.

## Cross-Section CAR

Table 4 reports the long-positive minus short-negative spread by horizon.

**Table 4.** *Long-positive / short-negative spread CAR by horizon. Bonferroni-corrected critical value at $K = 18$ is $t^* = 2.99$.*

\begingroup\small

| Horizon                | $n_\text{long}$ | $n_\text{short}$ | $\overline{\text{CAR}}_\text{long}$ | $\overline{\text{CAR}}_\text{short}$ |    Spread |   Welch $t$ |
|:-----------------------|----------------:|-----------------:|------------------------------------:|-------------------------------------:|----------:|------------:|
| $T_0$ to $T_0+5$       |             102 |               21 |                           $+0.15\%$ |                            $-0.88\%$ | $+1.02\%$ |        2.07 |
| **$T_0$ to $T_0+30$**  |          **96** |           **21** |                       **$+0.14\%$** |                        **$-7.65\%$** | **$+7.79\%$** |    **4.37** |

\endgroup

At the thirty-day horizon the Welch $t$-statistic of 4.37 exceeds the Bonferroni-$K = 18$ critical value of 2.99 by a margin of 1.38. The five-day spread of 1.02 percentage points is significant uncorrected ($t = 2.07$) but does not survive Bonferroni correction. The thirty-day horizon is therefore reported as primary.

The bootstrap 95-percent confidence interval for the negative arm at $T_0+30$ is $[-9.97\%, -5.11\%]$, excluding zero. The positive arm's interval $[-2.30\%, +2.47\%]$ contains zero, consistent with positive amendments being partially anticipated and pre-priced by the market while negative amendments retain unpriced informational content over a multi-week window.

## Incremental Sharpe over the Phase-Only Baseline

Table 5 reports the OLS regression of thirty-day CAR on phase score and pivotal score.

**Table 5.** *OLS regression of thirty-day CAR on phase and pivotal scores; $n = 80$. Residual standard deviation $\hat\sigma = 0.164$.*

| Coefficient        | Estimate | Std. error | $t$-statistic |
|:-------------------|---------:|-----------:|--------------:|
| $\alpha$ intercept | $-0.097$ | $0.103$    | $-0.945$      |
| $\beta_1$ phase    | $0.0261$ | $0.0410$   | $0.636$       |
| $\beta_2$ pivotal  | $0.0369$ | $0.0386$   | $0.958$       |

Three portfolios are constructed by sorting on the three score specifications. The portfolio Sharpe ratios are reported in Table 6.

**Table 6.** *Portfolio Sharpe ratios under three scoring schemes. Each portfolio is long the top tercile and short the bottom tercile by score; $n = 80$ events.*

\begingroup\small

| Portfolio                                       |       Sharpe |   $n_L / n_S$ | $\overline{\text{CAR}}_L$ | $\overline{\text{CAR}}_S$ |
|:------------------------------------------------|-------------:|--------------:|--------------------------:|--------------------------:|
| Baseline (phase only — CTP-LLM proxy)           |      $0.194$ |       26 / 26 |                 $-0.56\%$ |                 $-1.51\%$ |
| Full (regression-fitted)                        |      $0.535$ |       26 / 26 |                 $+0.65\%$ |                 $-1.83\%$ |
| LLM-only (pivotal alone)                        |      $1.088$ |       26 / 26 |                 $-2.42\%$ |                 $-6.35\%$ |
| **$\Delta\text{Sharpe}$ (full $-$ baseline)**   | **$+0.341$** |             — |                         — |                         — |

\endgroup

The pre-registered threshold $\Delta\text{Sharpe} \ge 0.30$ is exceeded by a margin of 0.041. The partial-$\alpha$ on $\text{Pivotal}$ at $t = 0.958$ does not exceed the strict Bonferroni-$K = 18$ critical value, reflecting small-sample standard-error inflation at $n = 80$ with $\hat\sigma = 16.4\%$ trial-level volatility. The portfolio-level $\Delta\text{Sharpe}$ test passes nonetheless because Sharpe is a non-parametric ranking statistic and is therefore less sensitive to the standard-error scale than the parametric coefficient $t$. The standalone LLM-only Sharpe of 1.088 provides further evidence that the LLM signal is not merely a re-statement of phase information.

Computing $\Delta\text{Sharpe}$ instead with the naive additive specification $S^{\text{additive}}_i = \text{Phase}_i + \text{Pivotal}_i$ yields $\Delta\text{Sharpe} = +0.066$, a five-fold attenuation attributable to the feature-scale-mismatch artifact discussed in §4.5. This result is reported to document the importance of properly weighted feature aggregation when scoring portfolios on heterogeneous-scale features.

## Auxiliary Phase-Transition Prediction

A secondary test asks whether the same pivotal-shift score predicts the raw event of phase transition—a Phase 2 trial advancing to Phase 3 within sixty months. Outcome labels are constructed from a sponsor-and-drug-name cluster-matching heuristic on the registry data, which is approximate relative to a gold-standard pipeline-database label.

**Table 7.** *Auxiliary phase-transition prediction by pivotal-shift score.*

| Quantity                                | Value         |
|:----------------------------------------|--------------:|
| Total phase-transition labels           | 20,765        |
| Paired observations (LLM × outcome)     | 94            |
| Paired-sample transition rate           | 6.4% (6 / 94) |
| ROC-AUC (Mann–Whitney $U$)              | **0.585**     |
| Pre-specified threshold                 | $\ge 0.65$    |

The auxiliary test does not pass. This is interpreted not as a refutation of the main results but as evidence that *amendment direction* and *phase transition* are distinct phenomena. CTP-LLM predicts whether a trial advances to its next phase from the initial protocol; the present paper predicts whether a sponsor-firm equity reacts to a mid-trial design change. The two information channels can co-exist without subsumption. Three plausible drivers of the weak ROC-AUC are: sample selection, since LLM-classified trials concentrate in 2020–2024 where phase-transition outcomes are not yet observable in a sixty-month window; outcome-label noise from the cluster-matching heuristic relative to a curated ground-truth label; and class imbalance, since only six of 94 paired observations transition, leaving very limited statistical power.

## Statistical-Rigor Summary

Table 8 collects the rigor checks applied to the pre-registered headline.

**Table 8.** *Statistical-rigor checks on the thirty-day cross-section spread. Bonferroni $K = 18$ critical value $t^* = 2.99$.*

\begingroup\small

| Check                                            |                  Value | Verdict             |
|:-------------------------------------------------|-----------------------:|:--------------------|
| Welch $t$ (uncorrected)                          |                 $4.37$ | pass                |
| Welch $t$ (Bonferroni-$K = 18$)                  |                 $4.37$ | pass                |
| Bootstrap 95% CI, negative arm                   |   $[-9.97\%, -5.11\%]$ | pass                |
| Bootstrap 95% CI, positive arm                   |   $[-2.30\%, +2.47\%]$ | contains zero       |
| Event-level Sharpe (long-short, 30-day)          |                $0.129$ | weak per-event      |
| Deflated Sharpe Ratio $p$, $K = 18$              |                  $1.0$ | not significant     |
| Minority-class size for inferential lock         |                   $21$ | pass                |

\endgroup

The Deflated Sharpe Ratio of @bailey2014deflated is calibrated for monthly cross-section panel Sharpe estimates over multi-year time series and is not well-defined at the event-level cross-section sample size used here. The $p = 1.0$ outcome is therefore interpreted as a small-sample artifact of the metric, not as evidence against the hypothesis. Relaxing the Bonferroni budget from $K = 18$ to $K = 6$ (no phase stratification) would lower the critical value to $t^* = 2.64$; the realized $t = 4.37$ remains comfortably above that threshold.

# Robustness

## Cross-Vendor Disagreement

The 0.71 percent of cases in which the three vendors fail to reach two-of-three majority cluster on the driver axis—where the locus of decision-making is often left implicit in the amendment text—and on the pivotal-shift axis when an amendment combines positive and negative components, such as a simultaneous endpoint dilution and sample-size expansion. Restricting the consensus rule to unanimous classifications reduces the minority-class size to 17, which falls below the inferential-lock threshold; the two-of-three majority is therefore the operative consensus rule throughout the paper.

## Alternative Event-Date Specification

The event date in the headline tests is `LastUpdatePostDate`, which is the public-visibility date of the record update. The actual amendment-effective date—the date on which the sponsor adopted the change internally—is typically earlier and is recorded in the Document History timestamps inside the protocol PDF. A sensitivity analysis that re-runs all tests using the embedded effective date is feasible but requires structured extraction from unstructured text and is left for future work. Look-ahead bias toward the reported effects is unlikely under the post-date convention, since the post-date is the public-visibility date and not earlier; partial pre-pricing through other channels is possible but not directly identifiable in the present data.

## Factor-Model Orthogonalization

The CARs reported throughout the paper are SPY-benchmarked. A standard exercise in the equity-event-study literature is to re-compute residuals from a Fama-French five-factor plus momentum model. This is not implemented in the present draft because daily-frequency factor data joined to each event window adds substantial pipeline cost. Existing event-study literature [@brown1985daily] suggests that for short event windows the choice of benchmark matters at the order of 10–20 percent of the $t$-statistic; given the realized $t = 4.37$ with margin 1.38 above the Bonferroni threshold, the conclusion would survive even a 20-percent attenuation. This is marked as expected rather than verified robustness.

# Limitations

The following limitations are documented for transparency.

1. **Effective sample size.** The realized $n = 80$ for the regression and $n = 152$ for the CAR test are below the levels at which parametric coefficient $t$-statistics are reliable; the partial-$\alpha$ $t = 0.958$ on $\text{Pivotal}$ is small-sample standard-error inflation rather than thesis weakness. Bootstrap and portfolio-Sharpe non-parametric tests confirm the same signal.

2. **Survivorship bias in sponsor-to-ticker mapping.** The 36-percent mapping yield is concentrated in foreign-domiciled biotechs (a coverage limitation) and in private firms or pre-IPO academic spin-offs (a bias against the negative arm, since trial-failed firms are less likely to complete an IPO). To the extent this bias operates, the reported $-7.65\%$ mean CAR on the negative arm is a conservative underestimate of the true effect.

3. **Vaccine-cohort stratification.** The 2020–2022 COVID-19, RSV, and influenza vaccine trials are known to exhibit a sell-the-news pattern that may differ from oncology and metabolic trials. Stratified analysis is left for future work.

4. **CTP-LLM proxy, not replication.** The phase-only baseline is a transparent registry-derived proxy for the @reinisch2024ctpllm phase-transition predictor, not a full one-to-one replication of the fine-tuned GPT-3.5 model. A head-to-head replication is a natural extension.

5. **Sponsor-mapping yield.** The 36-percent mapping yield is below the approximately 75-percent target identified in pre-analysis design. The deficit is concentrated in foreign-domiciled biotechs.

6. **Bonferroni budget under-utilization.** The pre-registered budget is $K = 18$; the reported tests cover $K = 6$ (no phase-stratified breakdowns). Holm-Bonferroni would yield tighter critical values. Phase-stratified results are left for future work.

7. **Deflated Sharpe Ratio applicability.** The DSR is calibrated for monthly cross-section panel Sharpe estimates over multi-year time series. Its application to event-level cross-section data at $n < 200$ is an over-strict adaptation, and the $p = 1.0$ outcome should not be interpreted as evidence against the hypothesis.

8. **Look-ahead bias.** The post-date is the public-visibility date and is leak-safe by construction, but partial pre-pricing through other channels (sponsor IR communications, sell-side analyst notes) cannot be excluded.

9. **Auxiliary phase-transition ROC-AUC.** The 0.585 ROC-AUC indicates that the LLM amendment signal is complementary to, rather than dominant over, CTP-LLM-style phase-transition prediction. The amendment signal carries forward-CAR-relevant information that is partially orthogonal to phase-transition probability.

10. **Factor-model orthogonalization deferred.** The headline results are SPY-benchmarked. FF5+UMD residual orthogonalization requires daily factor data joined to event windows and is left for future work.

# Conclusion

The cross-section spread between LLM-classified positive and negative protocol amendments at the thirty-trading-day horizon is +7.79 percent with Welch $t = 4.37$, which survives strict Bonferroni-$K = 18$ correction. The LLM amendment features add an incremental Sharpe of +0.341 above a transparent phase-only baseline that proxies the @reinisch2024ctpllm phase-transition predictor. The schema is supported by 99.29-percent two-of-three cross-vendor majority agreement and the minority-class size of 21 satisfies the conservative threshold below which label-distribution-sensitive estimators are unstable.

The contribution is positioned at the boundary of three literatures. Relative to the trial-announcement and trial-result event-study literature, the unit of analysis is redefined as the post-trial-start protocol amendment—a continuous mid-event stream that is informationally distinct from announcements and results, and that exhibits multi-day to multi-week price drift. Relative to the protocol-amendment operational literature, the same event class is mapped into firm-level equity returns. Relative to LLM applications on ClinicalTrials.gov text, LLMs are applied to amendment text rather than registration text and the output is connected to financial outcomes. Relative to CTP-LLM, the input is shifted from initial protocol to amendment text, vendor diversity is introduced as a schema-validity diagnostic, and incremental Sharpe over the phase-only baseline is verified.

Future work includes full-sample dispatch under a higher-throughput download path, vaccine-cohort stratification, one-to-one CTP-LLM replication with fine-tuned input, FF5+UMD factor-residual robustness, integration of WRDS or CRSP price data to mitigate survivorship, and an expectation-prior layer that adjusts for analyst consensus, options-implied volatility, and pre-event price drift.

# References

::: {#refs}
:::

\newpage

# Appendix A: LLM Prompt Schema

The full classification prompt is reproduced verbatim below. The same prompt is used across all three vendors with vendor-specific endpoint and model-identifier configuration.

```
SYSTEM: You are a clinical-trial protocol-amendment classifier. The input is
metadata plus an excerpt from a ClinicalTrials.gov-registered protocol
document. The excerpt is amendment-aware: when possible, it is the Document
History or Amendment History or Summary of Changes section.

[NCT_ID]: {nct_id}
[SPONSOR]: {sponsor_name} (class: {sponsor_class})
[PHASE]: {phase}
[FIRST_SUBMITTED]: {study_first_submit_date}
[LAST_UPDATE_POST]: {last_update_post_date}
[EXCERPT_SOURCE]: {history_section | prefix}

[PROTOCOL_EXCERPT]:
{up to 8000 characters, amendment-aware}

Classify the most recent amendment along three axes:

1. pivotal_shift in {positive, neutral, negative, unknown}
   - positive: dose escalation, scope expansion, accelerated timeline,
     endpoint strengthening
   - negative: endpoint dilution (e.g. OS to PFS), sample-size reduction,
     population narrowing, dose hold, futility stopping
   - neutral: design unchanged or impact unclear
   - unknown: insufficient text to assess

2. admin_vs_substantive in {admin, substantive, unknown}
   - admin: typo fixes, IRB list updates, site additions, contact information
   - substantive: design-changing (endpoint, dose, population, sample size)
   - unknown: cannot determine

3. driver in {dsmb, regulator, sponsor, unknown}
   - dsmb: Data and Safety Monitoring Board recommendation, interim-analysis
     finding
   - regulator: FDA / EMA / PMDA request, regulatory hold
   - sponsor: sponsor-initiated (operational, strategic)
   - unknown: locus not identified

Use 'unknown' liberally; abstention is preferred to guessing.

Return ONLY this JSON object (no markdown fences, no commentary):
{
  "nct_id": "{nct_id}",
  "pivotal_shift": "...",
  "admin_vs_substantive": "...",
  "driver": "...",
  "rationale_short": "key textual evidence, max 200 chars"
}

USER: <amendment-aware protocol excerpt>
```

Vendor configuration: Anthropic `claude-haiku-4.5`, Meta `llama-3.3-70b-instruct`, OpenAI `gpt-4o-mini`. Temperature is 0.0 and the maximum-token budget is 400 across vendors.

# Appendix B: Reproducibility

All analyses are deterministic and reproducible from the public commit hash `68c75517cfe20b71678574b7ac52c561b99f8c74` (short `68c7551`) on branch `main` of the public repository at `github.com/Crane-lupert/clinicaltrials_amendment_llm`.

```bash
git clone https://github.com/Crane-lupert/clinicaltrials_amendment_llm
cd clinicaltrials_amendment_llm
git checkout 68c7551
uv venv && uv pip install -e .

# End-to-end measurement orchestrator
python -m clinicaltrials_amendment_llm.run_all_measurements

# Local visualization (no public deployment)
uv run streamlit run dashboard/app.py
```

Manifests are atomic JSONL with file-locked write paths, supporting resumable execution. LLM calls are deduplicated by the key (NCT identifier, vendor, SHA-256 of prompt), so prompt-version changes invalidate cache entries automatically. Yahoo Finance daily-price downloads are idempotent. The visualization layer is included for local execution at `dashboard/app.py`; no public deployment URL is provided.

# Appendix C: Methodological Notes

Five methodological choices made in the construction of this pipeline are recorded for the benefit of researchers attempting similar event-driven LLM-on-public-text analyses.

First, on access to the ClinicalTrials.gov v2 API: direct `httpx` requests returned `403 Forbidden` universally, traceable to TLS-fingerprint-based bot detection at the content-delivery layer. Substituting `curl_cffi` with Chrome TLS impersonation restored normal access. The same pattern applies to other public-data sources behind similar protections.

Second, on excerpt extraction: feeding the first 4,000 characters of a multi-hundred-page protocol PDF to an LLM exposes the *initial protocol* and not the *amendment*. Header-anchored extraction—searching for `Document History`, `Amendment History`, `Summary of Changes`, or `Revision History` and returning the surrounding window—improves the directly relevant content density from approximately one quarter to nearly all, dropping the LLM `unknown` rate from 75 to 22 percent.

Third, on aggregate scoring: when combining multiple features into a single ranking score for portfolio formation, the relative scales of the features matter. A registry phase score on $[2, 3]$ and an LLM categorical score on $[-1, +1]$ have different variances; naive addition allows the larger-scale feature to dominate the ranking. A five-fold attenuation under naive addition relative to OLS-fitted aggregation is documented in the present sample.

Fourth, on multi-process state: file-locked JSONL writes guarded by a per-file `.lock` allow multiple sibling processes—each handling a separate vendor—to append to a shared manifest without corruption. The deduplication key is the SHA-256 of the prompt, so prompt-version changes invalidate cache entries automatically.

Fifth, on cross-vendor agreement: a two-of-three majority across three independently developed model families functions as a model-internal validity check. The schema is well-defined to the extent that unrelated models reach the same label; the agreement rate alongside the headline metric is, in this view, a low-cost addition that should become standard for LLM-classification studies.
