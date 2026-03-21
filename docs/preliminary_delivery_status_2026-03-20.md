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
- latest generated headline table:
  - `paper/generated/tables/regression_headline_prelim_v1.md`

## Headline Empirical Read

Current main-text framing should emphasize separate one-variable future-patent LPMs rather than crowded omnibus specifications.

Headline coefficients from the refreshed paper assets:

- speculative-only disclosure, firm/year FE:
  - `0.048`
  - `p = 0.086`
  - significance band: `10%`
- actionable-only disclosure, firm/year FE:
  - `-0.023`
  - `p = 0.409`
  - significance band: `n.s.`
- speculative share, firm/year FE:
  - `0.079`
  - `p = 0.029`
  - significance band: `5%`

Exploratory but not headline:

- actionable-only, no FE:
  - `0.089`
  - `p = 0.000`
  - likely sensitive to omitted-variable structure
- `AI_Focus`, firm/year FE:
  - `-0.039`
  - `p = 0.001`
  - useful as a credibility-style exploratory metric, not yet a headline replacement

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

1. Rebuild `Table 1` so the main-text version is anchored on the ever-speaker annual panel.
2. Estimate the new main-text `Table 2` on AI patent timing outcomes in the ever-speaker annual panel.
3. Move the current conditional validation table from the speaking-only panel to the appendix.
4. Build the FE ladder / sample-trim companion for the strongest timing specification.
