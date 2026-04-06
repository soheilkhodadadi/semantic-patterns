# Restructure Progress Checkpoint V4

## Purpose

This checkpoint closes Queue V11 and tests whether the current migration style can safely move an entire active project workflow family, not just isolated authorities.

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Latest Queue V11 commits:
- `3931c54` `refactor: seed ai-washing sample-builder authority`
- `350de5f` `refactor: seed ai-washing dedupe authority`
- `38940c6` `refactor: seed ai-washing qa authority`

## What Queue V11 proved

Queue V11 completed cleanly with:
1. `ai_washing_member.labeling.build_labeling_sample`
2. `ai_washing_member.labeling.dedupe_labeled_sentences`
3. `ai_washing_member.labeling.qa_labeled_dataset`

This matters because it is the first queue that moved an end-to-end current-stage `ai_washing` dataset workflow family into the member-owned lane.

## Direction check

### Are we still moving in the right direction?

Yes.

Why:
- the member-owned `ai_washing` lane is now handling larger coherent workflows, not just utility slices
- the root compatibility layer is still intact, so the migration remains non-destructive
- the workflow-level gate stayed stable across all three batches

### Are we still on a safe path?

Yes.

Why:
- Queue V11 reused one shared regression bundle across all three rounds
- each round still had its own bounded authority and commit
- the hygiene queue remained isolated
- Atlas/private spillover remained clean

## What Queue V11 changes in practice

The migration now has evidence for two safe patterns:
- mixed-lane queues with a director rotation, like Queue V10
- single-workflow queues inside one active project lane, like Queue V11

That means we can choose between them intentionally instead of assuming every queue must look the same.

## Recommended posture after Queue V11

Recommended posture:
- keep Protocol V2
- keep the hygiene queue separate
- allow single-workflow queues when one active project workflow has a strong shared gate
- continue using a short checkpoint after each completed queue

## Bottom line

Queue V11 confirms that the restructure can move faster without getting sloppier when the queue is built around a real active workflow family.

That is a meaningful upgrade in confidence for the next cycle.
