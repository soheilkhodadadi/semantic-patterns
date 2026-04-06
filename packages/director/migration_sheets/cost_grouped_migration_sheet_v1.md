# Cost Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.cost`

Legacy compatibility shim:
- `semantic_ai_washing.director.core.cost`

## Group 1: Direct director callers

Files:
- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/planner.py`
- `src/semantic_ai_washing/director/core/llm.py`
- `src/semantic_ai_washing/director/tasks/api_bootstrap.py`
- `tests/test_director_core.py`

Gate:
- `packages/director/tests/test_cost.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- `tests/test_api_assistive_bootstrap.py`
- package build smoke
- `git diff --check`

Status:
- complete
