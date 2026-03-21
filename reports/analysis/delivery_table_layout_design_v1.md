# Delivery Table Layout Design V1

This note freezes the current layout conventions for standalone delivery tables.
The goal is to generate one clean Word document per exhibit so each table can be
reviewed, revised, and inserted into the draft independently of the full paper
build.

## Output convention

- Output folder: `output/doc/delivery_tables_v1/`
- One file per table:
  - `table_1_summary_statistics_prelim_v1.docx`
  - `table_2_core_patent_validation_prelim_v1.docx`
- Each file is self-contained:
  - centered title
  - note paragraph above the table
  - one table body
  - no dependency on the full manuscript build

## Table styling rules

- Font: Times New Roman throughout.
- Page: portrait, 0.75-inch margins.
- Title: centered, bold, larger than body text.
- Note: justified paragraph directly below the title and above the table.
- Table body:
  - no vertical rules
  - no shading
  - sparse horizontal rules only
  - stub column left-aligned
  - numeric columns centered
- Regression cells:
  - coefficient on first line
  - standard error on next line in parentheses
  - stars attached to coefficients only
- Footer rows:
  - controls
  - fixed effects
  - observations
  - additional fit statistics can be added later if we decide to display them

## Table-specific decisions

### Table 1

- Sample: regression-ready `2016-2024` panel
- Layout follows the journal-style summary-statistics template:
  - `Variable`
  - `Mean`
  - `Std. Dev.`
  - `p5`
  - `p25`
  - `p50`
  - `p75`
  - `p95`
  - `N`

### Table 2

- Layout follows the journal-style regression template.
- The dependent variable appears as a spanner header over model columns.
- Column structure:
  - `(1)` actionable-only model
  - `(2)` speculative-only model
  - `(3)` share model
- The share model displays both `Actionable share` and `Speculative share` rows
  so the column is not misleadingly summarized by one coefficient.

## Generator

- Builder module:
  - `python -m semantic_ai_washing.analysis.build_delivery_table_docs`
- Inputs:
  - regression-ready panel
  - merged clean panel
  - portfolio coefficient export
- The current generator is intentionally table-by-table and does not depend on
  `build_paper.py`.

## Open decisions

- Whether Table 1 should remain on the regression-ready sample or move to the
  broader clean merged panel.
- Whether to display `Adj. R^2` / `Pseudo R^2` in Table 2 once we expose those
  statistics cleanly from the regression pipeline.
- Whether appendix tables should switch to landscape when they become wider than
  the current three-column layout.
