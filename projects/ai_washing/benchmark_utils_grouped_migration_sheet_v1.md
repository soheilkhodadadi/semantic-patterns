# AI-Washing Benchmark Utils Grouped Migration Sheet V1

## Purpose

This note records the grouped migration shape used for the member-owned
classification benchmark utility surface.

## Canonical member-owned authority

Current member-owned benchmark utility surface:
- `projects/ai_washing/src/ai_washing_member/classification/benchmark_utils.py`

Legacy compatibility remains in place at:
- `src/semantic_ai_washing/classification/benchmark_utils.py`

## Grouped caller families

### Family A: benchmark matrix callers
- `benchmark_preliminary_models.py`

### Family B: held-out evaluation callers
- `evaluate_preliminary_heldout.py`

## Shared validation gate

- `projects/ai_washing/tests/test_benchmark_utils_member.py`
- `tests/test_preliminary_benchmarking.py`
- `tests/test_preliminary_phase3.py`

## Status

This grouped migration batch has now completed successfully through:
- `docs/roadmap_v2/migration_round_s_ai_washing_benchmark_utils_seed_v1.md`
