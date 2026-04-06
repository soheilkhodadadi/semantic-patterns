# Migration Round AI: Director Playbooks Seed V1

## Scope

Batch 3 from Queue V5.

Authority:
- `semantic_director.playbooks`

Batch:
- seed canonical package authority
- keep the root director path as a compatibility shim
- migrate the direct `director` caller and test bundle onto the new authority

## Pre-Scan Result

The `playbooks` boundary stayed clean enough to auto-run under Queue V5.

What made it clean:
- it remains fully inside the `director` lane
- direct caller pressure is concentrated in `cli`, `review`, and the playbook tests
- it depends on already-canonical `semantic_director.schemas`
- it does not pull Atlas-facing adapters or project-member code into the batch

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_playbooks.py`
- `tests/test_director_playbooks.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/playbooks.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/playbooks.py`

Migrated callers:
- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/review.py`
- `tests/test_director_playbooks.py`

New package-local test:
- `packages/director/tests/test_playbooks.py`
