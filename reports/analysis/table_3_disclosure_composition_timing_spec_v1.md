# Table 3 Spec Card

Table title:
- `Table 3. Disclosure Composition and AI Patent Timing`

Status:
- preliminary main-text table

## Purpose

This table is the first direct composition test on the rebuilt ever-speaker annual panel.

Its job is to show whether the timing pattern differs when we split broad AI disclosure into:

- actionable disclosure
- speculative-only disclosure

That makes it the first table that speaks directly to the substantive distinction motivating the project.

## Input

- primary file:
  - `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## Sample

- regression-ready ever-speaker annual panel
- firms:
  - firms that mention AI at least once during `2016–2024`
- years:
  - `2016–2024`

## Dependent Variables

Columns should correspond to:

- `t-2`: `log(1 + AI patents_{t-2})`
- `t-1`: `log(1 + AI patents_{t-1})`
- `t`: `log(1 + AI patents_t)`
- `t+1`: `log(1 + AI patents_{t+1})`
- `t+2`: `log(1 + AI patents_{t+2})`

## Panels

### Panel A

- regressor:
  - `has_actionable`
- interpretation:
  - indicator that the firm-year contains actionable AI disclosure

### Panel B

- regressor:
  - `has_spec_only`
- interpretation:
  - indicator that the firm-year contains speculative-only AI disclosure

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

## Table Layout

- two panels
- one coefficient row per panel
- one standard-error row per panel
- one shared footer block at the bottom:
  - `Controls`
  - `Firm FE`
  - `Year FE`
  - `Observations`

## Main-Text / Appendix Boundary

- main text

Reason:
- this is the first table that directly tests whether decomposition adds information beyond broad AI talk
- it fits naturally after the `AI_Focus` timing table
- it is cleaner and more persuasive than stacking every disclosure metric at once

## Interpretation Goal

The reader should be able to see:

- whether actionable disclosure is more aligned with prior or contemporaneous AI innovation
- whether speculative-only disclosure is more weakly aligned, contemporaneous, or forward-looking
- whether decomposition adds signal beyond the broad `AI_Focus` table

## Caveats

- this is still a timing-alignment table, not a final causal design
- FE ladders, industry trims, and alternative estimators should come later
- if the table becomes crowded, FE ladder variants should be split into a later companion table rather than pushed into this object

## Output Artifacts

- `paper/generated/tables/table_3_disclosure_composition_timing_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_3_disclosure_composition_timing_prelim_v1.docx`
