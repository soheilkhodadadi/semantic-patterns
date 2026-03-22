# Table 4 Spec Card

Table title:
- `Table 4. Specification Ladder for Future AI Patent Timing`

Status:
- preliminary main-text robustness table

## Purpose

This table is the first robustness ladder for the timing result we are most likely to care about in the main text:

- future AI patenting at `t+1`

Its job is to show whether the disclosure-composition result survives standard specification discipline without overcrowding the earlier timing tables.

## Input

- primary file:
  - `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## Sample

- regression-ready ever-speaker annual panel
- years:
  - `2016–2024`

## Dependent Variable

- `log(1 + AI patents_{t+1})`

## Panels

### Panel A

- `has_actionable`

### Panel B

- `has_spec_only`

## Columns / Specification Ladder

- `(1)` firm + year FE, full sample
- `(2)` industry + year FE, full sample
- `(3)` firm + year FE, non-financial sample
- `(4)` firm + year FE, non-financial and non-utility sample

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

- firm or industry fixed effects, depending on column
- year fixed effects in all columns
- clustered standard errors at the firm level
- adjusted R-squared reported

## Main-Text / Appendix Boundary

- main text candidate

Reason:
- it is the right next table after the timing family
- it tells us whether the `t+1` interpretation survives reasonable specification changes
- it is more persuasive than jumping directly to a larger menu of exploratory metrics

## Output Artifacts

- `paper/generated/tables/table_4_spec_ladder_tplus1_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_4_spec_ladder_tplus1_prelim_v1.docx`
