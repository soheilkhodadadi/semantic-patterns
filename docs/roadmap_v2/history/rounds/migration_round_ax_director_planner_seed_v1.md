# Migration Round AX: Director Planner Seed V1

## Scope

Batch 3 from Queue V10.

Authority:
- `semantic_director.planner`

Batch:
- seed canonical package authority
- keep the legacy root path as a compatibility shim
- migrate direct runtime callers and tests onto the package-owned authority

## Pre-Scan Result

The `planner` boundary stayed clean enough to auto-run under Queue V10.

What made it clean:
- it now sits downstream of canonical `cost`, `llm`, `roadmap_model`, and `task_graph`
- direct caller pressure is concentrated in the CLI and focused director test bundles
- package-side schema and policy dependencies already exist
- no Atlas-adjacent adapter move is required for this batch

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_planner.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`
- `tests/test_director_cli.py`
- `semantic-director` build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/planner.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/planner.py`

Migrated callers:
- `src/semantic_ai_washing/director/cli.py`
- `tests/test_director_core.py`
- `tests/test_director_roadmap_model.py`

New package test:
- `packages/director/tests/test_planner.py`
