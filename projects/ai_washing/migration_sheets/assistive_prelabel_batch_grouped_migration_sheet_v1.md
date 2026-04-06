# Assistive Prelabel Batch Grouped Migration Sheet V1

## Authority

Canonical member authority:
- `ai_washing_member.labeling.assistive_prelabel_batch`

Legacy compatibility shim:
- `semantic_ai_washing.labeling.assistive_prelabel_batch`

## Group 1: Direct workflow callers

Files:
- `src/semantic_ai_washing/labeling/benchmark_prompt_variants.py`
- `src/semantic_ai_washing/labeling/run_assistive_prelabel_restartable.py`
- `tests/test_iteration2_parallel.py`
- `tests/test_restartable_jobs.py`

Gate:
- `projects/ai_washing/tests/test_assistive_prelabel_batch_member.py`
- `tests/test_iteration2_parallel.py -k "generate_assistive_prelabels"`
- `tests/test_restartable_jobs.py -k "run_restartable_prelabel"`
- `git diff --check`

Status:
- complete
