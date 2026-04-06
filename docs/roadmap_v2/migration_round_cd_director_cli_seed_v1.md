# Migration Round CD: Director CLI Seed V1

## Scope

Batch 2 from Queue V21.

Authority:
- `semantic_director.cli`

Batch:
- seed canonical package authority
- keep the root CLI path as a compatibility shim
- move the direct CLI caller bundle onto the package path
- switch package-owned command strings onto the canonical CLI module path

## Pre-Scan Result

The `cli` boundary stayed clean enough to follow canonical `api_bootstrap`.

What made it clean:
- the queue already opened the runtime-entrypoint lane with the smaller task
  runtime
- direct caller pressure is concentrated in a focused CLI/review/tooling bundle
- the remaining work is now mostly entrypoint routing and canonical command
  strings, not unrelated runtime logic

## Validation Gate

Default gate for this round:
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
