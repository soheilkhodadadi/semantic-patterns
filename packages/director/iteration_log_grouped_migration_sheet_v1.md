# Iteration Log Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.iteration_log`

Legacy compatibility shim:
- `semantic_ai_washing.director.adapters.iteration_log`

## Group 1: Direct snapshot/parser callers

Files:
- `packages/director/src/semantic_director/snapshot.py`
- `tests/test_director_core.py`

Gate:
- `packages/director/tests/test_iteration_log.py`
- `tests/test_director_core.py -k "snapshot_parser_handles_missing_and_conflicting_phase_entries"`
- `packages/director/tests/test_snapshot.py`
- package build smoke

Status:
- complete
