# AI-Washing Member Seed

## Status
- member shell is real
- member-owned code is real
- the migration is now in the mid-to-late phase, not the shell-planning phase

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

### Data support
- `data/index_sec_filings.py`
- `data/extract_sentence_table.py`
- `data/build_filing_manifest.py`

## Read this folder in this order

1. `projects/ai_washing/root_surface_triage_registry_v1.md`
2. `projects/ai_washing/migration_sheets/README.md`
3. `docs/roadmap_v2/restructure_progress_checkpoint_v6.md`
4. `docs/roadmap_v2/batched_execution_queue_v13.md`

## Planning documents that still matter

- `projects/ai_washing/member_seed_plan_v1.md`
- `projects/ai_washing/member_shell_readiness_v1.md`
- `projects/ai_washing/first_code_seed_decision_v1.md`
- `projects/ai_washing/labeling_common_impact_map_v1.md`

These are now background/reference notes, not the front door.
