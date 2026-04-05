# Director First Extraction Slice V1

## Recommendation

The first real extraction slice for `director` should be:
- `src/semantic_ai_washing/director/schemas.py`
- `src/semantic_ai_washing/director/__init__.py`

and nothing larger in the same round.

## Why this slice is first

This is the cleanest package-authoritative opening for `director` because it:
- defines the public model surface of the package
- is already imported broadly across `director` and a few adjacent callers
- does not depend on root artifact lanes like `director/`
- does not yet force a split of `core/`, `tasks/`, or `adapters/`

## What should not be in the first slice

Do not include these in the first extraction round:
- `director/core/`
- `director/tasks/`
- `director/adapters/`
- CLI entry points
- root `director/` config or artifact lanes

Those are all real package candidates later, but they are not the lowest-risk
starting point.

## Canonical direction

After the first slice, the intended direction should be:
- canonical package path:
  - `packages/director/src/semantic_director/`
- compatibility path:
  - `src/semantic_ai_washing/director/`

The same copy-plus-shim discipline used for `labcore` should apply here.

## Proposed contents of the first slice

Package-authoritative files:
- `packages/director/src/semantic_director/schemas.py`
- `packages/director/src/semantic_director/__init__.py`

Compatibility shims:
- `src/semantic_ai_washing/director/schemas.py`
- `src/semantic_ai_washing/director/__init__.py`

Package-local tests:
- seed import test stays
- add one schema serialization test
- add one package export parity test

## Acceptance gate

The first `director` extraction slice should be accepted only when:
- package-local schema tests pass
- root `director` tests that exercise schema imports still pass
- root `semantic_ai_washing.director` exports remain stable
- no root `director/` artifact lane assumptions leak into the package code

## Bottom line

The first `director` extraction should start with the schema and export surface,
not with orchestration internals.
