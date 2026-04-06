# Director API Bootstrap Grouped Migration Sheet V1

## Authority

- `semantic_director.api_bootstrap`

## Canonical package module

- `packages/director/src/semantic_director/api_bootstrap.py`

## Root compatibility shim

- `src/semantic_ai_washing/director/tasks/api_bootstrap.py`

## Direct callers moved to package authority

- `tests/test_api_assistive_bootstrap.py`
- package-local parity test:
  - `packages/director/tests/test_api_bootstrap.py`

## Runtime/fixture follow-ons moved in the same batch

- `tests/test_director_review.py`
  - review fixture command strings now point at
    `python -m semantic_director.api_bootstrap`

## Validation gate

- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_api_bootstrap.py`
- `tests/test_api_assistive_bootstrap.py`
- `tests/test_director_review.py -k "api_bootstrap"`
- package build smoke
- `git diff --check`
