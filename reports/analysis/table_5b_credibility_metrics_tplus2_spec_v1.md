# Appendix Table A2 Spec Card V1

Date:
- `2026-03-21`

Title:
- `Appendix Table A2. Exploratory Credibility Metrics and Longer-Horizon AI Patenting`

## Purpose

This table is the longer-horizon companion to Table 5. It asks whether the same
credibility metrics line up with AI patenting at `t+2`, which is useful for
checking persistence beyond the first post-disclosure year.

## Sample

Input panel:
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

Unit of observation:
- firm-year

Sample logic:
- ever-speaker annual panel
- regression-ready sample
- zero-disclosure years retained within the ever-speaker scaffold

## Dependent Variable

- `log(1 + AI patents at t+2)`

## Row Metrics

Rows report separate one-variable regressions for:
- `AI_Focus`
- `SpecShare`
- `CredAI`
- `A_S`
- `SpecMinusAct`

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
- absorbed OLS with firm-clustered standard errors

Display rules:
- one coefficient row per metric
- clustered SEs in parentheses beneath
- constants omitted
- footer rows include controls, FE/sample flags, adjusted R-squared, and observations

## Narrative Role

Expected use:
- appendix-only exploratory companion to Appendix Table A1
- helps decide whether any secondary credibility-style signal persists beyond `t+1`

## Output Artifacts

- `paper/generated/tables/table_5b_credibility_metrics_tplus2_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_5b_credibility_metrics_tplus2_prelim_v1.docx`
