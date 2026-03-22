# Table 6 Spec Card V1

Title:
- `Table 6. A/S Ratio, Patent Mismatch, and Future AI Patenting`

Purpose:
- First methodology-aligned AI-washing table.
- Tests whether the positive association between credible AI disclosure and future AI patenting weakens in mismatch years.

Panel:
- regression-ready ever-speaker annual panel
- `2016-2024`

Outcome:
- `log(1 + AI patents at t+1)`

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
- `A/S ratio` should be positive.
- `A/S ratio × PatentMismatch` should be negative.

Format:
- standalone journal-style Word table
- constants omitted
- clustered standard errors in parentheses
- adjusted R-squared reported
