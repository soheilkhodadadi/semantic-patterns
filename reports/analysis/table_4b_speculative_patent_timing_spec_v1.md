# Table 4B Spec Card V1

Date:
- `2026-03-21`

Title:
- `Table 4B. Speculative-Only Disclosure and AI Patent Timing`

## Purpose

This table is the companion timing-matrix table for speculative-only disclosure.
It asks whether speculative-only AI disclosure looks backward-looking,
contemporaneous, or forward-looking once the full AI patent timing window enters
in the same model.

## Sample

Input panel:
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

Unit of observation:
- firm-year

Sample logic:
- ever-speaker annual panel
- regression-ready sample
- zero-disclosure years retained when firms speak about AI elsewhere in the sample window

## Dependent Variable

- `has_spec_only`

Interpretation:
- indicator equal to `1` if the firm-year contains speculative AI disclosure but no actionable AI disclosure

## Core Regressors

Rows in the table correspond to the jointly estimated timing terms:
- `log(1 + AI patents)` at `t-2`
- `log(1 + AI patents)` at `t-1`
- `log(1 + AI patents)` at `t`
- `log(1 + AI patents)` at `t+1`
- `log(1 + AI patents)` at `t+2`

## Column Variants

1. firm + year FE
2. industry + year FE
3. firm + year FE, non-financial
4. firm + year FE, non-financial / non-utility

## Controls

Baseline controls:
- `ln_assets`
- `leverage`
- `cash`
- `rd_intensity`
- `capx_at`
- `roa`
- `sales_growth`
- `emp`

## Estimation

Estimator:
- linear probability model with absorbed fixed effects

Standard errors:
- clustered at the firm level

Display rules:
- coefficients on one line
- clustered SEs in parentheses beneath
- constants omitted
- footer rows include controls, FE flags, sample trims, adjusted R-squared, and observations

## Narrative Role

Expected use:
- companion to Table 4
- helps identify whether speculative-only disclosure is associated with weaker or more backward-looking AI innovation alignment

## Output Artifacts

- `paper/generated/tables/table_4b_speculative_patent_timing_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_4b_speculative_patent_timing_prelim_v1.docx`
