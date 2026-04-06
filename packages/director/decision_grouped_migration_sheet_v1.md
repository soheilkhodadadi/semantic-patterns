# Decision Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.decision`

Legacy compatibility shim:
- `semantic_ai_washing.director.core.decision`

## Group 1: Direct runtime callers

Files:
- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/executor.py`
- `tests/test_director_core.py`

Gate:
- `packages/director/tests/test_decision.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke

Status:
- complete
