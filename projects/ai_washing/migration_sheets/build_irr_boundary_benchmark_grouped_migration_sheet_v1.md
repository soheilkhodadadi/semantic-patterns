# Build IRR Boundary Benchmark Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.labeling.build_irr_boundary_benchmark`
- legacy compatibility shim:
  - `src/semantic_ai_washing/labeling/build_irr_boundary_benchmark.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `build_irr_boundary_benchmark`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test for benchmark publication output

## Caller Groups

### Group 1: Direct Benchmark Publication Edge

- `projects/ai_washing/tests/test_build_irr_boundary_benchmark_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete

## Known Dependency Note

This authority is intentionally narrow:
- it publishes a diagnostic benchmark from adjudication outputs already owned by
  the member labeling workflow
- it does not reopen dormant restartable wrappers or older benchmark lanes
