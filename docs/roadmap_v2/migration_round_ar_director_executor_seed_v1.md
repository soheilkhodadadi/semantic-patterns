# Migration Round AR: Director Executor Seed V1

## Scope

Batch 3 from Queue V8.

Authority:
- `semantic_director.executor`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the direct `director` caller bundle onto the new authority

## Pre-Scan Result

The `executor` boundary stayed clean enough to auto-run under Queue V8.

What made it clean:
- it now sits downstream of canonical `decision`, `gates`, and `sensors`
- remaining root dependencies were already thin compatibility shims over `labcore` or canonical package surfaces
- direct caller pressure is concentrated in the CLI and root `director` regression bundle
- Atlas-adjacent adapter boundaries remain outside this round

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_executor.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/executor.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/executor.py`

Migrated callers:
- `src/semantic_ai_washing/director/cli.py`
- `tests/test_director_core.py`

New package-local test:
- `packages/director/tests/test_executor.py`
