# Migration Round AK: Director Snapshot Seed V1

## Scope

Batch 2 from Queue V6.

Authority:
- `semantic_director.snapshot`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the direct `director` caller bundle onto the new authority

## Pre-Scan Result

The `snapshot` boundary stayed clean enough to auto-run under Queue V6.

What made it clean:
- direct caller pressure is concentrated in `director.cli` and the core
  snapshot regression bundle
- the implementation is compact and self-contained
- Atlas-adjacent adapter wiring stays repo-local and can remain on the adapter
  boundary for now
- the package boundary value is real without forcing a wider adapter migration

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_snapshot.py`
- `packages/director/tests/test_*.py`
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/snapshot.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/snapshot.py`

Migrated callers:
- `src/semantic_ai_washing/director/cli.py`
- `tests/test_director_core.py`

New package-local test:
- `packages/director/tests/test_snapshot.py`
