# Migration Round AO: Director Gates Seed V1

## Scope

Batch 3 from Queue V7.

Authority:
- `semantic_director.gates`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the direct `director` caller bundle onto the new authority

## Pre-Scan Result

The `gates` boundary stayed clean enough to auto-run under Queue V7.

What made it clean:
- the implementation is compact and has one clear direct runtime consumer
- it is a useful downstream package boundary for the future `executor` move
- the regression story is focused in the package gate test and core executor bundle
- there is no Atlas-adjacent or cross-project dependency pressure here

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_gates.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/gates.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/gates.py`

Migrated callers:
- `src/semantic_ai_washing/director/core/executor.py`

New package-local test:
- `packages/director/tests/test_gates.py`
