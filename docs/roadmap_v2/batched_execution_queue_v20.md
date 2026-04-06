# Batched Execution Queue V20

## Purpose

This queue starts after Queue V19 completed cleanly.

It closes the remaining `director` snapshot-adapter lane by moving iteration-log
parsing, document ingestion, and Atlas metadata access into canonical package
authorities.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- use Queue V20 to reduce the remaining root-only pressure around
  `semantic_director.snapshot`
- keep Atlas/private spillover watch active and preserve the existing read-only
  Atlas posture

## Immediate execution queue

### Batch 1

Authority:
- `semantic_director.iteration_log`

Lane:
- `director`

Why next:
- cleanest remaining snapshot-adapter opener
- direct caller pressure already exists in the focused core regression bundle
- lowers root-only dependency pressure for `semantic_director.snapshot`

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_iteration_log.py`
- `tests/test_director_core.py -k "snapshot_parser_handles_missing_and_conflicting_phase_entries"`
- `packages/director/tests/test_snapshot.py`
- package build smoke
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `semantic_director.documents`

Lane:
- `director`

Why next:
- natural follow-on after canonical iteration-log parsing
- keeps Queue V20 inside the same snapshot/document-ingestion lane
- improves package-side `SnapshotIngestor` without widening into unrelated runtime work

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_documents.py`
- `packages/director/tests/test_snapshot.py`
- package build smoke
- `git diff --check`

Status:
- complete

### Batch 3

Authority:
- `semantic_director.atlas`

Lane:
- `director`

Why next:
- closes the remaining snapshot-adapter dependency chain
- keeps the Atlas boundary read-only and policy-driven
- gives `semantic_director.snapshot` a fully package-owned adapter surface

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_atlas.py`
- `tests/test_director_tooling_policy.py -k "atlas_runs_in_isolated_cwd"`
- `packages/director/tests/test_snapshot.py`
- package build smoke
- `git diff --check`

Status:
- complete
