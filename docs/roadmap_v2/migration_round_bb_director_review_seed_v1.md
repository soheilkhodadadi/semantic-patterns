# Migration Round BB: Director Review Seed V1

## Scope

Batch 1 from Queue V12.

Authority:
- `semantic_director.review`

Batch:
- seed canonical package authority
- keep the legacy root path as a compatibility shim
- migrate direct runtime callers onto the package-owned authority where the boundary stays clean

## Pre-Scan Result

The `review` boundary stayed clean enough to auto-run under Queue V12.

What made it clean:
- most package-side dependencies were already canonical before this round
- direct caller leverage is concentrated in the CLI and focused director review/playbook tests
- the legacy root shim can re-export the same `ReviewEngine` class object, which keeps the playbooks monkeypatch path stable
- no Atlas-adjacent adapter move is required for this batch

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_review.py`
- `tests/test_director_review.py`
- `tests/test_director_playbooks.py`
- `tests/test_director_cli.py`
- `semantic-director` build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/review.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/core/review.py`

Migrated callers:
- `src/semantic_ai_washing/director/cli.py`

New package test:
- `packages/director/tests/test_review.py`
