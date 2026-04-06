# Migration Round BD: Director API Assistive Seed V1

## Scope

Batch 3 from Queue V12.

Authority:
- `semantic_director.api_assistive`

Batch:
- seed canonical package authority
- keep the legacy root path as a compatibility shim
- migrate the director-owned task and focused bootstrap test onto the package-owned authority
- keep broader integration callers on the compatibility path where that preserves queue discipline

## Pre-Scan Result

The `api_assistive` boundary stayed clean enough to auto-run after Batches 1 and 2.

What made it clean:
- the focused bootstrap test only monkeypatches task-local response transport hooks, not the shared api-assistive helper surface
- the director-owned task is the clean direct runtime caller for this authority
- broader assistive-labeling integrations can stay on the compatibility path without weakening package ownership
- no Atlas-adjacent adapter move is required for this batch

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_api_assistive.py`
- `tests/test_api_assistive_bootstrap.py`
- `tests/test_iteration2_parallel.py -k api_assistive`
- `semantic-director` build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/api_assistive.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/api_assistive.py`

Migrated callers:
- `src/semantic_ai_washing/director/tasks/api_bootstrap.py`
- `tests/test_api_assistive_bootstrap.py`

Compatibility callers intentionally retained:
- `tests/test_iteration2_parallel.py`
- `src/semantic_ai_washing/labeling/assistive_prelabel_batch.py`

New package test:
- `packages/director/tests/test_api_assistive.py`
