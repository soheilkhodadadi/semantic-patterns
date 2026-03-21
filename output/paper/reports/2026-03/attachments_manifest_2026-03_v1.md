# Attachments Manifest: March 2026

This note lists the canonical artifacts that can be attached or referenced alongside the March 2026 project updates.

## Core data artifacts

- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
  - This is the broad merged annual panel for firms that mention AI at least once during `2016–2024`. It keeps all years for those ever-speaking firms, including years with zero AI disclosure, and merges disclosure measures, AI patent outcomes, and controls before the final regression-ready filter.
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`
  - This is the cleaned estimation sample derived from the ever-speaker panel after applying the regression-side completeness filters. It is the main file to use for the next timing-analysis regressions because it preserves the broader annual scaffold while removing rows with missing variables needed for estimation.
- `data/processed/aggregates/firm_year_narrative_measures_prelim_clean_v1.parquet`
  - This is the narrative backbone generated from the sentence-classification pipeline. It contains the firm-year AI disclosure measures, including actionable, speculative, and irrelevant sentence counts, before patents and Compustat controls are merged in.
- `data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv`
  - This is the promoted AI-patent series used for the preliminary package. It contains the patent-side firm-year counts after the assignee-matching cleanup, including legal-suffix normalization and improved handling of name variants.

## Planning / audit artifacts

- `reports/analysis/preliminary_delivery_story_roadmap_v1.md`
  - This note is the main delivery-story guide for the current phase. It records which tables and figures we plan to build, what each is supposed to teach us, and how the story is meant to progress.
- `reports/analysis/sample_construction_audit_v1.md`
  - This audit explains the methodological difference between the earlier speaking-only panel and the comparison paper’s broader sample logic. It documents why the ever-speaker annual panel was needed for timing analysis.
- `reports/analysis/sample_comparison_ever_speaker_v1.md`
  - This is the before-and-after comparison between the earlier conditional panel and the rebuilt ever-speaker panel. It is useful for understanding how the sample size, zero-disclosure rows, and patent-positive rows changed after the rebuild.
- `docs/preliminary_results_execution_plan.md`
  - This is the current execution guide for the preliminary delivery phase. It summarizes the active workstreams, the table/figure sequence, and the immediate next empirical gate.

## Delivery artifacts

- `output/doc/delivery_tables_v1/table_1_summary_statistics_prelim_v1.docx`
  - This is the standalone Word version of the current summary-statistics table. It is meant for direct visual review and formatting checks rather than for running analysis.
- `output/doc/delivery_tables_v1/table_2_core_patent_validation_prelim_v1.docx`
  - This is the standalone Word version of the current conditional validation table from the narrower AI-speaking panel. It is still useful as an appendix or conditional check, even though the next main-text timing table will be built on the ever-speaker panel.
- `output/doc/delivery_tables_v1/table_2_ai_focus_timing_prelim_v1.docx`
  - This is the new main-text timing table on the rebuilt ever-speaker annual panel using `AI_Focus` as the focal regressor and `log(1 + AI patents)` at `t-2`, `t-1`, `t`, `t+1`, and `t+2` as the outcomes. It is the cleanest first broad-disclosure timing object for the delivery package.
- `output/doc/delivery_tables_v1/table_3_disclosure_composition_timing_prelim_v1.docx`
  - This is the new main-text disclosure-composition timing table on the rebuilt ever-speaker annual panel. Panel A shows actionable disclosure timing and Panel B shows speculative-only disclosure timing against AI patent outcomes across the same five horizons. It is the first table that directly operationalizes the project’s core substantive distinction on the corrected sample.
- `output/doc/reports/2026-03/executive_update_2026-03_v1.docx`
  - This is the short one-page March executive update intended for quick stakeholder review. It summarizes what changed materially and what the next gate is.
- `output/doc/reports/2026-03/detailed_update_2026-03_v1.docx`
  - This is the longer March project update intended for a supervisor or close stakeholder. It explains the main data, methodology, blocker-resolution, and next-step developments in paragraph form.
