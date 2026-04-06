# Migration Round AF: Director Decision Seed V1

## Scope

Batch 3 from Queue V4.

Authority:
- `semantic_director.decision`

Batch:
- seed canonical package authority
- keep the root director path as a compatibility shim
- migrate the direct `cli`, `executor`, and core regression callers onto the new authority

## Pre-Scan Result

The `decision` boundary stayed clean enough to auto-run under Queue V4.

What made it clean:
- direct caller pressure is concentrated in `cli`, `executor`, and the core test bundle
- it stays fully inside the `director` lane
- it does not pull Atlas-facing adapters into the package boundary
- it is a natural rotation after the two `ai_washing` held-out rounds

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_decision.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/decision.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/decision.py`

Migrated callers:
- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/executor.py`
- `tests/test_director_core.py`

New package-local test:
- `packages/director/tests/test_decision.py`
