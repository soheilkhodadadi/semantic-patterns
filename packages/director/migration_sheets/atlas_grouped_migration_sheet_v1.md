# Atlas Grouped Migration Sheet V1

## Authority

Canonical package authority:
- `semantic_director.atlas`

Legacy compatibility shim:
- `semantic_ai_washing.director.adapters.atlas`

## Group 1: Direct snapshot/tooling-policy callers

Files:
- `packages/director/src/semantic_director/snapshot.py`
- `tests/test_director_tooling_policy.py`

Gate:
- `packages/director/tests/test_atlas.py`
- `tests/test_director_tooling_policy.py -k "atlas_runs_in_isolated_cwd"`
- `packages/director/tests/test_snapshot.py`
- package build smoke

Status:
- complete
