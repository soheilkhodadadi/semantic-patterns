# Migration Round G: Director Schema Extraction V1

## Scope

This round promotes the first real `director` package slice into
`packages/director/src/semantic_director/`.

Included in this slice:
- `semantic_director.schemas`
- `semantic_director.__init__`
- package-local schema and export tests

Compatibility preserved in:
- `src/semantic_ai_washing/director/schemas.py`
- `src/semantic_ai_washing/director/__init__.py`

## Why this slice now

This is the cleanest first `director` extraction because it:
- defines the public model surface of the package
- is imported broadly across `director` code and tests
- does not require moving `core/`, `tasks/`, or `adapters/`
- keeps the canonical implementation self-contained behind a clear shim line

## Package authority

Canonical implementation now lives in:
- `packages/director/src/semantic_director/schemas.py`
- `packages/director/src/semantic_director/__init__.py`

Legacy compatibility paths now re-export from the package surface:
- `src/semantic_ai_washing/director/schemas.py`
- `src/semantic_ai_washing/director/__init__.py`

## Validation gate

Accept this slice only when:
- package-local schema tests pass
- package-local export parity tests pass
- root `director` tests exercising schema imports still pass
- package build smoke still succeeds

## Outcome

This round makes `packages/director` materially real without forcing a larger
control-plane extraction too early.
