# Table 1 Spec Card

Table title:
- `Table 1. Summary Statistics`

Status:
- preliminary main-text table

## Purpose

This table establishes:

- the scale of the ever-speaker annual sample
- the distribution of the core disclosure-composition measures
- the sparsity and skewness of AI patent outcomes
- the baseline range of the financial controls

It should be the first empirical table the reader sees after the data and sample description because it anchors the reader on the sample that drives the main-text regressions.

## Input

- primary file:
  - `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## Sample

- regression-ready ever-speaker annual panel
- firms:
  - firms that mention AI at least once during `2016–2024`
- years:
  - `2016–2024`
- current sample size:
  - `18,741` firm-year rows

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
- `Mean`
- `Std. Dev.`
- `p5`
- `p25`
- `p50`
- `p75`
- `p95`
- `N`

## Main-Text / Appendix Boundary

- main text

Reason:
- this table defines the sample and variable scale used in the core timing tables
- the ever-speaker version is now the authoritative main-text sample
- additional sample-comparison or conditional-panel summary statistics can move to the appendix if needed

## Interpretation Goal

The table should help the reader see:

- the ever-speaker sample contains many zero-disclosure years by construction
- AI disclosure measures remain highly skewed even in that broader panel
- AI patenting is sparse at the firm-year level, with a zero median and a heavy right tail
- the controls look like a standard public-firm annual panel rather than a narrow hand-selected subsample

## Caveats

- variable-specific `N` differs because some controls have missing values
- this table is descriptive only; it does not imply a balanced panel
- this table should not include FE, standard errors, or significance markers

## Output Artifacts

- `paper/generated/tables/table_1_summary_statistics_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_1_summary_statistics_prelim_v1.docx`
