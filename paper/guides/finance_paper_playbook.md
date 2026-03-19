# Finance Paper Playbook for This Project

Updated: 2026-03-18

## Purpose

This note translates the current methodology draft and the local comparison paper
`paper/literature/AI_Washing_Nov.pdf` into an implementation playbook for our
preliminary draft.

It is not a claim that we should copy that paper. It is a guide for:

- what a finance-style empirical paper usually shows
- which tables and figures should exist in the portfolio
- where our project should intentionally differ

## Our Distinctive Angle

The comparison paper studies AI washing using:

- earnings-call AI talk
- employee-resume AI walk
- market reactions, institutional ownership, and managerial incentives

Our project should differentiate itself by leaning into what is genuinely unique
in the repo:

- annual 10-K narrative disclosure rather than conference-call rhetoric
- sentence-level classification into `Actionable`, `Speculative`, and `Irrelevant`
- explicit validation infrastructure:
  - held-out benchmark
  - IRR / adjudication lane
  - model benchmark matrix
- disclosure credibility measures derived from classified text:
  - `AI_Focus`
  - `SpecShare`
  - `CredAI`
  - `A_S`

The message should be:

- we are not simply measuring “AI talk”
- we are measuring the credibility composition of annual AI disclosure
- we test whether credible vs speculative disclosure predicts independent innovation outcomes

## Core Empirical Portfolio

### Table 1: Summary Statistics

Should include:

- `AI_Focus`
- `n_A`, `n_S`, `n_I`
- `ActShare`
- `SpecShare`
- `CredAI`
- `A_S`
- `patents_ai`
- `patents_total`
- core controls

### Table 2: Validation / Benchmarking

Should include:

- held-out benchmark asset summary
- class balance and exclusions
- benchmark matrix across candidate models
- selected model performance
- IRR summary and adjudication note

This can live in the appendix for journal format, but it should exist in the
technical-report portfolio.

### Table 3: Baseline Regressions

Primary specifications:

- future AI patents on `log_1p_A` and `log_1p_S`
- future AI patents on `has_actionable` and `has_spec_only`
- contemporaneous patent robustness
- binary “any AI patent” robustness

### Table 4: Credibility / AI-Washing Regressions

Primary specifications should use:

- `A_S`
- `SpecShare`
- `CredAI`
- mismatch interaction terms once mismatch is implemented

### Table 5+: Robustness and Heterogeneity

Candidates from the methodology:

- leads `t+1`, `t+2`
- alternative FE structure:
  - firm + year FE
  - industry x year FE
- subsamples by:
  - R&D intensity
  - prior patenting
  - financing frictions
  - competitive pressure
- governance incentives:
  - CEO Vega when available

## Figures Worth Generating

### Main Text

- yearly trend in AI disclosure volume
- yearly trend in `Actionable` vs `Speculative` shares
- top industries by AI disclosure growth
- trend in `SpecShare` or `CredAI`

### Appendix / Presentation

- benchmark-model comparison visual
- held-out confusion matrix
- sentence-cleanup coverage by year
- AI patent coverage by year
- industry-level AI disclosure trend

The local comparison paper uses a strong figure portfolio. We should do the same,
but tailored to the annual 10-K disclosure setting.

## Controls

### Already Implemented

- `ln_assets`
- `leverage`
- `cash`
- `rd_intensity`
- `capx_at`
- `roa`
- `sales_growth`
- `emp`

### Explicitly Called for in Our Methodology Draft

These should be added to the implementation queue:

- firm age
- market-to-book
- industry concentration (`HHI`)
- financing frictions (`SA index`)

### Heterogeneity / Extension Variables

- prior AI patenting
- industry-year AI narrative trend
- CEO Vega from ExecuComp
- AI-skills job-posting intensity if that data becomes feasible in time

## Reporting Style

For each regression table:

- state dependent variable clearly in the title
- state horizon clearly (`t`, `t+1`, `t+2`)
- report FE and clustering in notes
- keep the main text table clean
- move alternative estimators and extended robustness to appendix tables

For the surrounding prose:

- start with the sign and magnitude of the focal coefficients
- then discuss whether the speculative vs actionable split behaves as expected
- then explain the sample and caveats

## Immediate Implementation Order

1. stabilize the expanded patent keyword lane
2. extend controls to `2016-2020`
3. rebuild the full `2016-2024` panel
4. add missing methodology controls:
   - age
   - market-to-book
   - `HHI`
   - `SA index`
5. generate:
   - summary statistics
   - baseline regression portfolio
   - credibility / AI-washing portfolio
   - trend figures
6. refresh the manuscript and technical-report outputs

## Notes for Differentiation

To distinguish our paper from the comparison paper:

- emphasize disclosure credibility in annual reports, not management rhetoric in calls
- emphasize reproducible label validation and benchmark design
- show that the `Actionable` / `Speculative` distinction matters empirically
- use patents and, if feasible later, job postings as independent validation outcomes
