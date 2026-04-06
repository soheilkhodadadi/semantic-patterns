# Optimizer Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.optimizer`

Legacy compatibility shim:
- `semantic_ai_washing.director.core.optimizer`

## Group 1: Direct runtime callers

Files:
- `src/semantic_ai_washing/director/cli.py`
- `tests/test_director_roadmap_model.py`

Gate:
- `packages/director/tests/test_optimizer.py`
- `tests/test_director_roadmap_model.py`
- `tests/test_director_cli.py`
- `git diff --check`

Status:
- complete
