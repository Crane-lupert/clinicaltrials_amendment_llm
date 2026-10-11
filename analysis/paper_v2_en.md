---
title: "Protocol Amendments and Cross-Section Pharmaceutical Stock Returns: A Multi-Vendor LLM Event Study from ClinicalTrials.gov"
author: "Ahn Hyun"
date: "May 2026 (revised 11 October 2026)"
abstract: |
  This study examines whether post-trial-start protocol amendments registered on ClinicalTrials.gov carry directional information about forward sponsor-firm equity returns at the cross-section. The empirical setting is the fifteen-year panel 2010–2024 of 25,000 industry-sponsored Phase 2 and Phase 3 trial records. To convert unstructured amendment text into a tractable structured signal at scale, a three-vendor ensemble (Anthropic Claude Haiku 4.5, Meta Llama 3.3 70B Instruct, OpenAI GPT-4o-mini) extracts a three-axis classification of each trial's most recent amendment text—pivotal-shift direction, administrative-versus-substantive scope, and decision-driver locus. After mapping sponsor names to listed-equity tickers and deduplicating re-classification rows to obtain one observation per unique amendment event, the matched panel contains 80 unique-amendment cumulative-abnormal-return observations. At the thirty-trading-day horizon, negative pivotal-shift amendments ($n = 4$) underperform SPY by 7.34 percent on average while positive pivotal-shift amendments ($n = 16$) return $+0.14$ percent, a cross-section spread of $+7.48$ percentage points. Welch's $t$-statistic on this strict positive-versus-negative spread is $1.69$ ($\mathrm{df} \approx 10$), which does not exceed the conventional $\alpha = 0.05$ threshold or the Bonferroni-corrected critical value of $2.99$ at $K = 18$; the directional effect is therefore documented as a *preliminary scout-feasible candidate* rather than a deployed alpha. An earlier draft of this paper reported $\text{Welch } t = 4.37$ under Bonferroni-$K = 18$ strict-pass, computed on row-iteration aggregation of the per-event re-classification manifest; that aggregation violated Welch's independence assumption and is corrected in this revision (see §7 Post-Publication Self-Correction). Relative to a transparent phase-only baseline that proxies the @reinisch2024ctpllm phase-transition predictor, the incremental-Sharpe test does not support an incremental contribution. An earlier version reported an incremental Sharpe ratio of $+0.341$; that figure was a difference of pooled $t$-statistics built with in-sample regression weights, it is not distinguishable from a permutation null ($p \approx 0.68$), and it turns negative with leave-one-out weights ($-0.78$). It is withdrawn (see Post-Publication Self-Correction #2). Cross-vendor two-of-three majority agreement is $99.29$ percent across the three axes (95 trials with full coverage). The contribution is positioned at the boundary of three literatures. Existing trial-event–to–return work concentrates on trial *announcements* and *results* [@pinto2023bert; @arxiv2208_07248; @wang2022pmc]; the protocol-amendment literature is operational and cost-focused [@tufts2024amendments]; and concurrent LLM applications to ClinicalTrials.gov text address orthogonal classification tasks [@liu2025innovative]. To my knowledge this is the first paper to use post-trial-start protocol amendments as the unit of cross-section equity-return prediction; whether the resulting signal is incremental over a CTP-LLM-style phase-transition baseline is tested and not supported at the present sample size. The full pipeline runs from the public ClinicalTrials.gov registry to the final alpha summary using only public data sources, and the extraction prompts, statistical scripts, and a locally runnable visualization dashboard are released in the public repository at the commit hash listed in Appendix B.
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

