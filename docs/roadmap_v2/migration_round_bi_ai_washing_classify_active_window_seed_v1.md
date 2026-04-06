# Migration Round BI: AI-Washing Classify Active Window Seed V1

## Purpose

Seed the canonical member-owned active-window classification authority for the preliminary classification lane and migrate its direct callers.

## Canonical authority

- `projects/ai_washing/src/ai_washing_member/classification/classify_active_window_preliminary.py`

## Compatibility shim

- `src/semantic_ai_washing/classification/classify_active_window_preliminary.py`

## Direct callers migrated

- `tests/test_preliminary_phase3.py`
- `tests/test_preliminary_benchmarking.py`
- `src/semantic_ai_washing/classification/classify_active_window_preliminary_restartable.py`
- `src/semantic_ai_washing/classification/reconcile_preliminary_classification_report.py`

## Validation gate

- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_classify_active_window_preliminary_member.py`
- `tests/test_preliminary_phase3.py -k "preliminary_training_eval_classification"`
- `tests/test_preliminary_classification_restartable.py`
- `git diff --check`
