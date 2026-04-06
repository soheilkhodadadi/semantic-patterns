# Semantic Patterns: AI Disclosure, Composition, and Patent Validation

## Overview

This repository contains a research pipeline for measuring AI-related corporate disclosure in SEC filings and validating those disclosure measures against external innovation outcomes.

The current `2016-2024` delivery lane does four things:

1. extracts AI-related sentences from annual filings
2. classifies those sentences as `Actionable`, `Speculative`, or `Irrelevant`
3. aggregates sentence-level outputs into firm-year disclosure measures
4. merges those measures with AI patent outcomes and Compustat controls for panel analysis

The repo still contains legacy-compatible extraction/classification entry points, but the authoritative preliminary-delivery artifacts now live in the broader `2016-2024` panel and reporting workflow described below.

## Environment

- Python baseline: `3.11+`
- canonical local environment: repo-local `.venv`
- workspace packages seeded during the lab restructure:
  - `semantic_labcore`
  - `semantic_director`
- recommended setup:

```bash
make bootstrap
source .venv/bin/activate
make doctor
make format
make lint
pytest -q
```

Detailed environment notes are in [docs/environment_setup.md](docs/environment_setup.md).

Until the workspace restructure is fully tool-managed, repo commands use a
workspace path profile equivalent to:

```bash
PYTHONPATH=src:packages/labcore/src:packages/director/src:projects/ai_washing/src
```

The Makefile now applies that profile for repo-owned module commands and doctor
checks.

## Current State

The repo is now in a usable preliminary-delivery state for the `2016-2024` analysis window.

Current authoritative artifacts include:

- cleaned narrative backbone:
  - `data/processed/aggregates/firm_year_narrative_measures_prelim_clean_v1.parquet`
- promoted patent series:
  - `data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv`
- controls backbone:
  - `data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv`
- merged conditional panel:
  - `data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv`
- regression-ready conditional panel:
  - `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv`
- merged ever-speaker annual panel:
  - `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- regression-ready ever-speaker annual panel:
  - `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

Current delivery status is tracked in [docs/preliminary_delivery_status_2026-03-20.md](docs/preliminary_delivery_status_2026-03-20.md).

## Lab Restructure Transition

The repo is now also being prepared to operate as a multi-program lab rather than a single-project workspace.

Wave 2 of that restructure creates the first stable destination lanes for future shared and project-scoped artifacts:

- lab-wide docs:
  - `docs/lab/`
- project docs:
  - `docs/projects/`
- shared registry and inventory reports:
  - `reports/registry/`
- project report lanes:
  - `reports/projects/`
- shared and project processed-data destination markers:
  - `data/manifests/`
  - `data/processed/shared/`
  - `data/processed/projects/`
- shared and project delivery destination markers:
  - `output/doc/shared/`
  - `output/doc/projects/`
  - `output/figures/shared/`
  - `output/figures/projects/`

The first registry-style map for those lanes is:

- `reports/registry/artifact_registry_v1.md`

The current AI-washing replacement map and Wave 3 note are:

- `docs/lab/migration/ai_washing_legacy_to_new_mapping_v1.md`
- `docs/roadmap_v2/migration_wave_3_v1.md`

Round A and Round B now add:
- shared contracts and acceptance gates under `docs/lab/schemas/` and `docs/lab/control_plane/`
- visible root landing zones:
  - `packages/`
  - `projects/`
  - `shared/`
- the Round B workspace-skeleton note:
  - `docs/roadmap_v2/history/rounds/migration_round_b_workspace_skeleton_v1.md`

Round C now adds:
- package/member seed plans for:
  - `packages/labcore/`
  - `packages/director/`
  - `projects/ai_washing/`
- staged placeholder decisions for:
  - `projects/eri/`
  - `projects/allocationlab/`
- the Round C package-seeding note:
  - `docs/roadmap_v2/history/rounds/migration_round_c_package_seeding_v1.md`

Important transition rule:
- existing authoritative AI-washing artifacts remain authoritative in their current legacy paths until later migration waves create explicit replacement maps

