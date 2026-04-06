# Migration Round CA: Director Documents Seed V1

## Scope

Batch 2 from Queue V20.

Authority:
- `semantic_director.documents`

Batch:
- seed canonical package authority
- keep the root project path as a compatibility shim
- migrate the snapshot document-ingestion caller bundle onto the new authority

## Pre-Scan Result

The `documents` boundary stayed clean enough to auto-run under Queue V20.

What made it clean:
- it is the natural follow-on after canonical iteration-log parsing
- `semantic_director.snapshot` is the primary caller and stays inside the same
  package lane
- the parser boundary is compact and easy to validate without widening into
  unrelated runtime tasks

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_documents.py`
- `packages/director/tests/test_snapshot.py`
- package build smoke
- `git diff --check`

## Result

Status:
- completed

Canonical package authority:
- `packages/director/src/semantic_director/documents.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/director/adapters/documents.py`

Migrated callers:
- `packages/director/src/semantic_director/snapshot.py`

New package-local test:
- `packages/director/tests/test_documents.py`