This study makes four contributions. First, the unit of equity-event analysis is redefined as the post-trial-start protocol amendment, distinct from announcements and results both in timing and in the textual richness of the change description itself. Second, rather than reduce amendment text to a binary positive-or-negative sentiment, a three-axis structured classification is extracted—pivotal-shift, administrative-versus-substantive, and decision-driver locus—enabling separate testing of mechanism components. Third, the extraction is performed by a three-vendor ensemble and the cross-vendor majority-agreement rate is treated as a schema-validity diagnostic, protecting against single-vendor classification artifacts. Fourth, building on the phase-transition prediction work of @reinisch2024ctpllm, a transparent phase-only baseline is constructed from registry metadata alone and the LLM amendment features are tested for *incremental* portfolio Sharpe ratio above this baseline; the test does not find an incremental contribution (Post-Publication Self-Correction #2).

The principal empirical findings are these. Under proper deduplication by unique amendment event, the cross-section spread between the long-positive and short-negative cohorts at the thirty-trading-day horizon is $+7.48$ percentage points—negative pivotal-shift amendments (n = 4 unique events) underperform SPY by 7.34 percent on average while positive pivotal-shift amendments (n = 16 unique events) return $+0.14$ percent. Welch's $t$-statistic on this spread is $1.69$, which does not exceed the conventional $\alpha = 0.05$ threshold and does not exceed the strict Bonferroni-corrected critical value of $2.99$ at $K = 18$; the directional effect is therefore documented as a preliminary scout-feasible candidate rather than a deployed alpha. The LLM amendment features do not add a demonstrable incremental Sharpe over the phase-only baseline: the previously reported $+0.341$ is withdrawn because it was a difference of pooled $t$-statistics with in-sample weights, indistinguishable from a permutation null ($p \approx 0.68$) and negative out of sample; the standalone pivotal-shift statistic of $1.088$ is the same pooled $t$-statistic (per-event Sharpe $0.15$) and is not evidence of a standalone signal (Post-Publication Self-Correction #2). Cross-vendor two-of-three majority agreement is $99.29$ percent across the three classification axes (95 trials with full coverage). The minority-class size of 4 unique negative-pivotal-shift events falls below the pre-registered $n \ge 20$ inferential-lock threshold; results are therefore reported as tentative on the strict-significance axis, but the direction and magnitude of the cross-section spread are preserved relative to the row-aggregated draft of this paper. A secondary test on the same LLM features for raw phase-transition prediction yields ROC-AUC of 0.586, below the pre-registered 0.65 threshold; this auxiliary failure is interpreted in §5.4 as evidence that the amendment direction signal is *complementary* to the @reinisch2024ctpllm phase-transition signal rather than a stronger version of it.

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
| LLM classification rows across vendors (raw manifest)          |       343 | Classification-distribution analysis |
| Trials with full three-vendor coverage                         |        95 | Cross-vendor consistency (§5.1)      |
| Unique-amendment CAR observations (deduplicated)               |        80 | Cross-section CAR test (§5.2)        |
| Regression-ready unique amendments                             |        80 | Incremental Sharpe (§5.3)            |
| Minority-class unique amendments (negative pivotal-shift)      |         4 | Inferential lock (§5.5, FAIL)        |

\endgroup

Each unique amendment event is identified by the pair (NCT identifier, event date). The CAR manifest stores multiple rows per event because of re-classification runs across vendors and prompt versions; under proper Welch-style independent-observation inference the rows must be collapsed to one observation per event, with a consensus label computed as the most-common non-unknown pivotal-shift label across the rows for that amendment. An earlier draft of this paper iterated rows directly, treating each re-classification as an independent observation; the corrected aggregation is used throughout this revision and the discrepancy is documented in §7.

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

Inference is performed at the unique-amendment level. Each amendment event is identified by the pair (NCT identifier, event date), and a single CAR observation is associated with each unique event. The CAR manifest stores multiple rows per event because of re-classification runs across vendors and prompt versions; under Welch's independent-observation assumption these rows must be collapsed to one observation per event before the test, with a consensus pivotal-shift label computed as the most-common non-unknown vote across rows for that event. §7 documents that an earlier draft of this paper iterated rows directly and over-stated the Welch $t$-statistic; the corrected procedure is the one specified here.

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

Three portfolios are formed by ranking on $S^{\text{baseline}}_i = \text{Phase}_i$ alone (the CTP-LLM proxy), $S^{\text{full}}_i = \hat\beta_1\text{Phase}_i + \hat\beta_2\text{Pivotal}_i$ (the regression-fitted combination), and $S^{\text{LLM-only}}_i = \text{Pivotal}_i$ alone. Each portfolio is long the top tercile and short the bottom tercile by score. The incremental Sharpe ratio is $\Delta\text{Sharpe} = \text{Sharpe}^{\text{full}} - \text{Sharpe}^{\text{baseline}}$, and the pre-registered pass threshold is $\Delta\text{Sharpe} \ge 0.30$. As implemented, each "Sharpe" is the mean divided by the standard deviation of the 52 pooled long and sign-flipped short event returns, multiplied by $\sqrt{52}$, which is a one-sample $t$-statistic rather than a Sharpe ratio, and $\hat\beta_1, \hat\beta_2$ are estimated on the same events that are ranked. Post-Publication Self-Correction #2 explains why this statistic cannot test the threshold.

An earlier version of this paragraph stated that naive addition $S^{\text{additive}}_i = \text{Phase}_i + \text{Pivotal}_i$ is dominated by phase variation and lowers $\Delta\text{Sharpe}$ from $+0.341$ under regression-fitted weights to $+0.07$. That comparison mixed two samples and is withdrawn: on the same $n = 80$ sample the additive specification gives $+0.427$, and on the 70-event sample that produced $+0.07$ the regression-fitted specification gives $-0.028$. The phase range ($1$) is also smaller than the pivotal range ($2$). See Post-Publication Self-Correction #2.

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

**Table 4.** *Long-positive / short-negative spread CAR by horizon at the unique-amendment level (dedup-corrected). Bonferroni-corrected critical value at $K = 18$ is $t^* = 2.99$; uncorrected $\alpha = 0.05$ threshold is $t^* = 2.0$.*

\begingroup\small

| Horizon                | $n_\text{long}$ | $n_\text{short}$ | $\overline{\text{CAR}}_\text{long}$ | $\overline{\text{CAR}}_\text{short}$ |    Spread |   Welch $t$ |
|:-----------------------|----------------:|-----------------:|------------------------------------:|-------------------------------------:|----------:|------------:|
| **$T_0$ to $T_0+30$**  |          **16** |            **4** |                       **$+0.14\%$** |                        **$-7.34\%$** | **$+7.48\%$** |    **1.69** |

\endgroup

At the thirty-day horizon the Welch $t$-statistic of $1.69$ does not exceed the conventional uncorrected $\alpha = 0.05$ threshold of $2.0$, and is therefore well below the Bonferroni-$K = 18$ critical value of $2.99$. The directional effect—negative pivotal-shift amendments underperforming SPY by $7.34$ percent on average while positive pivotal-shift amendments return $+0.14$ percent—is preserved relative to an earlier draft of this paper, with the spread changing only marginally from $+7.79$ percentage points to $+7.48$ percentage points. What does not survive the dedup correction is the strict-significance certificate: the earlier draft reported Welch $t = 4.37$ under row-iteration aggregation that violated Welch's independent-observation assumption. The correction is documented in §7.

For comparison, under the audit-only row-iteration aggregation, the current data state yields $n_{\text{long-raw}} = 144$ and $n_{\text{short-raw}} = 33$ rows with spread $+7.68\%$ and Welch $t = 5.42$; that aggregation is preserved in `analysis/rigor_pass.json` under `pre_dedup_raw_for_audit` for transparency only and is not used for inference because the same amendment contributes multiple non-independent rows to each leg.

A bootstrap 95-percent confidence interval on the negative arm is not reported in the dedup-corrected results because the minority class of $n = 4$ falls below the $n \ge 5$ minimum that the bootstrap implementation in `rigor_pass.py` requires for stable percentile estimation. The bootstrap CI of $[-9.97\%, -5.11\%]$ reported in the earlier draft was computed on the row-aggregated negative bucket ($n = 21$ rows) and shares the same independence-violation artifact as the inflated Welch $t$; it is withdrawn together with the inflated test.

## Incremental Sharpe over the Phase-Only Baseline

Table 5 reports the OLS regression of thirty-day CAR on phase score and pivotal score. The regression dataset is at the unique-amendment level by construction: rows are aggregated into a dictionary keyed on the NCT identifier before the design matrix is built, so the dedup discussed in §5.2 and §7 is enforced automatically and the regression headline numbers are unaffected by the row-aggregation artifact that affected the earlier draft's cross-section $t$-statistic.

**Table 5.** *OLS regression of thirty-day CAR on phase and pivotal scores at the unique-amendment level; $n = 80$. Residual standard deviation $\hat\sigma = 0.164$.*

| Coefficient        | Estimate | Std. error | $t$-statistic |
|:-------------------|---------:|-----------:|--------------:|
| $\alpha$ intercept | $-0.097$ | $0.103$    | $-0.945$      |
| $\beta_1$ phase    | $0.0261$ | $0.0410$   | $0.636$       |
| $\beta_2$ pivotal  | $0.0369$ | $0.0386$   | $0.958$       |

Three portfolios are constructed by sorting on the three score specifications. The portfolio Sharpe ratios are reported in Table 6.

**Table 6.** *Portfolio statistics under three scoring schemes. Each portfolio is long the top tercile and short the bottom tercile by score; $n = 80$ events. The column labelled "Sharpe" in earlier versions is mean/sd $\times \sqrt{52}$ over the pooled long and sign-flipped short events, i.e. a one-sample $t$-statistic; the per-event Sharpe is shown alongside. Weights of the full score are in-sample OLS estimates. Corrected 11 October 2026 (Post-Publication Self-Correction #2).*

\begingroup\small

| Portfolio                                       | Pooled $t$ (was "Sharpe") | Per-event Sharpe |   $n_L / n_S$ | $\overline{\text{CAR}}_L$ | $\overline{\text{CAR}}_S$ |
|:------------------------------------------------|------------:|------------:|--------------:|--------------------------:|--------------------------:|
| Baseline (phase only — CTP-LLM proxy)           |     $0.194$ |     $0.027$ |       26 / 26 |                 $-0.56\%$ |                 $-1.51\%$ |
| Full (regression-fitted, in-sample weights)     |     $0.535$ |     $0.074$ |       26 / 26 |                 $+0.65\%$ |                 $-1.83\%$ |
| LLM-only (pivotal alone)                        |     $1.088$ |     $0.151$ |       26 / 26 |                 $-2.42\%$ |                 $-6.35\%$ |
| Difference (full $-$ baseline)                  | $+0.341$ (not a pass; withdrawn) | $+0.047$ | — | — | — |

\endgroup

An earlier version stated that the pre-registered threshold $\Delta\text{Sharpe} \ge 0.30$ is exceeded by a margin of 0.041 and that the test passes because Sharpe is a non-parametric ranking statistic. Both statements are withdrawn. The statistic is a parametric pooled $t$-statistic, not a ranking statistic; with weights fitted on the same events, $68\%$ of permutation-null draws reach $+0.341$; with leave-one-out weights the difference is $-0.78$; and because scores take few distinct values, the tercile cut falls inside tied groups whose order is set by the manifest (random tie order: median $+0.28$, 90\% range $-0.62$ to $+1.15$). The partial-$\alpha$ on $\text{Pivotal}$ at $t = 0.958$ does not reach the uncorrected or the Bonferroni-$K = 18$ critical value. The pre-registered incremental-Sharpe test is therefore not passed, and the LLM-only statistic of 1.088 is not evidence of a standalone signal.

An earlier version reported that the naive additive specification $S^{\text{additive}}_i = \text{Phase}_i + \text{Pivotal}_i$ yields $\Delta\text{Sharpe} = +0.066$, a five-fold attenuation attributed to feature-scale mismatch. The $+0.066$ was computed on an earlier sample of 70 events. On the present 80-event sample the additive specification gives $+0.427$, higher than the regression-fitted $+0.341$, and on the 70-event sample the regression-fitted value was $-0.028$. The attenuation claim is withdrawn.

## Auxiliary Phase-Transition Prediction

A secondary test asks whether the same pivotal-shift score predicts the raw event of phase transition—a Phase 2 trial advancing to Phase 3 within sixty months. Outcome labels are constructed from a sponsor-and-drug-name cluster-matching heuristic on the registry data, which is approximate relative to a gold-standard pipeline-database label.

**Table 7.** *Auxiliary phase-transition prediction by pivotal-shift score.*

| Quantity                                | Value         |
|:----------------------------------------|--------------:|
| Total phase-transition labels           | 20,765        |
| Paired observations (LLM × outcome)     | 94            |
| Paired-sample transition rate           | 6.4% (6 / 94) |
| ROC-AUC (Mann–Whitney $U$)              | **0.586**     |
| Pre-specified threshold                 | $\ge 0.65$    |

The auxiliary test does not pass. This is interpreted not as a refutation of the main results but as evidence that *amendment direction* and *phase transition* are distinct phenomena. CTP-LLM predicts whether a trial advances to its next phase from the initial protocol; the present paper predicts whether a sponsor-firm equity reacts to a mid-trial design change. The two information channels can co-exist without subsumption. Three plausible drivers of the weak ROC-AUC are: sample selection, since LLM-classified trials concentrate in 2020–2024 where phase-transition outcomes are not yet observable in a sixty-month window; outcome-label noise from the cluster-matching heuristic relative to a curated ground-truth label; and class imbalance, since only six of 94 paired observations transition, leaving very limited statistical power.

## Statistical-Rigor Summary

Table 8 collects the rigor checks applied to the pre-registered headline.

**Table 8.** *Statistical-rigor checks on the thirty-day cross-section spread under unique-amendment dedup. Bonferroni $K = 18$ critical value $t^* = 2.99$; uncorrected $\alpha = 0.05$ threshold $t^* = 2.0$.*

\begingroup\small

| Check                                            |                Value | Verdict             |
|:-------------------------------------------------|---------------------:|:--------------------|
| Welch $t$ (uncorrected)                          |               $1.69$ | fail                |
| Welch $t$ (Bonferroni-$K = 18$)                  |               $1.69$ | fail                |
| Bootstrap 95% CI, negative arm                   |       not computable | $n_{\text{neg}}=4<5$ |
| Event-level Sharpe (long-short, 30-day)          |              $0.153$ | weak per-event      |
| Deflated Sharpe Ratio $p$, $K = 18$              |                $1.0$ | not significant     |
| Minority-class size for inferential lock         |                  $4$ | fail ($n < 20$)     |

\endgroup

None of the strict-inference checks pass under the corrected unique-amendment aggregation. The Welch $t$-statistic of $1.69$ does not reach uncorrected $\alpha = 0.05$ ($t^* = 2.0$); the Bootstrap 95-percent CI on the negative arm is not computable at $n_{\text{neg}} = 4$ because the implementation requires $n \ge 5$ for stable percentile estimation; the pre-registered $n_{\text{minority}} \ge 20$ inferential-lock threshold is not met. The Deflated Sharpe Ratio of @bailey2014deflated is calibrated for monthly cross-section panel Sharpe estimates over multi-year time series and is not well-defined at the event-level cross-section sample size used here, so the $p = 1.0$ outcome is interpreted as a small-sample artifact of the metric rather than as evidence against the hypothesis. Relaxing the Bonferroni budget from $K = 18$ to $K = 6$ (no phase stratification) would lower the critical value to $t^* = 2.64$; the realized $t = 1.69$ remains below that threshold as well.

The directional effect—$+7.48$ percentage points spread between positive and negative pivotal-shift amendments at the thirty-day horizon—is preserved relative to the inflated-significance draft, but no strict-inference check passes at the current minority-class size. Restoring the strict-significance certificate would require either expanding the labeled-amendment sample to push $n_{\text{negative}}$ above the conservative $n \ge 20$ floor (estimated under current pivotal-shift base rates at roughly $400$ to $500$ additional unique amendment events), or adopting an alternative inferential framework (e.g.\ a permutation test or a hierarchical posterior on the spread) that is better-suited to the minority-class regime.

# Robustness

## Cross-Vendor Disagreement

The 0.71 percent of cases in which the three vendors fail to reach two-of-three majority cluster on the driver axis—where the locus of decision-making is often left implicit in the amendment text—and on the pivotal-shift axis when an amendment combines positive and negative components, such as a simultaneous endpoint dilution and sample-size expansion. Restricting the consensus rule to unanimous classifications further reduces the labeled subsample and is therefore not adopted; the two-of-three majority is the operative consensus rule throughout the paper. Both consensus rules yield a unique-amendment minority class well below the pre-registered $n \ge 20$ floor at the current sample size, which is the relevant inferential constraint discussed in §5.6 and §7.

## Alternative Event-Date Specification

The event date in the headline tests is `LastUpdatePostDate`, which is the public-visibility date of the record update. The actual amendment-effective date—the date on which the sponsor adopted the change internally—is typically earlier and is recorded in the Document History timestamps inside the protocol PDF. A sensitivity analysis that re-runs all tests using the embedded effective date is feasible but requires structured extraction from unstructured text and is left for future work. Look-ahead bias toward the reported effects is unlikely under the post-date convention, since the post-date is the public-visibility date and not earlier; partial pre-pricing through other channels is possible but not directly identifiable in the present data.

## Factor-Model Orthogonalization

The CARs reported throughout the paper are SPY-benchmarked. A standard exercise in the equity-event-study literature is to re-compute residuals from a Fama-French five-factor plus momentum model. This is not implemented in the present draft because daily-frequency factor data joined to each event window adds substantial pipeline cost. Existing event-study literature [@brown1985daily] suggests that for short event windows the choice of benchmark matters at the order of $10$ to $20$ percent of the $t$-statistic; under the dedup-corrected Welch $t = 1.69$ a $20$-percent attenuation would not change the verdict because the test is already below uncorrected $\alpha = 0.05$. The factor-model exercise is therefore reframed as a future-work item that would be informative chiefly under a larger labeled-amendment sample where the dedup-corrected test is closer to the conventional threshold.

# Limitations

The following limitations are documented for transparency.

1. **Effective sample size.** The realized $n = 80$ unique-amendment observations for both the cross-section CAR test and the OLS regression are below the levels at which parametric coefficient $t$-statistics are reliable, and the minority-class size of $4$ unique negative-pivotal-shift amendments is far below the conservative $n \ge 20$ inferential-lock threshold. The directional spread of $+7.48$ percentage points is documented as a preliminary scout-feasible candidate rather than a deployed alpha. The partial-$\alpha$ $t = 0.958$ on $\text{Pivotal}$ in the OLS regression does not reach significance; the portfolio-level statistics previously cited as non-parametric support ($\Delta = +0.341$, pivotal-only $1.088$) are pooled $t$-statistics with in-sample weights and are withdrawn as evidence (Post-Publication Self-Correction #2).

2. **Survivorship bias in sponsor-to-ticker mapping.** The 36-percent mapping yield is concentrated in foreign-domiciled biotechs (a coverage limitation) and in private firms or pre-IPO academic spin-offs (a bias against the negative arm, since trial-failed firms are less likely to complete an IPO). To the extent this bias operates, the reported $-7.34\%$ mean CAR on the negative arm is a conservative underestimate of the true effect.

3. **Vaccine-cohort stratification.** The 2020–2022 COVID-19, RSV, and influenza vaccine trials are known to exhibit a sell-the-news pattern that may differ from oncology and metabolic trials. Stratified analysis is left for future work.

4. **CTP-LLM proxy, not replication.** The phase-only baseline is a transparent registry-derived proxy for the @reinisch2024ctpllm phase-transition predictor, not a full one-to-one replication of the fine-tuned GPT-3.5 model. A head-to-head replication is a natural extension.

5. **Sponsor-mapping yield.** The 36-percent mapping yield is below the approximately 75-percent target identified in pre-analysis design. The deficit is concentrated in foreign-domiciled biotechs.

6. **Bonferroni budget under-utilization.** The pre-registered budget is $K = 18$; the reported tests cover $K = 6$ (no phase-stratified breakdowns). Holm-Bonferroni would yield tighter critical values. Phase-stratified results are left for future work.

7. **Deflated Sharpe Ratio applicability.** The DSR is calibrated for monthly cross-section panel Sharpe estimates over multi-year time series. Its application to event-level cross-section data at $n < 200$ is an over-strict adaptation, and the $p = 1.0$ outcome should not be interpreted as evidence against the hypothesis.

8. **Look-ahead bias.** The post-date is the public-visibility date and is leak-safe by construction, but partial pre-pricing through other channels (sponsor IR communications, sell-side analyst notes) cannot be excluded.

9. **Auxiliary phase-transition ROC-AUC.** The 0.585 ROC-AUC indicates that the LLM amendment signal is complementary to, rather than dominant over, CTP-LLM-style phase-transition prediction. The amendment signal carries forward-CAR-relevant information that is partially orthogonal to phase-transition probability.

10. **Factor-model orthogonalization deferred.** The headline results are SPY-benchmarked. FF5+UMD residual orthogonalization requires daily factor data joined to event windows and is left for future work.

11. **Row-aggregation independence violation in earlier draft.** An earlier draft of this paper reported the cross-section CAR test on row-iteration aggregation of the per-event re-classification manifest (`data/manifest_car.jsonl`), treating each re-classification row as an independent observation in Welch's two-sample test. This violated Welch's independent-observation assumption and inflated the test statistic. The present revision uses one observation per unique amendment event identified by the pair (NCT identifier, event date), with a consensus pivotal-shift label computed as the most-common non-unknown vote across the rows for that amendment. The directional effect is preserved while the strict-significance certificate is withdrawn; the full audit is recorded in §7.

# Post-Publication Self-Correction

## Row-Aggregation Dedup Audit (2026-05-17)

An earlier version of this working paper, distributed under the title *Protocol Amendments and Cross-Section Pharmaceutical Stock Returns: A Bonferroni-Strict Event Study from ClinicalTrials.gov*, reported a Welch's $t$-statistic of $4.37$ on the long-positive minus short-negative cross-section spread at the thirty-trading-day horizon, with the headline summary $n_{\text{long}} = 96$, $n_{\text{short}} = 21$, spread $+7.79$ percentage points, Bonferroni-$K = 18$ critical value $t^* = 2.99$, and a verdict of \emph{strict Bonferroni-PASS} with margin $1.38$. Reproduction of those numbers from the public commit failed.

### What went wrong

The CAR manifest at `data/manifest_car.jsonl` stores one row per (event, classification run) pair. Each unique amendment event identified by the pair (NCT identifier, event date) is therefore represented by multiple rows—typically five to ten—because the LLM extraction was re-dispatched across vendors and prompt versions during the pipeline build-out. The implementation of the cross-section CAR test in `src/clinicaltrials_amendment_llm/rigor_pass.py` and the day-14 mid-checkpoint script `day14_midcheckpoint.py` iterated this manifest row-by-row and appended each row's CAR value to its label's bucket. The same amendment's CAR was therefore counted five-to-ten times against the negative or positive bucket, depending on how many re-classification rows survived in the final manifest. Welch's two-sample $t$-statistic assumes independent observations; replicated rows of the same event are not independent and the standard-error denominator is artificially shrunk by approximately the square-root of the per-event row multiplicity.

### Magnitude of the inflation

\begingroup\small

| Quantity                                  | Row aggregation (earlier draft) | Dedup correction (this revision) |
|:------------------------------------------|--------------------------------:|---------------------------------:|
| Source-data cut                            | `bcf2144` (Layer A LOCKED commit) | `c438dc6` (current main HEAD)    |
| $n_{\text{long}}$                          | 96 (rows)                       | 16 (unique amendments)           |
| $n_{\text{short}}$                         | 21 (rows)                       | 4 (unique amendments)            |
| Mean CAR, long                             | $+0.14\%$                       | $+0.14\%$                        |
| Mean CAR, short                            | $-7.65\%$                       | $-7.34\%$                        |
| Cross-section spread                       | $+7.79\%$                       | $+7.48\%$                        |
| Welch $t$                                  | $4.37$                          | $1.69$                           |
| Welch standard-error (long − short)        | $\approx 1.78\%$                | $\approx 4.42\%$                 |
| Degrees of freedom (Welch–Satterthwaite)   | $\approx 76$                    | $\approx 10$                     |
| Bonferroni-$K = 18$ critical $t^* = 2.99$  | PASS                            | FAIL                             |
| Uncorrected $\alpha = 0.05$ ($t^* = 2.0$)  | PASS                            | FAIL                             |
| Minority-class lock $n_{\text{neg}} \ge 20$| PASS ($n = 21$ rows)            | FAIL ($n = 4$ unique amendments) |

\endgroup

The direction of the signal and the magnitude of the cross-section spread are essentially unchanged—negative pivotal-shift amendments underperform SPY by between seven and eight percent over thirty trading days—but the strict-significance certificate is withdrawn. The Welch $t$-statistic falls from $4.37$ (row aggregation) to $1.69$ (unique-amendment dedup), and the bootstrap 95-percent CI on the negative arm of $[-9.97\%, -5.11\%]$ reported in the earlier draft was computed on the same non-independent rows and is withdrawn together with the inflated $t$. The OLS regression for the incremental Sharpe test in §5.3 was already at the unique-amendment level by construction (its implementation uses dictionary-keyed dedup) and is therefore unaffected; $\Delta\text{Sharpe} = +0.341$ over the phase-only baseline and the standalone pivotal-only Sharpe of $1.088$ stand. [Corrected 11 October 2026: the regression is indeed unaffected by the row-aggregation issue, but the incremental-Sharpe result is withdrawn for separate reasons; see Self-Correction #2 below.]

### Diagnostic procedure

The discrepancy was discovered during preparation of a LinkedIn writeup that attempted to visualize each unique amendment as a single point. The visualization counted approximately $20$ classified-non-neutral unique amendments while the earlier draft's headline claimed $96 + 21 = 117$. Tracing this gap exposed the row-iteration aggregation in `rigor_pass.py` and `day14_midcheckpoint.py`. A direct dedup-audit script (`output/linkedin/dedup_audit.py` in the author's career-workspace) confirmed the magnitude of the inflation. The corrected `rigor_pass.py` now preserves the original row-aggregated values under the JSON key `pre_dedup_raw_for_audit` for reproducibility, and computes the dedup-corrected unique-amendment statistics as the primary output. The strict positive-versus-negative test is also reported separately under the JSON key `strict_positive_vs_negative` so that the paper's original framing remains directly inspectable from the artifact.

### Why this is reported rather than silently amended

This paper was distributed under a public commit hash (Appendix B) and a public abstract on SSRN (resubmission in flight as of 2026-05-14). A silent in-place edit would be inconsistent with the reproducibility-from-public-commit commitment in Appendix B, and would create an asymmetry between the SSRN distribution copy and the repository copy. The audit is therefore documented in this section and the previous strict-significance headlines—Welch $t = 4.37$, Bonferroni-strict PASS, $n_{\text{negative}} = 21$ lock-safe—are explicitly retracted. The contribution claims listed in §1 are otherwise preserved: the unit of analysis is still the post-trial-start protocol amendment, the three-axis schema and the cross-vendor majority diagnostic remain valid, and the incremental Sharpe test over the phase-only baseline is unaffected. [Corrected 11 October 2026: the incremental-Sharpe result is withdrawn; see Self-Correction #2 below.]

### Path to restoring the strict certificate

Under the current pivotal-shift base rate in the labeled-amendment subsample—approximately twenty percent split between positive and negative labels, with negative roughly $20$ percent of that twenty percent—reaching the conservative $n_{\text{negative}} \ge 20$ floor at the unique-amendment level requires labeling approximately $400$ to $500$ additional unique amendment events. This is a one-to-two-order-of-magnitude expansion relative to the present $80$ unique-amendment sample and is operationally feasible within the existing pipeline ($\approx \$10$ in additional LLM credits under the present per-amendment cost) but requires substantially more PDF parsing throughput than the present rate-limited 819-PDF cache. Restoring the strict-significance certificate is left for a successor revision.

## Erratum / Post-Publication Self-Correction #2: Incremental Sharpe (2026-10-11)

Earlier versions of this paper, including the revision that introduced Self-Correction #1, reported that the regression-fitted combination of phase and pivotal scores delivers an incremental Sharpe ratio of $+0.341$ over the phase-only baseline (baseline $0.194$, full $0.535$), exceeding the pre-registered threshold of $0.30$ by $0.041$, and that a naive additive score attenuates this to $+0.066$. These statements are withdrawn. The arithmetic reproduces exactly from the committed manifests; the problem is what the statistic measures.

### What went wrong

1. *Units.* Each portfolio "Sharpe" is the mean divided by the standard deviation of the 52 pooled long and sign-flipped short event returns, multiplied by $\sqrt{52}$. This is a one-sample $t$-statistic. The per-event Sharpe difference is $0.047$. The $0.30$ threshold was specified for a portfolio Sharpe ratio, not for a difference of $t$-statistics that grows with $\sqrt{n}$.
2. *In-sample weights.* $\hat\beta_1$ and $\hat\beta_2$ are estimated on the same 80 events that are then ranked. Fitted weights align with the realized returns by construction, while the baseline direction is fixed. Under a permutation null that shuffles the CARs and refits the regression each time (10,000 draws), $68\%$ of draws give a difference of at least $+0.341$ and $69\%$ at least $0.30$. The test cannot separate the reported value from noise.
3. *Out of sample.* With leave-one-out weights the difference is $-0.78$; repeated 5-fold estimates have a median between $-0.54$ and $-0.88$, depending on how ties are ordered. Most of the leave-one-out drop comes from one event with a $+78\%$ CAR whose own return makes the phase coefficient positive and keeps it in the long leg.
4. *Ties.* The baseline score takes 3 values, the full score 9, and the pivotal score 3 (60 of 80 events score zero). The tercile cut therefore falls inside tied groups, and which tied events enter each leg is set by the order of rows in the manifest. Re-drawing the tie order at random gives a median difference of $+0.28$ (90\% range $-0.62$ to $+1.15$); reversing the row order gives $+0.21$. The LLM-only statistic of $1.088$ has a tie-order 90\% range of $-0.77$ to $+2.12$.
5. *The additive comparison.* The $+0.066$ additive value was computed on an earlier sample of 70 events. On that same sample, the regression-fitted difference was $-0.028$. On the final 80-event sample the additive difference is $+0.427$, above the regression-fitted $+0.341$. The move from fail to pass came from ten added events, not from the change of weighting.

### Consequence

The pre-registered incremental-Sharpe test is not passed. The alternative pass route, a partial-$\alpha$ $t \ge 2.0$ on $\text{Pivotal}$ controlling for phase, also fails ($t = 0.958$). Following the pre-registered rule, the study is closed as a writeup-only negative incremental result: at the present sample size, LLM-classified amendment direction is not shown to add to a phase-only baseline. Together with Self-Correction #1, no strict-inference claim of the paper remains. The cross-vendor agreement diagnostic ($99.29\%$) and the descriptive spread ($+7.48$ percentage points on 16 versus 4 unique amendments) are unaffected.

### How it was found

The defect was flagged on 10 October 2026 by a multi-model code review of the incremental-Sharpe routine and confirmed on 11 October 2026 by an independent re-implementation that reads only the committed manifests. It was not caught by the project's own pre-registered checks.

# Conclusion

The cross-section spread between LLM-classified positive and negative protocol amendments at the thirty-trading-day horizon is $+7.48$ percentage points at the unique-amendment level, with Welch $t = 1.69$ on $n_{\text{long}} = 16$ versus $n_{\text{short}} = 4$ unique amendments. The directional effect is preserved relative to the row-aggregated earlier draft, but neither the conventional $\alpha = 0.05$ threshold nor the strict Bonferroni-$K = 18$ critical value of $2.99$ is met; the contribution is therefore documented as a preliminary scout-feasible candidate rather than a deployed alpha. The LLM amendment features are not shown to add an incremental Sharpe above a transparent phase-only baseline that proxies the @reinisch2024ctpllm phase-transition predictor; the previously reported $+0.341$ and the standalone pivotal-only $1.088$ are withdrawn (Post-Publication Self-Correction #2), and the study closes as a negative incremental result under its pre-registered rule. The schema is supported by $99.29$-percent two-of-three cross-vendor majority agreement on the $95$-trial subsample with full three-vendor coverage, but the minority-class size of $4$ unique negative-pivotal-shift events is below the conservative $n \ge 20$ inferential-lock threshold and the strict-significance certificate is therefore withdrawn until the labeled-amendment sample is expanded.

The contribution is positioned at the boundary of three literatures. Relative to the trial-announcement and trial-result event-study literature, the unit of analysis is redefined as the post-trial-start protocol amendment—a continuous mid-event stream that is informationally distinct from announcements and results, and that exhibits multi-day to multi-week price drift. Relative to the protocol-amendment operational literature, the same event class is mapped into firm-level equity returns. Relative to LLM applications on ClinicalTrials.gov text, LLMs are applied to amendment text rather than registration text and the output is connected to financial outcomes. Relative to CTP-LLM, the input is shifted from initial protocol to amendment text, vendor diversity is introduced as a schema-validity diagnostic, and incremental Sharpe over the phase-only baseline is tested but not supported.

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

Third, on scoring portfolios from fitted weights (revised 11 October 2026): weights estimated on the same events that are then ranked inflate the full-model statistic, and coarse scores create ties at the tercile boundary whose resolution depends on row order. Out-of-sample weights, a permutation null that refits the weights, and tie-invariant leg assignment are needed before an incremental comparison is read. An earlier version of this note claimed a five-fold attenuation under naive addition; that comparison mixed samples and is withdrawn.

Fourth, on multi-process state: file-locked JSONL writes guarded by a per-file `.lock` allow multiple sibling processes—each handling a separate vendor—to append to a shared manifest without corruption. The deduplication key is the SHA-256 of the prompt, so prompt-version changes invalidate cache entries automatically.

Fifth, on cross-vendor agreement: a two-of-three majority across three independently developed model families functions as a model-internal validity check. The schema is well-defined to the extent that unrelated models reach the same label; the agreement rate alongside the headline metric is, in this view, a low-cost addition that should become standard for LLM-classification studies.
