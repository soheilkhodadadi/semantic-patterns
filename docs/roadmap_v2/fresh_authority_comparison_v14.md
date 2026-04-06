# Fresh Authority Comparison V14

## Purpose

Choose the Queue V11 opener after Queue V10 completed cleanly.

## Candidates compared

1. `ai_washing_member.labeling.build_labeling_sample`
2. `semantic_director.review`

## Candidate A: `ai_washing_member.labeling.build_labeling_sample`

Why it is attractive:
- it opens a coherent Phase 1 dataset-prep workflow that is still relevant to the project
- direct caller pressure is concentrated in `tests/test_labeling_phase1.py`
- it naturally opens `dedupe_labeled_sentences` and `qa_labeled_dataset` as adjacent follow-on rounds
- it keeps Queue V11 inside one active `ai_washing` workflow family

Risk shape:
- low
- one active project workflow
- one focused regression bundle

## Candidate B: `semantic_director.review`

Why it is attractive:
- it is a meaningful `director` control-plane surface
- direct CLI/test leverage exists
- it would continue the package boundary build-out after `planner`

Risk shape:
- medium-high
- broader dependency surface than the labeling workflow opener
- better taken after the current dataset-prep workflow family is member-owned end to end

## Decision

Chosen Queue V11 opener:
- `ai_washing_member.labeling.build_labeling_sample`

## Why this wins now

It is the cleaner opener and lets Queue V11 take a fully coherent shape:

1. `build_labeling_sample`
2. `dedupe_labeled_sentences`
3. `qa_labeled_dataset`

That keeps the queue inside one active flagship workflow, with one shared root regression bundle and no need to reopen the hygiene question.
