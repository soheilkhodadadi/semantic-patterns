# Restructure Progress Checkpoint V6

## Purpose

This checkpoint closes Queue V13 and tests whether the restructure can keep rotating back into `ai_washing` without losing the safe pace established in Queue V12.

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Latest Queue V13 commits:
- `e7a5557` `refactor: seed ai-washing assistive prelabel authority`
- `8521fae` `refactor: seed ai-washing benchmark variants authority`
- `08faa0e` `refactor: seed ai-washing prelabel scoring authority`

## What Queue V13 proved

Queue V13 completed cleanly with:
1. `ai_washing_member.labeling.assistive_prelabel_batch`
2. `ai_washing_member.labeling.benchmark_prompt_variants`
3. `ai_washing_member.labeling.score_prelabel_sheet`

This matters because it moved a full assistive calibration workflow into the member-owned `ai_washing` lane while preserving the truthfulness of the old root integration tests.

## Direction check

### Are we still moving in the right direction?

Yes.

Why:
- the member-owned `ai_washing` lane is now carrying another coherent current-stage workflow family, not just isolated helper slices
- the migration is still focused on active project surfaces rather than dead/template carry-forward
- the root compatibility layer remains intact, so the queue stayed non-destructive while new authority moved into the member-owned lane

### Are we still on a safe path?

Yes.

Why:
- Queue V13 kept one bounded authority per commit
- each batch reused the same shared calibration regression bundle in a focused way
- the root shims kept monkeypatch-sensitive tests truthful instead of forcing premature test rewrites
- the hygiene queue remained isolated
- Atlas/private spillover stayed clean

## What Queue V13 changes in practice

Queue V13 strengthens the already-proven single-workflow queue pattern inside an active project lane.

That means we now have strong evidence for:
- mixed-lane queues with deliberate rotation
- compact control-plane chains inside `director`
- full workflow-family queues inside `ai_washing`

## Recommended posture after Queue V13

Recommended posture:
- keep Protocol V2
- keep the hygiene queue separate
- keep alternating queue shape deliberately based on the cleanest next active workflow or control-plane chain
- keep one short checkpoint after each fully completed queue

## Bottom line

Queue V13 confirms that we are still moving quickly in the right direction and that the current safety spine is holding across different queue shapes.

No repositioning is needed right now.
