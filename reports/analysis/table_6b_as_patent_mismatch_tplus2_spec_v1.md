# Table 6B Spec Card V1

Title:
- `Table 6B. A/S Ratio, Patent Mismatch, and Longer-Horizon AI Patenting`

Purpose:
- Longer-horizon companion to Table 6.
- Tests whether the mismatch attenuation pattern persists at `t+2`.

Panel:
- regression-ready ever-speaker annual panel
- `2016-2024`

Outcome:
- `log(1 + AI patents at t+2)`

Rows:
- `A/S ratio`
- `A/S ratio × PatentMismatch`

Columns:
- `(1)` firm + year FE
- `(2)` industry×year FE
- `(3)` firm + year FE, non-financial
- `(4)` firm + year FE, non-financial/non-utility

Controls:
- `ln_assets`
- `leverage`
- `cash`
- `rd_intensity`
- `capx_at`
- `roa`
- `sales_growth`
- `emp`

Expectation:
- `A/S ratio` should remain weakly positive or attenuate.
- `A/S ratio × PatentMismatch` should remain negative, though potentially weaker than at `t+1`.

Format:
- standalone journal-style Word table
- constants omitted
- clustered standard errors in parentheses
- adjusted R-squared reported
