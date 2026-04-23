# AI-Washing Project Member

## Status
- member-owned code is real
- the active workflow migration is in the late stage
- the remaining work is now publication execution, benchmark hygiene, and
  panel-building rather than shell seeding

## Purpose

`ai_washing` is the flagship project member in the lab structure.

It is the canonical home for:
- project-specific code
- project-specific tests
- project-specific reports and outputs
- project-specific migration and triage decisions
- publication-upgrade planning and execution notes

## Canonical locations

Project-scoped docs and planning:
- `projects/ai_washing/docs/`
- `projects/ai_washing/docs/publication_upgrade_stakeholder_expectations_v1.md`
- `projects/ai_washing/docs/publication_upgrade_roadmap_v1.md`
- `projects/ai_washing/docs/track_a_publication_execution_map_v1.md`
- `projects/ai_washing/docs/track_a_event_study_and_economic_impact_design_v1.md`
- `projects/ai_washing/docs/track_a_master_run_execution_posture_v1.md`

Project-scoped run configuration:
- `projects/ai_washing/configs/master_run_registry_v1.json`
- `projects/ai_washing/docs/templates/writer_packet_template_v1.md`

Heavy runtime bootstrap:
- `scripts/ai_washing/bootstrap_publication_runtime_layout.sh`

Member-owned code:
- `projects/ai_washing/src/ai_washing_member/`

Member-owned tests:
- `projects/ai_washing/tests/`

Installed runtime namespace and canonical CLI entrypoints:
- `src/semantic_ai_washing/`
- use `python -m semantic_ai_washing...` for live execution

Label and IRR assets:
- `data/labels/v1/`
- `data/labels/v2/`
- `data/labels/v3/`

Held-out and benchmark assets:
- `data/validation/held_out_v3/`
- `data/validation/held_out_v4/`
- `data/validation/irr_boundary_benchmark_v1.csv`

Canonical refreshed annual panels:
- `data/processed/panel/canonical/`
- pre-hybrid annual ever-speaker panel:
  - `data/processed/panel/canonical/ever_speaker_panel_2016_2025_prehybrid_v1.parquet`
  - `data/processed/panel/canonical/ever_speaker_panel_2016_2025_prehybrid_v1.csv`
- companion note:
  - `projects/ai_washing/docs/track_a_ever_speaker_panel_rebuild_v1.md`

Shadow-classification and deferred-review assets:
- `data/processed/classifications_shadow_local_layered_v1/`
- `data/processed/shadow/deferred_review_sheets/`

Evaluation and run reports:
- `reports/evaluation/`
- `reports/classification/`
- `reports/labels/`
- `reports/api/`
- `reports/final/`

Paper-facing generated exports:
- `paper/generated/tables/`
- `paper/generated/figures/`
- `paper/generated/latex/`
- `paper/generated/writer_packets/`

Preferred heavy runtime root outside the repo:
- `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing`

Migration sheets:
- `projects/ai_washing/migration_sheets/README.md`

Planning notes:
- `projects/ai_washing/planning_notes/README.md`

Legacy compatibility still exists in:
- `src/semantic_ai_washing/`

## Where to edit now

### 1. Project docs and execution notes
Use `projects/ai_washing/docs/` for:
- publication roadmap updates
- classifier / IRR notes
- market-data and event-study design notes
- execution maps and handoff-style research memos

### 2. Live runtime scripts
Use `src/semantic_ai_washing/` for:
- scripts that are run via `python -m semantic_ai_washing...`
- active classification, labeling, aggregation, and shadow-defer utilities
- installed-package code that the repo currently executes in production

This is the important operational point:
- `projects/ai_washing/src/ai_washing_member/` exists and is useful
- but the live installed runtime still primarily flows through
  `src/semantic_ai_washing/`
- do not assume a file is inactive just because it sits under `src/`

### 3. Member-local code
Use `projects/ai_washing/src/ai_washing_member/` for:
- member-scoped helpers
- wrappers
- project-local implementation that should travel with the project member

### 4. Benchmarks and labels
Use:
- `data/labels/v1/` for the core label backbone and early IRR assets
- `data/labels/v2/` for revised-boundary adjudication outputs
- `data/labels/v3/` for the rerun IRR cycle and rerun adjudication outputs
- `data/validation/held_out_v3/` and `held_out_v4/` for frozen benchmark sets

