# Batched Execution Queue V13

## Purpose

This queue starts after Queue V12 completed cleanly.

It rotates back into `ai_washing` and uses Protocol V2 to move a coherent assistive calibration workflow inside the member-owned lane.

## Planning assumptions

- keep Protocol V2 as the per-round safety spine
- keep one authority and one lane per code batch
- keep the hygiene queue isolated
- prefer one coherent active workflow when a strong shared regression bundle already exists
- use `tests/test_iteration2_parallel.py` as the shared root gate for this queue

## Immediate execution queue

### Batch 1

Authority:
- `ai_washing_member.labeling.assistive_prelabel_batch`

Lane:
- `ai_washing`

Why next:
- strongest clean opener after Queue V12
- direct workflow leverage is concentrated in the assistive calibration tests and restartable wrapper
- Queue V12 lowered the dependency risk by making `semantic_director.api_assistive` canonical

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_assistive_prelabel_batch_member.py`
- `tests/test_iteration2_parallel.py -k "generate_assistive_prelabels"`
- `tests/test_restartable_jobs.py -k "run_restartable_prelabel"`
- `git diff --check`

Status:
- complete

### Batch 2

Authority:
- `ai_washing_member.labeling.benchmark_prompt_variants`

Lane:
- `ai_washing`

Why next:
- direct follow-on after `assistive_prelabel_batch`
- keeps the same calibration workflow inside the member-owned lane
- the shared root gate already covers the benchmark path

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_benchmark_prompt_variants_member.py`
- `tests/test_iteration2_parallel.py -k "benchmark_prompt_variants"`
- `git diff --check`

Status:
- planned

### Batch 3

Authority:
- `ai_washing_member.labeling.score_prelabel_sheet`

Lane:
- `ai_washing`

Why next:
- closes the assistive calibration workflow with the scoring/report utility that reads the generated prelabels
- uses the same root calibration gate without reopening the hygiene question
- keeps Queue V13 as one coherent current-stage workflow family

Default gate:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_score_prelabel_sheet_member.py`
- `tests/test_iteration2_parallel.py -k "score_prelabel_sheet"`
- `git diff --check`

Status:
- planned

## Current recommendation

Next in Queue V13:

1. Batch 1:
   - `ai_washing_member.labeling.assistive_prelabel_batch`
2. Batch 2:
   - `ai_washing_member.labeling.benchmark_prompt_variants`
3. Batch 3:
   - `ai_washing_member.labeling.score_prelabel_sheet`
