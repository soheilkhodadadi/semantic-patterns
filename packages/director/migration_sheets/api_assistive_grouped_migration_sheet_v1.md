# API Assistive Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.api_assistive`

Legacy compatibility shim:
- `semantic_ai_washing.director.core.api_assistive`

## Group 1: Direct runtime callers

Files:
- `src/semantic_ai_washing/director/tasks/api_bootstrap.py`
- `tests/test_api_assistive_bootstrap.py`
- `tests/test_iteration2_parallel.py`

Gate:
- `packages/director/tests/test_api_assistive.py`
- `tests/test_api_assistive_bootstrap.py`
- `tests/test_iteration2_parallel.py -k api_assistive`
- `git diff --check`

Status:
- complete
