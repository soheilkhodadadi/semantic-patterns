# Migration Round CP

## Queue

Queue V25

## Batch

`semantic_director.responses_transport_boundary_cleanup`

## Purpose

Switch `semantic_director.api_bootstrap` from root compatibility transport and
runtime imports to the canonical shared `labcore` surfaces where the
equivalents are already stable and exact.

## Expected surfaces

Canonical responses transport target:
- `semantic_labcore.openai_responses`

Canonical runtime helper target:
- `semantic_labcore.runtime`

## Gate

Required gate:
- targeted Ruff
- targeted `py_compile`
- focused api-bootstrap and related `director` tests
- `git diff --check`

## Outcome

Completed cleanly.

Validated with:
- targeted Ruff on changed package module and queue docs
- `python -m py_compile packages/director/src/semantic_director/api_bootstrap.py`
- focused pytest bundle
  - `packages/director/tests/test_api_bootstrap.py`
  - `packages/director/tests/test_api_assistive.py`
  - `tests/test_api_assistive_bootstrap.py`
  - `tests/test_director_cli.py`
- result: `21 passed`
