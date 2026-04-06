# Director Main Module Grouped Migration Sheet V1

## Authority

- `semantic_director.__main__`

## Canonical package module

- `packages/director/src/semantic_director/__main__.py`

## Root compatibility shim

- `src/semantic_ai_washing/director/__main__.py`

## Direct callers moved to package authority

- package-local parity test:
  - `packages/director/tests/test_main_module.py`

## Validation gate

- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_main_module.py`
- `packages/director/tests/test_cli.py`
- package build smoke
- `git diff --check`
