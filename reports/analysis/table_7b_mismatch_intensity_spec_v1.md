# Table 7B. Firm-Level Determinants of PatentMismatch Intensity

## Purpose
This companion table asks whether the same baseline firm characteristics also predict the intensity of mismatch, not just whether a firm ever exhibits it.

## Sample
- Source panel: `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`
- Estimation unit: firm
- Baseline row: year `2016`
- Industry fixed effects: baseline `sic2`

## Dependent Variable
- `mismatch_share_talk`: the share of AI-talking years between `2016` and `2024` that are flagged as `PatentMismatch`.

## Regressors
Baseline firm characteristics measured in `2016`:
- `ln_assets`
- `cash`
- `leverage`
- `rd_intensity`
- `capx_at`
- `roa`
- `emp`

## Specification Layout
- Columns `(1)-(7)`: one-variable cross-sectional specifications with industry fixed effects.
- Column `(8)`: multivariate specification with all baseline characteristics jointly.
- Standard errors are clustered at the industry level.
- Constants are omitted from the displayed table.

## Narrative Role
This table is the nearby variant to Table 7. It helps separate one-off mismatch incidents from persistent mismatch behavior across a firm's AI-talking years.

## Output Artifacts
- Markdown: `paper/generated/tables/table_7b_mismatch_intensity_prelim_v1.md`
- Review DOCX: `output/doc/delivery_tables_v1/table_7b_mismatch_intensity_prelim_v1.docx`
