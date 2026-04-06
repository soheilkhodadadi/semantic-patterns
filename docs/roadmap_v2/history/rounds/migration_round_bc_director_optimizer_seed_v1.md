# Migration Round BC: Director Optimizer Seed V1

## Scope

Batch 2 from Queue V12.

Authority:
- `semantic_director.optimizer`

Batch:
- seed canonical package authority
- keep the legacy root path as a compatibility shim
- migrate direct runtime callers and tests onto the package-owned authority

## Pre-Scan Result

The `optimizer` boundary stayed clean enough to auto-run under Queue V12.

What made it clean:
- it now sits downstream of canonical `readiness`, `render`, `roadmap_model`, and `task_graph`
- direct caller pressure is concentrated in the CLI and roadmap-model regression bundle
- the remaining root-facing dependencies are limited to runtime/schema helpers that already have package-owned equivalents
- no Atlas-adjacent adapter move is required for this batch

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_optimizer.py`
- `tests/test_director_roadmap_model.py`
- `tests/test_director_cli.py`
- `semantic-director` build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/optimizer.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/optimizer.py`

Migrated callers:
- `src/semantic_ai_washing/director/cli.py`
- `tests/test_director_roadmap_model.py`

New package test:
- `packages/director/tests/test_optimizer.py`
