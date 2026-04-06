# Restructure Progress Checkpoint V8

## Purpose

This checkpoint closes Queue V15 and tests whether the triage-registry-driven `ai_washing` queue pattern is still producing coherent workflow moves instead of scattered file churn.

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Latest Queue V15 commits:
- `05e2793` `refactor: seed ai-washing binary training authority`
- `76c354a` `refactor: seed ai-washing logreg training authority`
- `a93d5dd` `refactor: seed ai-washing benchmark matrix authority`

## What Queue V15 proved

Queue V15 completed cleanly with:
1. `ai_washing_member.classification.train_binary_relevance_then_as`
2. `ai_washing_member.classification.train_logreg_preliminary`
3. `ai_washing_member.classification.benchmark_preliminary_models`

This matters because Queue V15 moved an upstream model-selection lane rather than a set of isolated helpers.

## Direction check

### Are we still moving in the right direction?

Yes.

Why:
- the queue moved one coherent wave-1 model-selection chain from training through benchmark matrix generation
- the root-surface triage registry kept the queue on active preliminary classification work instead of reopening dormant classifier-training utilities
- the member-owned `ai_washing` lane now owns a larger share of the current benchmark-selection workflow, not just baseline support surfaces

### Are we still on a safe path?

Yes.

Why:
- Queue V15 kept one bounded authority per commit
- the root compatibility layer remained intact while the direct benchmarking bundle moved to the member path
- the queue reused one strong shared gate in `tests/test_preliminary_benchmarking.py`
- the hygiene queue remained isolated
- Atlas/private spillover stayed clean

## What Queue V15 changes in practice

Queue V15 strengthens the `ai_washing` member in a meaningful way.

The member now owns the wave-1 model-selection path for:
- binary two-stage training
- multinomial logreg training
- benchmark matrix generation

That makes the remaining active classification surfaces narrower and more downstream than they were before Queue V15.

## Recommended posture after Queue V15

Recommended posture:
- keep Protocol V2
- keep the hygiene queue separate
- keep using the root-surface triage registry before opening the next `ai_washing` queue
- compare the remaining downstream preliminary reporting surfaces against one clean data-lane opener before Queue V16

## Bottom line

Queue V15 confirms that the restructure is still moving in the right direction and that the triage-registry-driven queue pattern remains useful after the consolidation pass.

The migration is more grounded than it was before Queue V15.
No strategic repositioning is needed right now.
