# Table 7D. Firm-Level Determinants of PatentMismatch Intensity (Reduced Baseline Set)

## Purpose
This refinement revisits Table 7B with a reduced baseline characteristic set so the multivariate column is estimated on a materially larger sample.

## Sample
- Source panel: `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`
- Estimation unit: firm
- Baseline row: year `2016`
- Industry fixed effects: baseline `sic2`

## Dependent Variable
- `mismatch_share_talk`: the share of AI-talking years between `2016` and `2024` that are flagged as `PatentMismatch`.

## Regressors
Reduced baseline firm characteristics measured in `2016`:
- `ln_assets`
- `cash`
- `leverage`
- `capx_at`
- `roa`

## Why Reduced
- `rd_intensity` has heavy baseline missingness in `2016`.
- `emp` has moderate baseline missingness in `2016`.
- Omitting those two variables preserves the multivariate sample and tests whether the intensity pattern is stable rather than driven by complete-case attrition.

## Output Artifacts
- Markdown: `paper/generated/tables/table_7d_mismatch_intensity_reduced_prelim_v1.md`
- Review DOCX: `output/doc/delivery_tables_v1/table_7d_mismatch_intensity_reduced_prelim_v1.docx`
