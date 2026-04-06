# Migration Round N: AI-Washing Classification Support Batch V1

## Purpose

This round seeds the next member-owned `ai_washing` authority surface and uses
it for the first larger-but-still-bounded batch experiment.

## Canonical authority moved in this round

New member-owned classification support surface:
- `projects/ai_washing/src/ai_washing_member/classification/preliminary_pipeline.py`
- `projects/ai_washing/src/ai_washing_member/classification/model_runtime.py`

Member-local export surface:
- `projects/ai_washing/src/ai_washing_member/classification/__init__.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/classification/preliminary_pipeline.py`
- `src/semantic_ai_washing/classification/model_runtime.py`

## Caller families migrated in the same batch

### Family A: classification and evaluation callers
- `src/semantic_ai_washing/classification/benchmark_preliminary_models.py`
- `src/semantic_ai_washing/classification/classify_active_window_preliminary.py`
- `src/semantic_ai_washing/classification/classify_active_window_preliminary_restartable.py`
- `src/semantic_ai_washing/classification/evaluate_preliminary_heldout.py`
- `src/semantic_ai_washing/classification/publish_selected_preliminary_eval.py`
- `src/semantic_ai_washing/classification/reconcile_preliminary_classification_report.py`
- `src/semantic_ai_washing/classification/train_binary_relevance_then_as.py`
- `src/semantic_ai_washing/classification/train_logreg_preliminary.py`
- `src/semantic_ai_washing/classification/train_preliminary_centroids.py`

### Family B: downstream reporting callers
- `src/semantic_ai_washing/aggregation/build_preliminary_narrative_measures.py`
- `src/semantic_ai_washing/analysis/audit_preliminary_panel_inputs.py`
- `src/semantic_ai_washing/labeling/sample_heldout_v2_candidates.py`

## Validation gate

Passed:
- `make doctor`
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- shared pytest bundle:
  - `projects/ai_washing/tests/test_classification_support_member.py`
  - `tests/test_preliminary_pipeline.py`
  - `tests/test_preliminary_benchmarking.py`
  - `tests/test_preliminary_classification_restartable.py`
  - `tests/test_preliminary_phase3.py`
  - `tests/test_heldout_v2_workflow.py`
- result: `15 passed`
- `git diff --check`

## Outcome

This larger batch passed cleanly.

It is the first successful example in this repo of:
- one authority move
- two adjacent caller families
- one shared regression gate
- one clean commit

That makes it the reference pattern for future larger-batch experiments under a
single existing lane.
