# Executor Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.executor`

Legacy compatibility shim:
- `semantic_ai_washing.director.core.executor`

## Group 1: Direct callers

Files:
- `src/semantic_ai_washing/director/cli.py`
- `tests/test_director_core.py`

Gate:
- `packages/director/tests/test_executor.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

Status:
- complete
