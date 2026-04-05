# Source of Truth Map V1

## Purpose

This note identifies the current authoritative lanes in the repo and separates them from transitional, legacy, scratch, or project-specific lanes.

It is a working map for restructure and onboarding.

## Code source of truth

### Authoritative implementation namespace
- `src/semantic_ai_washing/`

This is the current canonical code lane.
New implementation should target this namespace first.

### Transitional and legacy pressure lanes
- `src/aggregation/`
- `src/analysis/`
- `src/classification/`
- `src/config/`
- `src/core/`
- `src/data/`
- `src/modeling/`
- `src/patents/`
- `src/scripts/`
- `src/tests/`
- `src/tmp/`

These remain for compatibility and history, but they should not be treated as the forward architectural center.

## High-level restructure pressure summary

The repo already declares a canonical implementation lane, but several layers are still co-located:
- canonical code
- compatibility shims
- rerunnable data products
- manuscript delivery artifacts
- Director runtime and review state

The restructure pressure is therefore not just code cleanup.
It is the need to separate these lanes so multiple active programs can use the repo without ambiguity.

## Governance and architecture source of truth

### Director and policy lane
Primary files:
- `docs/director/data_architecture_target.md`
- `docs/director/script_registry.md`
- `docs/director/policy.md`
- `docs/director/tooling_isolation.md`
- `docs/director/quickstart.md`

Purpose:
- workflow discipline
- environment and tooling rules
- canonical architecture targets
- script inventory and policy context

### Roadmap and lab-transition lane
Primary directory:
- `docs/roadmap_v2/`

Current authoritative planning notes include:
- `roadmap_v4_multi_program_v1.md`
- `lab_mvp_1_0_blueprint_v1.md`
- `roadmap_v3_concept_v1.md`
- `lab_transition_architecture_v1.md`
- `roadmap_v2_review_v1.md`

Purpose:
- strategy
- restructure planning
- public-safe lab transition notes

## Current AI-washing analytical source of truth

### High-level current-state guide
- `README.md`
- `docs/preliminary_delivery_status_2026-03-20.md`

### Technical paper-support audit
- `reports/analysis/pass_c_technical_audit_2026-03-25_v1.md`

### Core current analytical objects
- cleaned narrative backbone:
  - `data/processed/aggregates/firm_year_narrative_measures_prelim_clean_v1.parquet`
- promoted patent series:
  - `data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv`
- controls backbone:
  - `data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv`
- merged ever-speaker panel:
  - `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- regression-ready ever-speaker panel:
  - `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

These are the current authoritative AI-washing analytical backbones for the active delivery lane.

## Benchmark and evaluation source of truth

### Labels and IRR
- `data/labels/v1/`
- `reports/labels/irr_report.json`
- `reports/labels/irr_disagreement_diagnostic_v1.json`

### Evaluation and benchmarking
- `reports/evaluation/heldout_eval_prelim_v2.json`
- `reports/evaluation/model_benchmark_matrix_prelim_v1.json`
- `reports/models/preliminary_results_readiness_v1.json`

These are the current canonical benchmark and measurement-audit lanes.

## Delivery artifact source of truth

### Generated tables, figures, and snippets
- `paper/generated/`
- `output/doc/delivery_tables_v1/`
- `output/doc/delivery_figures_v1/`
- `output/figures/delivery_figures_v1/`

### Reporting and review packets
- `output/doc/reports/`
- `output/paper/reports/`
- `output/doc/preliminary_delivery_review_packet_v1.docx`
- `output/doc/results_draft_scaffold_v1.docx`
- `output/doc/results_transition_notes_v1.docx`

These are current delivery surfaces, not reusable shared-core infrastructure by default.

## Public-safe vs local-private planning lanes

### Tracked public-safe lane
- `docs/roadmap_v2/`

### Local private lane
- `local_private/roadmap_v2/`

Use the local-private lane for:
- interview prep tied to specific organizations
- partner-sensitive project notes
- strategy notes that should not live in a public repo

## Current restructure implications

### Shared core candidates
Strong candidates for shared-core treatment:
- manifests and evidence contracts
- labeling and IRR workflow
- benchmark/evaluation registries
- report/export primitives
- project registry and artifact policy

### Project-specific candidates
Should remain project-specific unless reused:
- AI-specific semantic taxonomy
- patent validation logic
- project-specific empirical tables and figures
- paper-draft prose and journal-facing materials

## Bottom line

The repo already has a source of truth.
The problem is not absence of authoritative material.
The problem is that authoritative lanes, transitional lanes, and project-specific lanes are still too close together.

This map is the first step toward separating them cleanly.
