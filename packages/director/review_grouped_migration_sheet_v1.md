# Review Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.review`

Legacy compatibility shim:
- `semantic_ai_washing.director.core.review`

## Group 1: Direct runtime callers

Files:
- `src/semantic_ai_washing/director/cli.py`
- `tests/test_director_playbooks.py`
- `tests/test_director_review.py`

Gate:
- `packages/director/tests/test_review.py`
- `tests/test_director_review.py`
- `tests/test_director_playbooks.py`
- `tests/test_director_cli.py`
- `git diff --check`

Status:
- complete
