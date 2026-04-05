# AI-Washing Labeling Common Impact Map V1

## Purpose

This note bounds the future migration round for
`src/semantic_ai_washing/labeling/common.py`.

It is a planning artifact only. It does not authorize a code move by itself.

## Why this slice remains the first member-owned code seed

`labeling/common.py` is still the right first AI-washing code-seed candidate
because it is:
- clearly project-specific
- reused across labeling, classification, aggregation, and validation work
- stable enough to justify package-shaped ownership later
- not shared lab infrastructure

## Direct import surface

Current direct import families:
- labeling
  - `src/semantic_ai_washing/labeling/__init__.py`
  - `adjudicate_irr_labels.py`
  - `build_irr_boundary_benchmark.py`
  - `build_labeling_batch.py`
  - `build_labeling_sample.py`
  - `compute_irr_metrics.py`
  - `dedupe_labeled_sentences.py`
  - `diagnose_irr_disagreements.py`
  - `freeze_heldout_v2.py`
  - `freeze_split_registry.py`
  - `merge_labeling_batches.py`
  - `prepare_irr_subset.py`
  - `publish_preliminary_results_readiness.py`
  - `publish_rubric_freeze.py`
  - `qa_labeled_dataset.py`
  - `sample_heldout_v2_candidates.py`
- classification
  - `benchmark_utils.py`
  - `benchmark_preliminary_models.py`
  - `classify_active_window_preliminary.py`
  - `classify_active_window_preliminary_restartable.py`
  - `model_runtime.py`
  - `preliminary_pipeline.py`
  - `train_binary_relevance_then_as.py`
  - `train_logreg_preliminary.py`
  - `train_preliminary_centroids.py`
- aggregation and analysis
  - `src/semantic_ai_washing/aggregation/build_preliminary_narrative_measures.py`
  - `src/semantic_ai_washing/aggregation/merge_ai_with_patents.py`
  - `src/semantic_ai_washing/analysis/audit_preliminary_panel_inputs.py`
- data
  - `src/semantic_ai_washing/data/materialize_active_window_sentences.py`
- director-adjacent validation
  - `src/semantic_ai_washing/director/tasks/validation_assets.py`
- tests
  - `tests/test_labeling_batch.py`
  - `tests/test_labeling_phase1.py`
  - `tests/test_load_table_fallback.py`

## Shared helper clusters inside the module

The current slice mixes several helper clusters:
- label vocabulary and normalization
  - `ALLOWED_LABELS`
  - `ensure_allowed_label`
  - `normalize_sentence`
  - `parse_uncertain_flag`
- identity helpers
  - `compute_sentence_id`
  - `compute_sample_id`
  - `row_sha256`
- token and length helpers
  - `token_count`
  - `length_bin_from_tokens`
  - `safe_int`
- table I/O helpers
  - `load_table`
  - `write_excel`

## Migration pressure

The blast radius is manageable, but not small. The future move should group
callers deliberately instead of trying to flip the whole repo in one round.

Recommended future migration groups:
1. labeling core and tests
2. classification callers
3. aggregation and analysis callers
4. director validation caller

## Pre-move gate

Do not move this slice into a member-owned package until:
- the future `ai_washing` member import path is chosen explicitly
- grouped caller bundles are defined and ordered
- a focused regression bundle is written down for each group
- package-local tests exist for the extracted replacement surface

## Recommended next artifact

The next planning artifact for this future move should be a grouped caller
migration sheet that turns the four groups above into an execution order.
