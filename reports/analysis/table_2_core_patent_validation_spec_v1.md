# Table 2 Spec Card

Table title:
- `Table 2. Core Patent Validation: Future AI Patent Extensive Margin`

Status:
- preliminary main-text table

## Purpose

This is the first indispensable empirical table.

Its job is to validate whether our filing-based disclosure measures line up with
an external innovation outcome. For the preliminary package, the cleanest
version of that validation is the extensive margin of future AI patenting.

## Input

- coefficient source:
  - `results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_coefficients.csv`
- supporting portfolio summary:
  - `results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_summary.md`

## Sample

- regression-ready firm-year panel
- years:
  - `2016–2024`
- main headline sample for this table:
  - `3,617` firm-year observations

## Dependent Variable

- `any_pat_1`
- interpretation:
  - indicator that firm `i` has at least one AI patent in `t+1`

## Rows To Show

- actionable disclosure (dummy), firm + year FE
- speculative-only disclosure (dummy), firm + year FE
- speculative share, firm + year FE

## Controls

- `ln_assets`
- `leverage`
- `cash`
- `rd_intensity`
- `capx_at`
- `roa`
- `sales_growth`
- `emp`

## Fixed Effects And Inference

- firm fixed effects
- year fixed effects
- clustered standard errors at the firm level

## Columns

- `Outcome`
- `Focal variable`
- `FE`
- `Sample`
- `Coef.`
- `p-value`
- `Sig.`
- `N`

## Main-Text / Appendix Boundary

- main text

Reason:
- this table performs the first direct validation against later patent outcomes
- it uses one focal disclosure variable at a time
- it avoids clutter from functional-form and FE ladder variants

Those richer alternatives belong in later tables:

- FE ladder:
  - later main-text or appendix table
- count-model / Poisson variants:
  - appendix or robustness table
- no-FE sensitivity:
  - later comparison table, not this one

## Interpretation Goal

The reader should be able to see, quickly:

- whether actionable disclosure predicts later AI patenting
- whether speculative disclosure predicts later AI patenting
- whether speculative share behaves similarly or differently

The current preliminary expectation is:

- speculative-only disclosure is the clearest positive signal in this table
- actionable disclosure is weaker in the comparable FE specification

## Caveats

- this table is intentionally narrow and does not settle the full “AI washing” question
- it validates disclosure composition against later AI patent incidence only
- count intensity, FE ladder comparisons, and alternative estimators are deferred to later tables

## Output Artifact

- `paper/generated/tables/table_2_core_patent_validation_prelim_v1.md`

