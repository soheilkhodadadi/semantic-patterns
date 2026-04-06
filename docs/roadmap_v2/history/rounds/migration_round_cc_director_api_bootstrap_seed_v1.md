# Migration Round CC: Director API Bootstrap Seed V1

## Scope

Batch 1 from Queue V21.

Authority:
- `semantic_director.api_bootstrap`

Batch:
- seed canonical package authority
- keep the root task path as a compatibility shim
- move the direct assistive/bootstrap caller bundle onto the new authority

## Pre-Scan Result

The `api_bootstrap` boundary stayed clean enough to open Queue V21.

What made it clean:
- it is the smallest remaining non-adapter runtime surface in `director`
- direct caller pressure is concentrated in the bootstrap smoke-test bundle
- it opens the remaining runtime-entrypoint lane without forcing the whole CLI
  move first

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_api_bootstrap.py`
- `tests/test_api_assistive_bootstrap.py`
- `tests/test_director_review.py -k "api_bootstrap"`
- package build smoke
- `git diff --check`
