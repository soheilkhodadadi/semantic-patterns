# Next Candidate Surface Scan V1

## Purpose

This note records the first candidate-surface scan performed after adopting
`fast_safe_migration_protocol_v2.md`.

The goal was to answer two questions:
1. what still remains under already-member-owned authorities
2. which next batch is real rather than artificially inflated

## Established member-owned surfaces reviewed

Reviewed authorities already in force:
- `ai_washing_member.labeling.common`
- `ai_washing_member.classification.preliminary_pipeline`
- `ai_washing_member.classification.model_runtime`
- `ai_washing_member.data.index_sec_filings`
- `ai_washing_member.data.extract_sentence_table`

## Remaining direct legacy-root pressure

Remaining direct legacy-root imports found during the scan:
- `tests/test_preliminary_pipeline.py`
- `tests/test_preliminary_benchmarking.py`
- `tests/test_source_index_contract.py`
- `projects/ai_washing/tests/test_labeling_common_member.py`

Interpretation:
- `labeling.common` still had one intentional compatibility-check edge
- `classification support` still had two direct root test callers
- `index_sec_filings` still had one direct root contract test
- `extract_sentence_table` had no meaningful direct root tail left after Round P

## Candidate assessment

### Candidate 1: classification support test tail

Authority:
- `ai_washing_member.classification.preliminary_pipeline`
- `ai_washing_member.classification.model_runtime`

Remaining direct callers:
- `tests/test_preliminary_pipeline.py`
- `tests/test_preliminary_benchmarking.py`

Assessment:
- honest
- same lane
- same authority surface
- clear shared gate
- small, but still worth doing

### Candidate 2: source index contract tail

Authority:
- `ai_washing_member.data.index_sec_filings`

Remaining direct caller:
- `tests/test_source_index_contract.py`

Assessment:
- honest
- too small to count as the next meaningful larger batch by itself

### Candidate 3: another already-member-owned larger batch

Assessment:
- not currently available without stretching the family definition
- the remaining established-authority pressure is now sparse rather than deep

## Decision

Chosen next batch:
- the classification support test tail

Why:
- it is the largest remaining honest batch under an already-member-owned
  authority
- it fits the V2 protocol cleanly
- it avoids opening a fresh authority before we need to

## Implication for the next phase

After the classification support test tail, the repo is likely close to
exhausting the meaningful established-authority follow-on work for the current
`ai_washing` member-owned surfaces.

That means the next *real* larger-batch acceleration will probably require:
- a fresh authority move, or
- a different lane such as a new `director` slice

This is a healthy sign. It means the existing member-owned surfaces are
actually stabilizing rather than leaving a long messy tail behind.