## Current Paper-Support Audit

For the March 25, 2026 Pass C draft, the current technical audit and reproducibility note live here:

- tracked report (markdown):
  - `reports/analysis/pass_c_technical_audit_2026-03-25_v1.md`
- local working copy (markdown):
  - `output/paper/reports/2026-03/pass_c_technical_audit_2026-03-25_v1.md`
- report (Word):
  - `output/doc/reports/2026-03/pass_c_technical_audit_2026-03-25_v1.docx`

This report consolidates the current answers to three paper-facing technical questions:
- measurement-audit evidence for the sentence classifier and IRR workflow
- the exact live `PatentMismatch` coding rule
- sample-attrition mechanics across the main empirical tables

Primary source-of-truth inputs for that report:
- `reports/models/preliminary_results_readiness_v1.json`
- `reports/labels/irr_report.json`
- `reports/labels/irr_disagreement_diagnostic_v1.json`
- `reports/evaluation/heldout_eval_prelim_v2.json`
- `reports/evaluation/model_benchmark_matrix_prelim_v1.json`
- `data/labels/v1/labels_master.parquet`
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

## Panels and Sample Definitions

Two panel objects are relevant right now:

### 1. Conditional AI-speaking panel

This panel keeps firm-years in which companies are already speaking about AI.

Use it for:
- conditional validation checks
- appendix-style regressions
- comparing results against earlier exploratory runs

Main files:
- `data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv`
- `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv`

### 2. Ever-speaker annual panel

This panel keeps all years from `2016` through `2024` for firms that mention AI at least once during the window, including zero-disclosure years.

Use it for:
- main-text timing analysis
- lag / contemporaneous / lead patent tests
- the current delivery package

Main files:
- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

The rationale for this rebuild is documented in:
- [reports/analysis/sample_construction_audit_v1.md](reports/analysis/sample_construction_audit_v1.md)
- [reports/analysis/sample_comparison_ever_speaker_v1.md](reports/analysis/sample_comparison_ever_speaker_v1.md)

## Patents and Controls

The current external-validation backbone depends on two major inputs beyond the disclosure layer.

### Patent series

The promoted patent series is generated from the lightweight patent extraction path with improved assignee matching and legal-suffix normalization.

Key output:
- `data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv`

Key script family:
- `python -m semantic_ai_washing.patents.extract_filtered_patents_lightweight`

### Compustat controls

The annual controls backbone covers `2016-2024` and feeds the merged panel build.

Key output:
- `data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv`

Key script:
- `python -m semantic_ai_washing.data.pull_compustat_controls`

## Legacy vs Current Classification Backbone

The repo still supports the legacy-compatible extract/classify/aggregate flow:

1. `*_ai_sentences.txt`
2. `*_classified.csv`
3. aggregated counts

That path remains useful for:
- new extraction runs
- sentence-level QA
- classifier evaluation and benchmarking

The current `2016-2024` delivery lane, however, is anchored on cleaned downstream artifacts:

- `firm_year_narrative_measures_prelim_clean_v1.parquet`
- merged panel files under `data/processed/panel/`
- delivery tables under `paper/generated/tables/`
- Word review outputs under `output/doc/`

So the sentence pipeline is still the foundation, but the authoritative delivery objects are the cleaned panel and table/report outputs built on top of it.

## How To Run the Current Pipeline

All examples below assume the repo-local environment is active.
Use `PYTHONPATH=src` only where a command still explicitly relies on legacy root-lane imports during the migration.

### 1. Extract AI-related sentences

```bash
python -m semantic_ai_washing.data.extract_ai_sentences \
  --input-dir data/processed/sec \
  --keywords data/metadata/ai_keywords.txt \
  --include-forms 10-K \
  --years 2024
```

### 2. Classify extracted sentences

```bash
python -m semantic_ai_washing.classification.classify_all_ai_sentences \
  --years 2024 \
  --two-stage \
  --rule-boosts \
  --tau 0.07 \
  --eps-irr 0.03 \
  --min-tokens 6
```

