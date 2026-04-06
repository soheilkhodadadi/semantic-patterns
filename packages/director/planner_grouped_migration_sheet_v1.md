# Planner Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.planner`

Legacy compatibility shim:
- `semantic_ai_washing.director.core.planner`

## Group 1: Direct runtime callers

Files:
- `src/semantic_ai_washing/director/cli.py`
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`

Gate:
- `packages/director/tests/test_planner.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`
- `tests/test_director_cli.py`
- `git diff --check`

Status:
- complete
