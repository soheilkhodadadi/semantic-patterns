# Appendix Conditional Validation Spec Card

Table title:
- `Appendix Table. Conditional Disclosure Composition and Future AI Patenting`

Status:
- appendix table

## Purpose

This table preserves the earlier speaking-only validation result so it remains available as a useful conditional check.

It is no longer the main-text empirical anchor because it conditions on firm-years in which firms are already discussing AI.

## Input

- coefficient source:
  - `results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_coefficients.csv`
- supporting portfolio summary:
  - `results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_summary.md`

## Sample

- narrower AI-speaking regression sample
- years:
  - `2016–2024`

## Dependent Variable

- `any_pat_1`
- interpretation:
  - indicator that firm `i` has at least one AI patent in `t+1`

## Rows To Show

- actionable disclosure (dummy), firm + year FE
- speculative-only disclosure (dummy), firm + year FE
- actionable share, firm + year FE
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

## Main-Text / Appendix Boundary

- appendix

Reason:
- this remains a useful conditional-on-speaking validation object
- it does not support the broader calendar-time timing interpretation we now want in the main text
- the ever-speaker annual panel is the correct main-text base for timing analysis

## Interpretation Goal

The reader should be able to see:

- whether the earlier positive speculative signal survives in the narrower speaking-only design
- how that conditional result differs from the broader ever-speaker timing tables

## Caveats

- this table should not be used as the main-text sample definition
- it is conditional on already-speaking firm-years
- timing interpretation is therefore limited relative to the ever-speaker annual panel

## Output Artifacts

- `paper/generated/tables/table_2_core_patent_validation_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_2_core_patent_validation_prelim_v1.docx`
