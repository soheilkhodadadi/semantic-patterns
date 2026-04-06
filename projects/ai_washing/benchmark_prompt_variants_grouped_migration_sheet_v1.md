# Benchmark Prompt Variants Grouped Migration Sheet V1

## Authority

Canonical member authority:
- `ai_washing_member.labeling.benchmark_prompt_variants`

Legacy compatibility shim:
- `semantic_ai_washing.labeling.benchmark_prompt_variants`

## Group 1: Direct workflow callers

Files:
- `tests/test_iteration2_parallel.py`

Gate:
- `projects/ai_washing/tests/test_benchmark_prompt_variants_member.py`
- `tests/test_iteration2_parallel.py -k "benchmark_prompt_variants"`
- `git diff --check`

Status:
- complete