### 5. Shadow API run state
Use:
- `data/processed/shadow/deferred_review_sheets/` for deferred slices and shard CSVs
- `reports/api/` for progress and cost reports
- `reports/classification/` for local shadow pass outputs

## Current publication-upgrade read order

1. `projects/ai_washing/docs/track_a_publication_execution_map_v1.md`
2. `projects/ai_washing/docs/publication_upgrade_stakeholder_expectations_v1.md`
3. `projects/ai_washing/docs/publication_upgrade_roadmap_v1.md`
4. `projects/ai_washing/docs/track_a_event_study_and_economic_impact_design_v1.md`
5. `projects/ai_washing/docs/track_a_master_run_execution_posture_v1.md`
6. `projects/ai_washing/configs/master_run_registry_v1.json`
7. `projects/ai_washing/docs/track_a_event_ready_panel_spec_v1.md`
8. `projects/ai_washing/docs/track_a_ever_speaker_panel_rebuild_v1.md`
9. `projects/ai_washing/docs/track_a_classifier_upgrade_execution_roadmap_v1.md`
10. `projects/ai_washing/docs/track_a_market_data_source_review_v1.md`
11. `projects/ai_washing/docs/track_a_data_refresh_todo_v1.md`

## Current canonical workflow families

### Labeling and calibration
- `labeling/common.py`
- `labeling/assistive_prelabel_batch.py`
- `labeling/benchmark_prompt_variants.py`
- `labeling/score_prelabel_sheet.py`
- `labeling/build_labeling_batch.py`
- `labeling/build_labeling_sample.py`
- `labeling/initialize_review_sheet.py`
- `labeling/merge_labeling_batches.py`
- `labeling/dedupe_labeled_sentences.py`
- `labeling/qa_labeled_dataset.py`

### Held-out and IRR
- `labeling/prepare_heldout_v3_assets.py`
- `labeling/freeze_heldout_v3.py`
- `labeling/prepare_heldout_v4_from_adjudication.py`
- `labeling/freeze_split_registry.py`
- `labeling/publish_rubric_freeze.py`
- `labeling/build_irr_boundary_benchmark.py`
- `labeling/audit_sentence_integrity.py`
- `labeling/prepare_irr_subset.py`
- `labeling/adjudicate_irr_labels.py`
- `labeling/compute_irr_metrics.py`
- `labeling/diagnose_irr_disagreements.py`

### Classification support
- `classification/model_runtime.py`
- `classification/preliminary_pipeline.py`
- `classification/train_binary_relevance_then_as.py`
- `classification/train_logreg_preliminary.py`
- `classification/classify_active_window_preliminary.py`
- `classification/classify_active_window_preliminary_restartable.py`
- `classification/evaluate_preliminary_heldout.py`
- `classification/benchmark_preliminary_models.py`
- `classification/shadow_selective_defer.py`
- `classification/prepare_shadow_defer_review_sheet.py`
- `classification/prepare_shadow_defer_shards.py`
- `classification/merge_shadow_defer_shards.py`
- `classification/merge_shadow_defer_labels.py`
- `classification/publish_selective_defer_runtime.py`

### Data support
- `data/index_sec_filings.py`
- `data/extract_sentence_table.py`
- `data/build_filing_manifest.py`
- `data/build_expanded_sentence_pool.py`
- `data/combine_expanded_sentence_pool_batches.py`
- `data/materialize_active_window_sentences.py`
- `data/run_historical_backfill.py`
- `data/reextract_tranche_slice.py`
- `data/clean_crsp.py`
- `data/clean_compustat.py`
- `data/pull_compustat_controls.py`

### Aggregation and panel support
- `aggregation/build_panel.py`
- `aggregation/build_preliminary_narrative_measures.py`
- `aggregation/build_ever_speaker_annual_panel.py`
- `aggregation/merge_ai_with_patents.py`

## Current posture

- the live measurement, benchmark, and hybrid-classification lane is now real
- the repo is usable, but the navigation burden is still too high unless the
  docs above are followed in order
- the biggest active empirical next step is no longer classifier rescue
- it is capital-market design and downstream panel execution using the
  provisional hybrid classifier while benchmark hygiene finishes
- `projects/ai_washing/docs/track_a_data_refresh_todo_v1.md`
  remains the open operational backlog
