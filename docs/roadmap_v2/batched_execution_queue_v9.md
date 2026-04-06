# Batched Execution Queue V9

## Purpose

This queue starts after Queue V8 completed cleanly.

It keeps Protocol V2 as the migration spine while closing the current-stage
preliminary-results workflow in `ai_washing` before rotating into a compact
`director` cost/LLM control-runtime cleanup.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- open this cycle in `ai_washing` because the preliminary-results publisher is
  the cleanest active follow-on after Queue V8
- use the back half of the cycle to tighten one downstream `director`
  dependency chain: `cost` then `llm`
- keep the separate hygiene queue untouched

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.publish_preliminary_results_readiness`

Lane:
- `ai_washing`

Why next:
- strongest clean opener after Queue V8
- directly follows the newly canonical IRR metrics and disagreement diagnostic
  authorities
- localized regression bundle with one obvious compatibility edge

Expected batch shape:
- seed canonical member implementation
- retain legacy shim
- migrate:
  - `tests/test_irr_phase2.py`
  - any direct member-local test coverage needed for the new authority

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- member-local tests
- `tests/test_irr_phase2.py`
- `tests/test_director_roadmap_model.py`
- `git diff --check`

Status:
- complete

Fallback if pre-scan gets messy:
- rotate early to Batch 2

### Batch 2

Authority:
- `semantic_director.cost`

Lane:
- `director`

Why next:
- strongest clean `director` rotation after the preliminary-results publisher
- sits downstream of canonical audit/runtime/schema surfaces
- prepares a cleaner `llm` follow-on without touching Atlas-adjacent adapters

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate direct `director` callers and tests only
- leave `ai_washing` assistive callers on the compatibility path for now

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- package `director` tests
- `tests/test_director_core.py`
- `tests/test_director_cli.py`
- package build smoke
- `git diff --check`

Status:
- complete

Fallback if pre-scan gets messy:
- replace with a smaller `director` runtime round

### Batch 3

Authority:
- `semantic_director.llm`

Lane:
- `director`

Why next:
- clean downstream follow-on if `cost` is canonicalized first
- direct caller pressure is concentrated in planner-driven control-runtime code
- closes the cycle with a meaningful package-boundary move instead of a tail cleanup

Expected batch shape:
- seed canonical package implementation
- retain legacy shim
- migrate direct `director` callers and tests only

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- package `director` tests
- `tests/test_director_core.py`
- package build smoke
- `git diff --check`

Status:
- planned

Fallback if pre-scan gets messy:
- replace with a smaller downstream `director` control/runtime round

## Current recommendation

Next in Queue V9:

1. Batch 1 complete:
   - `ai_washing_member.labeling.publish_preliminary_results_readiness`
2. Batch 2 complete:
   - `semantic_director.cost`
3. Batch 3 planned:
   - `semantic_director.llm`
