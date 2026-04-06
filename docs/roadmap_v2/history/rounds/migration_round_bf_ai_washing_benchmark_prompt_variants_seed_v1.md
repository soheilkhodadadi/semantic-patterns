# Migration Round BF: AI-Washing Benchmark Prompt Variants Seed V1

## Scope

Batch 2 from Queue V13.

Authority:
- `ai_washing_member.labeling.benchmark_prompt_variants`

Batch:
- seed canonical member authority
- keep the legacy root path as a compatibility shim
- preserve the existing root monkeypatch path by forwarding the patched `generate_assistive_prelabels` symbol into the member-owned module

## Pre-Scan Result

The `benchmark_prompt_variants` boundary stayed clean enough to auto-run after Batch 1.

What made it clean:
- the assistive prelabel authority is already member-owned from Batch 1
- the root tests patch the benchmark module's local `generate_assistive_prelabels` symbol, which the compatibility shim can preserve cleanly
- the workflow-level regression bundle is already concentrated in `tests/test_iteration2_parallel.py`
- no Atlas-adjacent adapter move is required for this batch

## Validation Gate

Default gate for this round:
- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_benchmark_prompt_variants_member.py`
- `tests/test_iteration2_parallel.py -k "benchmark_prompt_variants"`
- `git diff --check`

## Result

Status:
- completed

Canonical member authority:
- `projects/ai_washing/src/ai_washing_member/labeling/benchmark_prompt_variants.py`

Legacy compatibility shim:
- `src/semantic_ai_washing/labeling/benchmark_prompt_variants.py`

New member test:
- `projects/ai_washing/tests/test_benchmark_prompt_variants_member.py`
