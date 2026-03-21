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
- standalone main-text delivery tables generated on the ever-speaker panel
- manuscript markdown refreshed to reflect the current headline regression framing

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
- main-text timing tables:
  - `paper/generated/tables/table_2_ai_focus_timing_prelim_v1.md`
  - `paper/generated/tables/table_3_disclosure_composition_timing_prelim_v1.md`
- standalone Word timing tables:
  - `output/doc/delivery_tables_v1/table_2_ai_focus_timing_prelim_v1.docx`
  - `output/doc/delivery_tables_v1/table_3_disclosure_composition_timing_prelim_v1.docx`

## Headline Empirical Read

Current main-text framing should now emphasize the timing structure on the ever-speaker annual panel.

From the new timing tables:

- `AI_Focus` is positive and statistically significant at every horizon:
  - `t-2 = 0.039***`
  - `t-1 = 0.056***`
  - `t = 0.056***`
  - `t+1 = 0.047***`
  - `t+2 = 0.031***`
- actionable disclosure is near zero at `t-2`, then positive and statistically significant from `t-1` through `t+2`
- speculative-only disclosure is negative and significant at `t-2`, `t-1`, and `t`, then fades toward zero at `t+1` and `t+2`

The earlier conditional validation table remains useful, but it now belongs in the appendix rather than the main-text empirical sequence.

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

1. Validate and tighten the new ever-speaker `Table 2` and `Table 3` timing objects for the main-text sequence.
2. Decide which timing result should anchor the next FE ladder / sample-trim companion.
3. Keep the current conditional validation table as appendix support rather than as a main-text anchor.
4. Refresh manuscript-facing paper assets once the next table boundary is locked.
