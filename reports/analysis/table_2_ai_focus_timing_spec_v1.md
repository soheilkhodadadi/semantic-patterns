# Table 2 Spec Card

Table title:
- `Table 2. AI Disclosure Intensity and AI Patent Timing`

Status:
- preliminary main-text table

## Purpose

This is the first main-text timing table on the rebuilt ever-speaker annual panel.

Its job is to answer a simple and important question:

- does broad AI disclosure intensity line up more closely with prior AI patenting, same-year AI patenting, or later AI patenting?

This table is intentionally narrow. It uses a single focal variable, `AI_Focus`, so the reader first understands the timing pattern for broad AI disclosure before seeing the more detailed decomposition in the next table.

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

## Focal Variable

- `AI_Focus`
- interpretation:
  - `log(1 + AI sentences)`

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

- one row for `AI_Focus`
- one standard-error row underneath
- footer rows:
  - `Controls`
  - `Firm FE`
  - `Year FE`
  - `Observations`

## Main-Text / Appendix Boundary

- main text

Reason:
- it is the first clean timing table on the correct sample
- it establishes whether “AI talk” in the broad sense has any meaningful timing alignment with AI patent outcomes
- it prepares the reader for the more diagnostic decomposition table that follows

## Interpretation Goal

The reader should be able to see:

- whether AI disclosure intensity is mostly backward-looking
- whether it is contemporaneous with realized innovation
- whether it remains predictive at `t+1` or `t+2`

## Caveats

- this table does not yet distinguish actionable from speculative language
- it should not be interpreted as the full AI-washing test by itself
- the decomposition table should follow immediately after this one

## Output Artifacts

- `paper/generated/tables/table_2_ai_focus_timing_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_2_ai_focus_timing_prelim_v1.docx`
