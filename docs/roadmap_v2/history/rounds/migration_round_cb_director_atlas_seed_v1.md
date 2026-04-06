# Migration Round CB: Director Atlas Seed V1

## Scope

Batch 3 from Queue V20.

Authority:
- `semantic_director.atlas`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the snapshot/tooling-policy caller bundle onto the new authority

## Pre-Scan Result

The `atlas` boundary stayed clean enough to auto-run under Queue V20.

What made it clean:
- the Atlas surface stays read-only and policy-driven
- direct caller pressure is concentrated in the isolated-wrapper test and the
  package snapshot ingestor
- it closes the remaining snapshot-adapter dependency chain without opening the
  separate hygiene queue or broader API-runtime work

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_atlas.py`
- `tests/test_director_tooling_policy.py -k "atlas_runs_in_isolated_cwd"`
- `packages/director/tests/test_snapshot.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/atlas.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/adapters/atlas.py`

Migrated callers:
- `packages/director/src/semantic_director/snapshot.py`
- `tests/test_director_tooling_policy.py`

New package-local test:
- `packages/director/tests/test_atlas.py`
