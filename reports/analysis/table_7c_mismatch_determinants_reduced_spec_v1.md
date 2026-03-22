# Table 7C. Firm-Level Determinants of PatentMismatch (Reduced Baseline Set)

## Purpose
This refinement revisits Table 7 with a reduced baseline characteristic set so the multivariate column is estimated on a materially larger sample.

## Sample
- Source panel: `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`
- Estimation unit: firm
- Baseline row: year `2016`
- Industry fixed effects: baseline `sic2`

## Dependent Variable
- `ever_mismatch = 1` if the firm records at least one `PatentMismatch` incident between `2016` and `2024`.

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
- Omitting those two variables preserves the multivariate sample and tests whether the main cross-sectional pattern is stable rather than driven by complete-case attrition.

## Output Artifacts
- Markdown: `paper/generated/tables/table_7c_mismatch_determinants_reduced_prelim_v1.md`
- Review DOCX: `output/doc/delivery_tables_v1/table_7c_mismatch_determinants_reduced_prelim_v1.docx`
