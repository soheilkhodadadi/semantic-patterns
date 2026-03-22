# Preliminary Delivery Status

Date: `2026-03-20`

## Current Position

The preliminary pipeline is now in a usable delivery state:

- cleaned sentence layer complete for `2016–2024`
- promoted patent series complete for `2016–2024`
- Compustat controls pulled through `2016–2024`
- merged panel and regression-ready panel built
- rebuilt ever-speaker annual panel and regression-ready sample built
- broader regression portfolio estimated
- standalone delivery tables generated on the ever-speaker panel through the methodology-aligned mismatch stage
- standalone delivery figures generated through the mismatch-incidence figure
- main-text versus appendix boundaries clarified in the delivery planning layer

## Authoritative Data Artifacts

- narrative / classification panel backbone:
  - `data/processed/aggregates/firm_year_narrative_measures_prelim_clean_v1.parquet`
- promoted patent series:
  - `data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv`
- merged full panel:
  - `data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv`
- regression-ready full panel:
  - `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv`
- merged ever-speaker annual panel:
  - `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- regression-ready ever-speaker annual panel:
  - `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`
- controls backbone:
  - `data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv`

## Authoritative Results Artifacts

- baseline / portfolio directory:
  - `results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/`
- portfolio manifest:
  - `results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_manifest.json`
- portfolio summary:
  - `results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique/portfolio_summary.md`
- compiled manuscript markdown:
  - `output/paper/manuscript_compiled.md`
- current main-text table family:
  - `paper/generated/tables/table_1_summary_statistics_prelim_v1.md`
  - `paper/generated/tables/table_2_ai_focus_timing_prelim_v1.md`
  - `paper/generated/tables/table_3_disclosure_composition_timing_prelim_v1.md`
  - `paper/generated/tables/table_4_actionable_patent_timing_prelim_v1.md`
  - `paper/generated/tables/table_4b_speculative_patent_timing_prelim_v1.md`
  - `paper/generated/tables/table_6_as_patent_mismatch_tplus1_prelim_v1.md`
  - `paper/generated/tables/table_6b_as_patent_mismatch_tplus2_prelim_v1.md`
- appendix table family:
  - `paper/generated/tables/table_2_core_patent_validation_prelim_v1.md`
  - `paper/generated/tables/table_5_credibility_metrics_tplus1_prelim_v1.md`
  - `paper/generated/tables/table_5b_credibility_metrics_tplus2_prelim_v1.md`
- current main-text figure family:
  - `output/figures/delivery_figures_v1/figure_1_disclosure_volume_composition_prelim_v1.png`
  - `output/figures/delivery_figures_v1/figure_2_ai_patent_coverage_prelim_v1.png`
  - `output/figures/delivery_figures_v1/figure_3_patent_mismatch_alignment_prelim_v1.png`
  - `output/figures/delivery_figures_v1/figure_4_mismatch_incidence_industry_prelim_v1.png`

## Headline Empirical Read

Current main-text framing should emphasize the ever-speaker annual panel and distinguish three layers of evidence:

1. broad AI-disclosure intensity and composition timing
2. disclosure-type timing matrices
3. methodology-aligned AI-washing evidence via `A_S × PatentMismatch`

From the timing tables:

- `AI_Focus` is positive and statistically significant at every horizon:
  - `t-2 = 0.039***`
  - `t-1 = 0.056***`
  - `t = 0.056***`
  - `t+1 = 0.047***`
  - `t+2 = 0.031***`
- actionable disclosure is near zero at `t-2`, then positive and statistically significant from `t-1` through `t+2`
- speculative-only disclosure is negative and significant at `t-2`, `t-1`, and `t`, then fades toward zero at `t+1` and `t+2`

From the methodology-aligned mismatch table:

- `A/S ratio` enters positively at `t+1`
- `A/S × PatentMismatch` enters negatively at `t+1` and remains negative at `t+2`
- the negative interaction is strongest in the industry×year specification but remains directionally consistent in the firm-FE trims

The earlier conditional validation table remains useful, but it now belongs in the appendix rather than the main-text empirical sequence. The exploratory credibility-metric table also moves to the appendix now that the methodology-aligned mismatch table is built.

## Modeling Decisions Locked In For The Preliminary Draft

- do not use `log_docs` / `log(# AI sentences)` as a default control in headline regressions
- omit constants from displayed main-text tables
- prefer separate actionable-only and speculative-only headline regressions
- keep richer functional-form / logit / count-model variants in robustness or appendix tables

## Paper Status

The paper generation layer was refreshed so the main Results section now:

- drops the stale baseline table that displayed `log(# AI sentences)`
- uses a new generated headline table driven by the current portfolio outputs
- explicitly states that controls are included in the regressions but constants are omitted from the display

If a fresh `.docx` is needed after further edits, run:

```bash
cd /Users/soheilkhodadadi/Documents/Projects/semantic-patterns
env PYTHONPATH=src ./.venv/bin/python scripts/build_paper.py
```

## Immediate Next Work

1. Decide whether the next empirical object should be `Table 7`, the determinants / correlates of `PatentMismatch`.
2. Keep final manuscript insertion separate from table/figure production so the paper-polish step stays controlled.
3. Refresh the modular review packet again only after the next main-text empirical object is validated.
