# AI-Washing Migration Sheets

## Purpose

This folder contains the per-authority grouped migration sheets for the
`ai_washing` member migration.

Each sheet records:
- the canonical member-owned authority
- the main migrated callers
- the focused validation gate used for that surface

These are operational tracking artifacts. They are useful during migration, but
they are not the front-door explanation of the member.

## Current families

### Foundation and support surfaces
- `labeling_common_grouped_migration_sheet_v1.md`
- `classification_support_grouped_migration_sheet_v1.md`
- `benchmark_utils_grouped_migration_sheet_v1.md`
- `index_sec_grouped_migration_sheet_v1.md`
- `extract_sentence_table_grouped_migration_sheet_v1.md`
- `build_filing_manifest_grouped_migration_sheet_v1.md`
- `ff12_mapping_grouped_migration_sheet_v1.md`

### Heldout and IRR workflow
- `sample_heldout_v2_candidates_grouped_migration_sheet_v1.md`
- `freeze_heldout_v2_grouped_migration_sheet_v1.md`
- `freeze_split_registry_grouped_migration_sheet_v1.md`
- `publish_rubric_freeze_grouped_migration_sheet_v1.md`
- `audit_sentence_integrity_grouped_migration_sheet_v1.md`
- `prepare_irr_subset_grouped_migration_sheet_v1.md`
- `adjudicate_irr_labels_grouped_migration_sheet_v1.md`
- `compute_irr_metrics_grouped_migration_sheet_v1.md`
- `diagnose_irr_disagreements_grouped_migration_sheet_v1.md`
- `publish_preliminary_results_readiness_grouped_migration_sheet_v1.md`

### Review-sheet and Phase 1 dataset workflow
- `build_labeling_batch_grouped_migration_sheet_v1.md`
- `initialize_review_sheet_grouped_migration_sheet_v1.md`
- `merge_labeling_batches_grouped_migration_sheet_v1.md`
- `build_labeling_sample_grouped_migration_sheet_v1.md`
- `dedupe_labeled_sentences_grouped_migration_sheet_v1.md`
- `qa_labeled_dataset_grouped_migration_sheet_v1.md`

### Assistive calibration workflow
- `assistive_prelabel_batch_grouped_migration_sheet_v1.md`
- `benchmark_prompt_variants_grouped_migration_sheet_v1.md`
- `score_prelabel_sheet_grouped_migration_sheet_v1.md`

## How to use this folder

If you are trying to understand the project member quickly, start here instead:
- `projects/ai_washing/README.md`
- `projects/ai_washing/root_surface_triage_registry_v1.md`

Use the grouped migration sheets only when you need authority-by-authority
migration detail.
