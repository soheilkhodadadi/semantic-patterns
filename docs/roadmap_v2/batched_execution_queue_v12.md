# Batched Execution Queue V12

## Purpose

This queue starts after Queue V11 completed cleanly.

It rotates back into the `director` lane and uses Protocol V2 to move a compact control-plane chain without mixing in hygiene work.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- prefer the cleaner control-plane opener over the still monkeypatch-sensitive assistive-labeling opener
- use the director CLI/review gate as the shared root bundle for this queue

## Immediate execution queue

### Batch 1

Authority:
- `semantic_director.review`

Lane:
- `director`

Why next:
- strongest clean opener after Queue V11
- direct CLI/test leverage is already concentrated here
- keeps the monkeypatch-sensitive playbooks test on a compatibility path while package ownership becomes canonical

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_review.py`
- `tests/test_director_review.py`
- `tests/test_director_playbooks.py`
- `tests/test_director_cli.py`
- `semantic-director` build smoke
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `semantic_director.optimizer`

Lane:
- `director`

Why next:
- direct downstream follow-on after `review`
- dependency chain is already mostly canonical
- direct caller pressure is concentrated in the CLI and roadmap-model bundle

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_optimizer.py`
- `tests/test_director_roadmap_model.py`
- `tests/test_director_cli.py`
- `semantic-director` build smoke
- `git diff --check`

Status:
- complete

### Batch 3

Authority:
- `semantic_director.api_assistive`

Lane:
- `director`

Why next:
- closes the compact control-plane chain if the follow-on boundary stays clean
- keeps the queue in `director` without opening the assistive-labeling member lane yet
- can migrate the director task and focused bootstrap tests while leaving broader integration callers on the compatibility path

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `packages/director/tests/test_api_assistive.py`
- `tests/test_api_assistive_bootstrap.py`
- `tests/test_iteration2_parallel.py -k api_assistive`
- `semantic-director` build smoke
- `git diff --check`

Status:
- planned

## Current recommendation

Next in Queue V12:

1. Batch 1:
   - `semantic_director.review`
2. Batch 2:
   - `semantic_director.optimizer`
3. Batch 3 if the pre-scan stays clean:
   - `semantic_director.api_assistive`
