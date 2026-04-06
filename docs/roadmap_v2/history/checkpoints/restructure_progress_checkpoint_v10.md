# Restructure Progress Checkpoint V10

## Purpose

This checkpoint closes Queue V17 and tests whether the queue pattern can move a
coherent active data lane cleanly after the preliminary-classification lane was
closed.

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Latest Queue V17 commits:
- `65aa13c` `refactor: seed ai-washing sentence-pool expansion authority`
- `fee71bb` `refactor: seed ai-washing sentence-pool combine authority`
- `f2e85aa` `refactor: seed ai-washing segmentation benchmark authority`

## What Queue V17 proved

Queue V17 completed cleanly with:
1. `ai_washing_member.data.build_expanded_sentence_pool`
2. `ai_washing_member.data.combine_expanded_sentence_pool_batches`
3. `ai_washing_member.data.benchmark_segmentation_modes`

This matters because Queue V17 did not just move another isolated helper. It
opened and closed a coherent sentence-pool data lane:
- expansion
- cumulative combination
- bounded segmentation QA

## Direction check

### Are we still moving in the right direction?

Yes.

Why:
- the queue followed the triage registry instead of opening a random new data surface
- the member-owned `ai_washing` lane now owns the active sentence-pool expansion workflow
- the remaining active data pressure is now clearer and smaller: active-window materialization and backfill

### Are we still on a safe path?

Yes.

Why:
- Queue V17 kept one bounded authority per commit
- the root compatibility layer remained intact
- the queue kept the hygiene queue isolated
- Atlas/private spillover stayed clean

## What Queue V17 changes in practice

Queue V17 shifts the active `ai_washing` migration center of gravity further
into the data lane.

The next queue decision is now simpler:
- continue with `materialize_active_window_sentences` / backfill follow-ons
- do not reopen already-closed sentence-pool surfaces

## Recommended posture after Queue V17

Recommended posture:
- keep Protocol V2
- keep the hygiene queue separate
- use the root-surface triage registry to open the next queue from the remaining active data candidates
- compare `materialize_active_window_sentences` against `run_historical_backfill` as the Queue V18 opener

## Bottom line

Queue V17 confirms that the restructure is still moving in the right direction
and that the queue pattern can migrate a meaningful active data workflow lane
without widening into cleanup or unrelated authority moves.

No strategic repositioning is needed right now.
