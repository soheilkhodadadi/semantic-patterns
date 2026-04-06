# Migration Round BZ: Director Iteration Log Seed V1

## Scope

Batch 1 from Queue V20.

Authority:
- `semantic_director.iteration_log`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the direct snapshot/parser caller bundle onto the new authority

## Pre-Scan Result

The `iteration_log` boundary stayed clean enough to auto-run under Queue V20.

What made it clean:
- direct caller pressure is concentrated in the focused core parser regression
  bundle
- it is the smallest remaining snapshot-adapter authority
- it improves `semantic_director.snapshot` immediately without widening into
  Atlas or document parsing yet

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_iteration_log.py`
- `tests/test_director_core.py -k "snapshot_parser_handles_missing_and_conflicting_phase_entries"`
- `packages/director/tests/test_snapshot.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/iteration_log.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/adapters/iteration_log.py`

Migrated callers:
- `packages/director/src/semantic_director/snapshot.py`
- `tests/test_director_core.py`

New package-local test:
- `packages/director/tests/test_iteration_log.py`
