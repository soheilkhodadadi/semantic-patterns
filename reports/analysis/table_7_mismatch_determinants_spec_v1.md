# Table 7. Firm-Level Determinants of PatentMismatch

## Purpose
This table asks who is more likely to exhibit PatentMismatch in the ever-speaker sample. It follows the mismatch-visualization stage and mirrors the comparison paper's firm-level determinants logic.

## Sample
- Source panel: `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`
- Estimation unit: firm
- Baseline row: year `2016`
- Industry fixed effects: baseline `sic2`

## Dependent Variable
- `ever_mismatch = 1` if the firm records at least one `PatentMismatch` incident between `2016` and `2024`.

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
This table follows Figure 4. After establishing that PatentMismatch rises over time and concentrates in certain sectors, the next question is which baseline firm characteristics predict that behavior.

## Output Artifacts
- Markdown: `paper/generated/tables/table_7_mismatch_determinants_prelim_v1.md`
- Review DOCX: `output/doc/delivery_tables_v1/table_7_mismatch_determinants_prelim_v1.docx`
