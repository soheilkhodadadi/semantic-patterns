# FF12 Mapping Grouped Migration Sheet V1

## Authority

- canonical authority: `ai_washing_member.labeling.ff12_mapping`
- legacy compatibility shim:
  - `src/semantic_ai_washing/labeling/ff12_mapping.py`

## Batch Shape

This migration stays inside one authority and one lane:

- authority: `ff12_mapping`
- lane: `ai_washing`
- compatibility strategy: legacy shim retained
- validation gate: member test + focused root `ai_washing` regressions

## Caller Groups

### Group 1: Member-Owned Data Edge

- `projects/ai_washing/src/ai_washing_member/data/build_filing_manifest.py`

### Group 2: Root Labeling Edge

- `src/semantic_ai_washing/labeling/build_labeling_sample.py`

### Group 3: Direct Validation Edge

- `projects/ai_washing/tests/test_ff12_mapping_member.py`
- `tests/test_labeling_phase1.py`
- `tests/test_sentence_table_pilot.py`
- `tests/test_iteration2_parallel.py`

## Status

- authority seeded: complete
- grouped caller migration: complete
- validation gate: complete
