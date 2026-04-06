# Fresh Authority Comparison V7

## Purpose

Choose the first authority for Queue V4 by comparing one clean `director`
candidate and one clean `ai_washing` candidate after Queue V3 closed.

## Candidates

### Candidate A

Authority:
- `semantic_director.decision`

Why it is attractive:
- meaningful `director` leverage in `cli` and `executor`
- compact enough to package without opening Atlas-adjacent surfaces
- good fit for a later downstream `executor` round

Risks:
- would keep the first move of the new cycle in `director` again
- depends on root-side runtime helpers that are stable, but not yet fully
  packaged at the `director` layer

### Candidate B

Authority:
- `ai_washing_member.labeling.sample_heldout_v2_candidates`

Why it is attractive:
- stays in the flagship project lane
- already depends on member-owned `classification` and `labeling` surfaces
- has a natural direct caller in the restartable wrapper
- has strong workflow tests in `tests/test_heldout_v2_workflow.py` and
  `tests/test_restartable_jobs.py`
- opens a clean follow-on authority for `freeze_heldout_v2`

Risks:
- held-out workflow touches larger data-shaped fixtures in tests
- batch validation needs both workflow and restartable coverage

## Decision

Choose:
- `ai_washing_member.labeling.sample_heldout_v2_candidates`

Why it wins now:
- better lane balance after the recent `director` streak
- cleaner use of already-member-owned imports
- stronger immediate workflow leverage than another `director` helper-first move
- sets up a coherent Queue V4 with one held-out workflow lane before rotating
  back to `director`

Do not choose first:
- `semantic_director.decision`

## Queue V4 Guidance

The next three-round cycle should be:

1. `ai_washing_member.labeling.sample_heldout_v2_candidates`
2. `ai_washing_member.labeling.freeze_heldout_v2`
3. `semantic_director.decision`

If Batch 1 gets messy at pre-scan or gate time:
- rotate immediately to `semantic_director.decision`
