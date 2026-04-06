# Restructure Progress Checkpoint V25

## Purpose

This checkpoint closes Queue V32 and records what the narrow repo-root cleanup
changed in practice.

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Latest Queue V32 commits:
- `1b8573e` `docs: retire legacy root requirements export`
- `e220a7e` `docs: refresh root cleanup posture`

## What Queue V32 proved

Queue V32 completed cleanly with:
1. `hygiene.root_old_requirements_cleanup`
2. `hygiene.root_cleanup_posture_refresh`
3. `hygiene.root_cleanup_checkpoint`

This matters because Queue V32 showed that we can still do a real late-stage
cleanup without drifting, as long as the scope is explicit and tiny.

## Direction check

### Are we still moving in the right direction?

Yes.

Why:
- the queue executed exactly the retire candidate surfaced by Queue V31
- it did not invent a broader cleanup wave
- it left the repo root slightly cleaner without destabilizing anything else

### Are we still on a safe path?

Yes.

Why:
- Queue V32 changed no code behavior
- the cleanup was scan-backed and reference-checked
- no packaging, environment, or local-noise side edits were mixed in
- Atlas/private spillover stayed clean

## What Queue V32 changes in practice

Queue V32 leaves the repo in a cleaner late-stage shape:
- `old_requirements.txt` is gone
- the root-clutter review now reflects the retired state accurately
- the remaining root-visible surfaces are either active repo-contract files or
  local-only ignored noise

## Current ballpark

Current estimated progress:
- `labcore`: ~95-100%
- `director`: ~98-100%
- `ai_washing` active member migration: ~85-93%
- full clean final lab structure: ~94-99%

## Recommended posture after Queue V32

Recommended posture:
- keep Protocol V2
- prefer only high-leverage late-stage hygiene or final polish from here
- avoid reopening broad cleanup classes without a fresh comparison
- treat the remaining root-visible noise mostly as local-only, not repo-wide
  migration debt

## Bottom line

Queue V32 was worth doing.

It was small, but it was real: one tracked stale root artifact is gone, and the
late-stage cleanup story is now more consistent and easier to trust.
