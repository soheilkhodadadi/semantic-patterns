# Initialize Review Sheet Grouped Migration Sheet V1

## Authority

Canonical member authority:
- `ai_washing_member.labeling.initialize_review_sheet`

Legacy compatibility shim:
- `semantic_ai_washing.labeling.initialize_review_sheet`

## Group 1: Direct workflow callers

Files:
- `src/semantic_ai_washing/labeling/benchmark_prompt_variants.py`
- `tests/test_iteration2_parallel.py`

Gate:
- `projects/ai_washing/tests/test_initialize_review_sheet_member.py`
- `tests/test_iteration2_parallel.py`
- `git diff --check`

Status:
- complete
