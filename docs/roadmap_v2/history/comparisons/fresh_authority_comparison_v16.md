# Fresh Authority Comparison V16

## Purpose

Choose the Queue V13 opener after Queue V12 completed cleanly.

## Candidates compared

1. `ai_washing_member.labeling.assistive_prelabel_batch`
2. `ai_washing_member.labeling.sample_heldout_v2_restartable`

## Candidate A: `ai_washing_member.labeling.assistive_prelabel_batch`

Why it is attractive:
- it opens the active assistive calibration workflow that is still relevant to the project
- Queue V12 already made the shared `api_assistive` and `director` dependencies cleaner, which lowers the boundary risk now
- it naturally opens `benchmark_prompt_variants` and `score_prelabel_sheet` as adjacent follow-on rounds
- the root compatibility shim can preserve the existing monkeypatch-based integration tests by forwarding patched hook symbols into the member-owned module

Risk shape:
- medium
- one active `ai_washing` workflow lane
- one strong shared regression bundle already exists in `tests/test_iteration2_parallel.py`

## Candidate B: `ai_washing_member.labeling.sample_heldout_v2_restartable`

Why it is attractive:
- it is still active and tied to the held-out workflow
- direct restartable-job coverage exists
- it would keep the queue inside `ai_washing`

Risk shape:
- medium-high
- weaker immediate leverage than the assistive calibration workflow
- does not open as clean a three-batch workflow family as the assistive lane

## Decision

Chosen Queue V13 opener:
- `ai_washing_member.labeling.assistive_prelabel_batch`

## Why this wins now

It is the stronger opener because it lets Queue V13 take a coherent current-stage shape:

1. `assistive_prelabel_batch`
2. `benchmark_prompt_variants`
3. `score_prelabel_sheet`

That keeps the queue inside one active calibration workflow with one shared root regression bundle, while still keeping the hygiene queue separate.
