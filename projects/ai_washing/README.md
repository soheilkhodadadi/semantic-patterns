# AI-Washing Member Seed

## Status
- member shell is real
- member-owned code is real
- active workflow migration is now in the late phase, not the shell-planning phase

## Purpose

`ai_washing` is the flagship project member in the lab structure.

It is gradually becoming the canonical home for:
- project-specific code
- project-specific tests
- project-specific reports and outputs
- project-specific migration decisions

## Canonical locations

Member-owned code:
- `projects/ai_washing/src/ai_washing_member/`

Member-owned tests:
- `projects/ai_washing/tests/`

Member-facing artifact lanes:
- `projects/ai_washing/reports/`
- `projects/ai_washing/output/`
- `projects/ai_washing/docs/`
- `projects/ai_washing/configs/`

Legacy compatibility still exists in:
- `src/semantic_ai_washing/`

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

### Heldout and IRR
- `labeling/sample_heldout_v2_candidates.py`
- `labeling/freeze_heldout_v2.py`
- `labeling/freeze_split_registry.py`
- `labeling/publish_rubric_freeze.py`
- `labeling/build_irr_boundary_benchmark.py`
- `labeling/audit_sentence_integrity.py`
- `labeling/prepare_irr_subset.py`
- `labeling/adjudicate_irr_labels.py`
- `labeling/compute_irr_metrics.py`
- `labeling/diagnose_irr_disagreements.py`
- `labeling/publish_preliminary_results_readiness.py`

### Classification support
- `classification/benchmark_utils.py`
- `classification/model_runtime.py`
- `classification/preliminary_pipeline.py`
- `classification/train_preliminary_centroids.py`
- `classification/train_binary_relevance_then_as.py`
- `classification/train_logreg_preliminary.py`
- `classification/classify_active_window_preliminary.py`
- `classification/classify_active_window_preliminary_restartable.py`
- `classification/evaluate_preliminary_heldout.py`
- `classification/benchmark_preliminary_models.py`
- `classification/publish_selected_preliminary_eval.py`
- `classification/reconcile_preliminary_classification_report.py`

### Data support
- `data/index_sec_filings.py`
- `data/extract_sentence_table.py`
- `data/build_filing_manifest.py`
- `data/build_expanded_sentence_pool.py`
- `data/combine_expanded_sentence_pool_batches.py`
- `data/benchmark_segmentation_modes.py`
- `data/materialize_active_window_sentences.py`
- `data/run_historical_backfill.py`
- `data/reextract_tranche_slice.py`

## Read this folder in this order

1. `projects/ai_washing/root_surface_triage_registry_v2.md`
2. `projects/ai_washing/migration_sheets/README.md`
3. `docs/roadmap_v2/restructure_progress_checkpoint_v17.md`
4. `docs/roadmap_v2/batched_execution_queue_v24.md`

## Planning documents that still matter

- `projects/ai_washing/planning_notes/member_seed_plan_v1.md`
- `projects/ai_washing/planning_notes/member_shell_readiness_v1.md`
- `projects/ai_washing/planning_notes/first_code_seed_decision_v1.md`
- `projects/ai_washing/planning_notes/labeling_common_impact_map_v1.md`

These are now background/reference notes, not the front door.

## Current posture

- the live labeling, classification, and data lanes are now mostly canonical
  under `ai_washing_member`
- the remaining root-owned `ai_washing` surfaces are mostly wrappers or
  dormant-but-relevant historical/project utilities
- there are no strong active `ai_washing` migration openers left right now
- the six historical data cleanup/acquisition utilities are now explicitly
  treated as script-deprecation candidates in the generated registry layer
- their flat `src/data/*` shims are now explicitly treated as legacy consumer
  surfaces rather than generic compatibility front doors
- use the triage registry before assuming a new `ai_washing` queue should open
