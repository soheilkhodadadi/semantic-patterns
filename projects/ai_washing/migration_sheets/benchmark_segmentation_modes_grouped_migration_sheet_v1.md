# Benchmark Segmentation Modes Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.data.benchmark_segmentation_modes`
- legacy compatibility shim:
  - `src/semantic_ai_washing/data/benchmark_segmentation_modes.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `benchmark_segmentation_modes`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused local smoke coverage

## Caller Groups

### Group 1: Direct Validation Edge

- `projects/ai_washing/tests/test_benchmark_segmentation_modes_member.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete

## Known Dependency Note

This authority stays intentionally narrow:
- it benchmarks segmentation modes through the already-canonical
  `ai_washing_member.data.extract_sentence_table` surface
- it leaves the broader active-window materialization lane for Queue V18
