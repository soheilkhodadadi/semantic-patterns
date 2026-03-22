# Appendix Table A1 Spec Card V1

Date:
- `2026-03-21`

Title:
- `Appendix Table A1. Exploratory Credibility Metrics and Future AI Patenting`

## Purpose

This table moves from raw disclosure counts into the paper's credibility-style
constructs. It asks whether the broad AI-focus measure and the main credibility
metrics line up with future AI patenting at `t+1`.

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

- `log(1 + AI patents at t+1)`

## Row Metrics

Rows report separate one-variable regressions for:
- `AI_Focus`
- `SpecShare`
- `CredAI`
- `A_S`
- `SpecMinusAct`

Definitions:
- `AI_Focus = log(1 + AI sentences)`
- `SpecShare = S / (A + S)`
- `CredAI = z(A) - z(S)`
- `A_S = log(1 + A / (1 + S))`
- `SpecMinusAct = SpecShare - ActShare`

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
- appendix-only exploratory companion
- useful for benchmarking secondary credibility constructs against the methodology-aligned mismatch table

## Output Artifacts

- `paper/generated/tables/table_5_credibility_metrics_tplus1_prelim_v1.md`
- `output/doc/delivery_tables_v1/table_5_credibility_metrics_tplus1_prelim_v1.docx`