### 3. Build cleaned narrative measures

```bash
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.aggregation.build_preliminary_narrative_measures
```

### 4. Pull controls

```bash
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.data.pull_compustat_controls \
  --start-year 2016 \
  --end-year 2024 \
  --company-list data/metadata/company_lookup_active_annual_allyears_2021_2024.csv \
  --out-crosswalk data/externals/crosswalks/cik_gvkey_active_annual_allyears_2021_2024_v3.csv \
  --out-controls data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv \
  --out-qc reports/controls_qc_active_annual_allyears_2016_2024_v3.md
```

### 5. Build the ever-speaker annual panel

```bash
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.aggregation.build_ever_speaker_annual_panel \
  --narrative data/processed/aggregates/firm_year_narrative_measures_prelim_clean_v1.parquet \
  --patents data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv \
  --controls data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv \
  --out data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv
```

### 6. Prepare the regression-ready ever-speaker sample

```bash
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.analysis.prepare_panel_for_regression \
  --input data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv \
  --output data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv \
  --qc reports/panel_clean_qc_ever_speaker_2016_2024_v1.md
```

### 7. Run modular regression bundles

```bash
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.analysis.run_modular_regression_portfolio \
  --panel data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv \
  --spec-path reports/analysis/regression_specification_prelim_v1.json \
  --outdir results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique \
  --bundle-name example_bundle
```

### 8. Generate standalone delivery tables

Markdown:

```bash
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.analysis.generate_delivery_table_artifacts
```

DOCX:

```bash
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.analysis.build_delivery_table_docs
```

### 9. Refresh paper-facing snippets and draft

```bash
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.analysis.generate_paper_assets
env PYTHONPATH=src ./.venv/bin/python scripts/build_paper.py
```

## Delivery Outputs

Current delivery-facing objects include:

- generated markdown tables:
  - `paper/generated/tables/`
- standalone Word tables:
  - `output/doc/delivery_tables_v1/`
- monthly reports:
  - `output/doc/reports/`
- compiled paper outputs:
  - `output/paper/manuscript_compiled.md`
  - `output/doc/ai_washing_preliminary_draft.docx`

## Evaluation and QA

Classifier evaluation:

```bash
python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out \
  --two-stage \
  --rule-boosts \
  --tau 0.07 \
  --eps-irr 0.03 \
  --min-tokens 6
```

Project QA:

```bash
make format
make lint
.venv/bin/pytest -q
```

## Repository Structure

- `src/semantic_ai_washing/data/`: extraction, external pulls, and raw data preparation
- `src/semantic_ai_washing/classification/`: sentence classification, embeddings, centroids, evaluation helpers
- `src/semantic_ai_washing/aggregation/`: disclosure aggregation, patent merges, panel builders
- `src/semantic_ai_washing/analysis/`: regressions, delivery tables, paper assets, reporting
- `paper/`: manuscript sections, generated tables/snippets, literature inputs
- `output/`: compiled paper artifacts, Word review docs, monthly reports
- `reports/analysis/`: planning notes, spec cards, delivery blueprints, sample audits
- `docs/`: environment, workflow, and pipeline notes

## Documentation Map

Useful starting points:

- [docs/environment_setup.md](docs/environment_setup.md)
- [docs/preliminary_delivery_status_2026-03-20.md](docs/preliminary_delivery_status_2026-03-20.md)
- [docs/preliminary_results_execution_plan.md](docs/preliminary_results_execution_plan.md)
- [docs/modular_regression_workflow.md](docs/modular_regression_workflow.md)
- [reports/analysis/preliminary_delivery_story_roadmap_v1.md](reports/analysis/preliminary_delivery_story_roadmap_v1.md)

## Development Workflow

Use canonical module execution (`python -m semantic_ai_washing...`) for all new work.

Legacy `src/...` entrypoints are compatibility shims and should not be the default for new automation or public documentation.

Branching and merge conventions are documented in [CONTRIBUTING.md](CONTRIBUTING.md).
