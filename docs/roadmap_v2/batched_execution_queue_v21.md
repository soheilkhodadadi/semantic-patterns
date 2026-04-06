# Batched Execution Queue V21

## Purpose

This queue starts after Queue V20 completed cleanly.

It opens the remaining `director` runtime-entrypoint lane by moving the focused
API bootstrap task first, then the CLI entrypoint, then the thin `__main__`
wrapper.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- keep Atlas/private spillover watch active
- prefer the smallest runtime opener before the broader CLI surface

## Immediate execution queue

### Batch 1

Authority:
- `semantic_director.api_bootstrap`

Lane:
- `director`

Why next:
- cleanest remaining non-adapter runtime opener
- direct caller pressure already exists in the assistive/bootstrap regression
  bundle
- opens the runtime-entrypoint lane without widening into the whole CLI at once

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_api_bootstrap.py`
- `tests/test_api_assistive_bootstrap.py`
- `tests/test_director_review.py -k "api_bootstrap"`
- package build smoke
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `semantic_director.cli`

Lane:
- `director`

Why next:
- natural follow-on after canonical API bootstrap runtime
- moves the remaining direct CLI test callers onto the package path
- lets package-owned modules emit canonical CLI commands instead of root-path
  strings

Default gate:
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

Status:
- planned

### Batch 3

Authority:
- `semantic_director.__main__`

Lane:
- `director`

Why next:
- closes the queue with the last thin root-only entry wrapper
- keeps Queue V21 inside the same entrypoint lane
- gives the package a canonical `python -m semantic_director` surface

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_main_module.py`
- `packages/director/tests/test_cli.py`
- package build smoke
- `git diff --check`

Status:
- planned
