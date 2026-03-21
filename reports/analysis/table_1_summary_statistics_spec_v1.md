# Table 1 Spec Card

Table title:
- `Table 1. Summary Statistics and Coverage`

Status:
- preliminary main-text table

## Purpose

This table establishes:

- sample credibility
- variable scale
- distribution of the core narrative measures
- sparsity of the patent outcomes
- baseline range of the controls

It should be the first empirical table the reader sees after the data and measure description.

## Input

- primary file:
  - `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv`

## Sample

- regression-ready firm-year panel
- years:
  - `2016–2024`
- sample size:
  - `6,152` firm-year rows

## Variables To Show

- `n_A`
- `n_S`
- `n_I`
- `AI_Focus`
- `share_A`
- `share_S`
- `CredAI`
- `A_S`
- `patents_ai`
- `patents_total`
- `ln_assets`
- `leverage`
- `cash`
- `rd_intensity`
- `capx_at`
- `roa`
- `sales_growth`
- `emp`

## Columns

- `Variable`
- `Definition`
- `N`
- `Mean`
- `SD`
- `P25`
- `Median`
- `P75`

## Main-Text / Appendix Boundary

- main text

Reason:
- this table defines the scale and distribution of the variables used later
- it should stay readable and compact
- extra distribution checks, winsorization checks, and variable-definition expansions can move to appendix later if needed

## Interpretation Goal

The table should help the reader see:

- AI disclosure is highly skewed
- speculative disclosure is smaller on average than actionable disclosure, but still materially present
- AI patenting is sparse even in the regression-ready sample
- the control variables look like a normal public-firm panel rather than a distorted niche sample

## Caveats

- variable-specific `N` differs because some controls have missing values
- this table is descriptive only; it does not imply a balanced panel
- this table should not include regression objects, FE, or significance markers

## Output Artifact

- `paper/generated/tables/table_1_summary_statistics_prelim_v1.md`

