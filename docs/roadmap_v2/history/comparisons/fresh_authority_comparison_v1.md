# Fresh Authority Comparison V1

## Purpose

This note compares the next fresh authority candidates after the already-owned
`ai_washing` member surfaces started to stabilize under Protocol V2.

## Candidates reviewed

### Candidate A: `build_filing_manifest`

Pros:
- already adjacent to the member-owned data lane
- direct relationship with the sentence-table workflow
- two known direct consumers

Cons:
- depends on `semantic_ai_washing.labeling.ff12_mapping`, which is still
  root-owned
- lower direct caller pressure than other candidates
- weaker immediate regression story for a fresh-authority acceleration round

### Candidate B: `benchmark_utils`

Pros:
- self-contained helper surface
- already depends only on member-owned or neutral dependencies
- two direct production callers:
  - `benchmark_preliminary_models.py`
  - `evaluate_preliminary_heldout.py`
- strong shared regression story through preliminary benchmarking and phase-3
  tests

Cons:
- narrower than a full classification authority move
- still requires a fresh grouped migration sheet and member-local tests

## Decision

Chosen next fresh authority:
- `benchmark_utils`

## Why this choice is better now

`benchmark_utils` is the cleaner fresh-authority seed because it gives us:
- lower cross-authority drag
- a stronger immediate shared gate
- two real caller families we can migrate in the same round

`build_filing_manifest` remains viable later, but it is a weaker next
acceleration candidate until its surrounding authority surface is broader or
its root-owned dependencies shrink.
