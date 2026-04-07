# AI-Washing Project Member

## Status
- member-owned code is real
- the active workflow migration is in the late stage
- remaining work is now wrapper/history/hygiene oriented, not shell seeding

## Purpose

`ai_washing` is the flagship project member in the lab structure.

It is the canonical home for:
- project-specific code
- project-specific tests
- project-specific reports and outputs
- project-specific migration and triage decisions

## Canonical locations

Member-owned code:
- `projects/ai_washing/src/ai_washing_member/`

Member-owned tests:
- `projects/ai_washing/tests/`

Migration sheets:
- `projects/ai_washing/migration_sheets/README.md`

Planning notes:
- `projects/ai_washing/planning_notes/README.md`

Member docs:
- `projects/ai_washing/docs/README.md`
- `projects/ai_washing/docs/publication_upgrade_stakeholder_expectations_v1.md`
- `projects/ai_washing/docs/publication_upgrade_roadmap_v1.md`
- `projects/ai_washing/docs/track_a_execution_plan_v1.md`
- `projects/ai_washing/docs/track_a_2025_refresh_readiness_v1.md`
- `projects/ai_washing/docs/track_a_2025_source_staging_v1.md`
- `projects/ai_washing/docs/track_a_2025_refresh_contract_v1.md`
- `projects/ai_washing/docs/track_a_filing_date_and_patent_window_audit_v1.md`
- `projects/ai_washing/docs/track_a_patent_refresh_source_review_v1.md`
- `projects/ai_washing/docs/track_a_market_data_source_review_v1.md`

Current root-surface triage:
- `projects/ai_washing/root_surface_triage_registry_v2.md`

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
- `data/stage_sec_year_root.py`
- `data/index_refresh_window.py`
- `data/build_refresh_extraction_manifests.py`
- `data/extract_refresh_year_batches.py`

## Read this folder in this order

1. `projects/ai_washing/root_surface_triage_registry_v2.md`
2. `projects/ai_washing/docs/publication_upgrade_roadmap_v1.md`
3. `projects/ai_washing/migration_sheets/README.md`
4. `projects/ai_washing/planning_notes/README.md`
5. `docs/roadmap_v2/current_state_navigation_v1.md`

## Current posture

- the live labeling, classification, and data lanes are now mostly canonical
  under `ai_washing_member`
- the remaining root-owned `ai_washing` surfaces are mostly wrappers or
  dormant-but-relevant historical/project utilities
- there are no strong active `ai_washing` migration openers right now
- the six historical data cleanup/acquisition utilities remain explicit
  script-deprecation candidates rather than migration targets
- any future queue in this lane should be chosen for real leverage, not for
  momentum alone
- `projects/ai_washing/docs/track_a_data_refresh_todo_v1.md`
