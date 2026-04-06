# Fresh Authority Comparison V6

## Purpose

Reset the queue after the first four-batch cycle completed cleanly.

This comparison chooses the first authority for Queue V3 by comparing one
strong `director` candidate and one strong `ai_washing` candidate.

## Candidates

### Candidate A

- authority: `semantic_director.branching`
- lane: `director`

Why it is attractive:

- clean package boundary
- direct production leverage in `cli` and `review`
- naturally downstream of already-canonical `roadmap_model`, `render`, and
  `readiness`
- low dependency complexity

Current direct caller pressure:

- `src/semantic_ai_washing/director/cli.py`
- `src/semantic_ai_washing/director/core/review.py`

Likely direct validation edge:

- `tests/test_director_cli.py`
- `tests/test_director_review.py`

### Candidate B

- authority: `ai_washing_member.labeling.build_labeling_batch`
- lane: `ai_washing`

Why it is attractive:

- meaningful project-member surface
- good fit for the flagship lane
- already aligned with member-owned `labeling.common`

Current direct caller pressure:

- mostly direct test pressure
- roadmap/review references in string commands, not strong runtime imports

Likely direct validation edge:

- `tests/test_labeling_batch.py`
- `tests/test_iteration2_parallel.py`

## Comparison

### Boundary Cleanliness

`semantic_director.branching` is cleaner.

Reasons:

- depends mainly on `semantic_director.schemas` plus standard library helpers
- caller surface is explicit and compact
- no new project-member lane boundary is needed

`build_labeling_batch` is still reasonable, but it has weaker live caller
pressure and a more test-heavy validation story.

### Immediate Leverage

`semantic_director.branching` wins.

Reasons:

- real runtime callers, not only tests
- high-value control-plane surface
- improves package coherence in a lane that is already converting well

### Safety

`semantic_director.branching` wins.

Reasons:

- bounded blast radius
- easy compatibility strategy
- clear package test plus two root regression anchors

## Decision

Choose:

- `semantic_director.branching`

Do not choose first:

- `ai_washing_member.labeling.build_labeling_batch`

## Queue V3 Guidance

The next three-round cycle should be:

1. `semantic_director.branching`
2. `semantic_director.state`
3. `ai_washing_member.labeling.build_labeling_batch`

Why this order:

- Batch 1 uses the cleanest fresh authority now available
- Batch 2 stays in the stronger lane for one follow-on authority
- Batch 3 rotates back into `ai_washing`

## Deferred Surface

`semantic_director.snapshot` remains promising, but it is deferred from the
immediate queue because it touches the Atlas adapter surface. That is not a
blocker, but it deserves a more deliberate pre-scan than `branching` or
`state`.

## Atlas / Private Spillover Check

No Atlas- or NDA-derived code or structure was used in this comparison note.
