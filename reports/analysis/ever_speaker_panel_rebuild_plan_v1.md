# Ever-Speaker Panel Rebuild Plan V1

## Why this rebuild is needed

The current merged panel is an `AI-speaking firm-year` panel, not an
`ever-AI-speaking firm over all years` panel. It also builds patent leads by
shifting to the next observed row within firm rather than on a complete annual
scaffold.

That is acceptable for a narrow conditional validation table, but not for:

- prior-patent checks
- same-year versus future-year patent timing
- mismatch-style designs
- onset-style designs

## Target design

Build an annual panel for `2016–2024` with:

- firms: all firms that ever have AI disclosure in the current sample window
- years: all years `2016–2024` for those firms
- controls: merged by `(cik, year)`
- patent counts: merged by `(cik, year)` with zeros where absent
- disclosure counts: merged by `(cik, year)` with zeros where absent

## New variables to create

- `any_ai_talk`
- `patents_ai_lag2`
- `patents_ai_lag1`
- `patents_ai_t`
- `patents_ai_lead1`
- `patents_ai_lead2`
- `any_pat_lag2`
- `any_pat_lag1`
- `any_pat_t`
- `any_pat_lead1`
- `any_pat_lead2`

## Recommended output files

- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`
- `reports/panel_clean_qc_ever_speaker_2016_2024_v1.md`
- `reports/analysis/sample_comparison_ever_speaker_v1.md`

## Recommended first regressions after rebuild

1. `any_pat_t ~ has_actionable + controls + FE`
2. `any_pat_t ~ has_spec_only + controls + FE`
3. `any_pat_lead1 ~ has_actionable + controls + FE`
4. `any_pat_lead1 ~ has_spec_only + controls + FE`
5. `any_pat_lag1 ~ has_actionable + controls + FE`
6. `any_pat_lag1 ~ has_spec_only + controls + FE`

## Interpretation goal

This rebuild lets us distinguish among three different stories:

- `Actionable talk aligns with existing innovation`
- `Actionable talk predicts future innovation`
- `Speculative talk is decoupled from both prior and future innovation`

That is a much stronger empirical foundation for delivery than the current
single-horizon conditional panel alone.
