# Director CLI Grouped Migration Sheet V1

## Authority

- `semantic_director.cli`

## Canonical package module

- `packages/director/src/semantic_director/cli.py`

## Root compatibility shim

- `src/semantic_ai_washing/director/cli.py`

## Direct callers moved to package authority

- `tests/test_director_cli.py`
- `tests/test_director_review.py`
- `tests/test_director_tooling_policy.py`
- `tests/test_director_playbooks.py`
- package-local parity test:
  - `packages/director/tests/test_cli.py`

## Package-owned follow-ons updated in the same batch

- `packages/director/src/semantic_director/planner.py`
- `packages/director/src/semantic_director/render.py`
- `tests/test_director_roadmap_model.py`

## Validation gate

- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_cli.py`
- `tests/test_director_cli.py`
- `tests/test_director_playbooks.py`
- `tests/test_director_review.py`
- `tests/test_director_tooling_policy.py`
- `tests/test_director_roadmap_model.py -k "review --iteration 1 or kickoff --iteration 3"`
- package build smoke
- `git diff --check`
