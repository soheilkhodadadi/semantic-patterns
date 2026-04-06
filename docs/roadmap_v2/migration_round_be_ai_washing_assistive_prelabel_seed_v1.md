# Migration Round BE: AI-Washing Assistive Prelabel Seed V1

## Scope

Batch 1 from Queue V13.

Authority:
- `ai_washing_member.labeling.assistive_prelabel_batch`

Batch:
- seed canonical member authority
- keep the legacy root path as a compatibility shim
- migrate direct workflow callers onto the member-owned authority where the boundary stays clean

## Pre-Scan Result

The `assistive_prelabel_batch` boundary stayed clean enough to auto-run under Queue V13.

What made it clean:
- Queue V12 already moved the shared `api_assistive` helpers into `semantic_director`
- the existing root integration tests can stay truthful if the root shim forwards monkeypatched transport hooks into the member-owned module
- direct workflow callers are concentrated in the prompt-benchmark and restartable assistive runners
- no Atlas-adjacent adapter move is required for this batch

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_assistive_prelabel_batch_member.py`
- `tests/test_iteration2_parallel.py -k "generate_assistive_prelabels"`
- `tests/test_restartable_jobs.py -k "run_restartable_prelabel"`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/assistive_prelabel_batch.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/assistive_prelabel_batch.py`

Migrated callers:
- `src/semantic_ai_washing/labeling/benchmark_prompt_variants.py`
- `src/semantic_ai_washing/labeling/run_assistive_prelabel_restartable.py`

New member test:
- `projects/ai_washing/tests/test_assistive_prelabel_batch_member.py`
