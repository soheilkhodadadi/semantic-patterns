# Migration Round AG: Director Sensors Seed V1

## Scope

Batch 1 from Queue V5.

Authority:
- `semantic_director.sensors`

Batch:
- seed canonical package authority
- keep the root director path as a compatibility shim
- migrate the direct `director` caller bundle onto the new authority

## Pre-Scan Result

The `sensors` boundary stayed clean enough to auto-run under Queue V5.

What made it clean:
- direct caller pressure is concentrated in the `director` lane
- it improves package cohesion by removing a root dependency from
  `semantic_director.readiness`
- the one cross-lane `ai_washing` edge can safely stay on the shim for now
- the validation story is strong and localized

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_sensors.py`
- `packages/director/tests/test_readiness.py`
- `tests/test_director_sensors.py`
- `tests/test_director_core.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/sensors.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/sensors.py`

Migrated callers:
- `packages/director/src/semantic_director/readiness.py`
- `src/semantic_ai_washing/director/core/executor.py`
- `tests/test_director_sensors.py`

New package-local test:
- `packages/director/tests/test_sensors.py`
