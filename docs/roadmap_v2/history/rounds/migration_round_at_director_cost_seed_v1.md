# Migration Round AT: Director Cost Seed V1

## Scope

Batch 2 from Queue V9.

Authority:
- `semantic_director.cost`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate direct `director` caller surfaces onto the new authority
- leave `ai_washing` assistive callers on the compatibility path for now

## Pre-Scan Result

The `cost` boundary stayed clean enough to auto-run under Queue V9.

What made it clean:
- it sits downstream of canonical audit/runtime/schema surfaces
- direct `director` caller pressure is concentrated in CLI, planner, LLM, and API smoke-test utilities
- `ai_washing` assistive callers can stay on the compatibility shim without weakening the package move
- Atlas-adjacent adapter boundaries remain outside this round

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_cost.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- `tests/test_api_assistive_bootstrap.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/cost.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/cost.py`

Migrated callers:
- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/planner.py`
- `src/semantic_ai_washing/director/core/llm.py`
- `src/semantic_ai_washing/director/tasks/api_bootstrap.py`
- `tests/test_director_core.py`

New package-local test:
- `packages/director/tests/test_cost.py`
