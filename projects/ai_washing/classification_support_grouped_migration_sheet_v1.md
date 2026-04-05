# AI-Washing Classification Support Grouped Migration Sheet V1

## Purpose

This note records the grouped migration shape used for the member-owned
classification support surface.

## Canonical member-owned authority

Current member-owned classification support surface:
- `projects/ai_washing/src/ai_washing_member/classification/preliminary_pipeline.py`
- `projects/ai_washing/src/ai_washing_member/classification/model_runtime.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/classification/preliminary_pipeline.py`
- `src/semantic_ai_washing/classification/model_runtime.py`

## Grouped caller families

### Family A: classification and evaluation callers
- `benchmark_preliminary_models.py`
- `classify_active_window_preliminary.py`
- `classify_active_window_preliminary_restartable.py`
- `evaluate_preliminary_heldout.py`
- `publish_selected_preliminary_eval.py`
- `reconcile_preliminary_classification_report.py`
- `train_binary_relevance_then_as.py`
- `train_logreg_preliminary.py`
- `train_preliminary_centroids.py`

### Family B: downstream reporting callers
- `build_preliminary_narrative_measures.py`
- `audit_preliminary_panel_inputs.py`
- `sample_heldout_v2_candidates.py`

## Shared validation gate

- `projects/ai_washing/tests/test_classification_support_member.py`
- `tests/test_preliminary_pipeline.py`
- `tests/test_preliminary_benchmarking.py`
- `tests/test_preliminary_classification_restartable.py`
- `tests/test_preliminary_phase3.py`
- `tests/test_heldout_v2_workflow.py`

## Status

This grouped migration batch has now completed successfully through:
- `docs/roadmap_v2/migration_round_n_ai_washing_classification_support_v1.md`
