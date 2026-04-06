# Restructure Progress Checkpoint V21

## Purpose

This checkpoint closes Queue V28 and records what the `ai_washing`
navigation/hygiene pass changed in practice.

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Latest Queue V28 commits:
- `56edf10` `docs: consolidate ai-washing planning notes`
- `bd6aa60` `docs: polish ai-washing project front door`

## What Queue V28 proved

Queue V28 completed cleanly with:
1. `hygiene.ai_washing_planning_note_consolidation`
2. `hygiene.ai_washing_readme_frontdoor_polish`
3. `hygiene.ai_washing_navigation_posture_refresh`

This matters because Queue V28 improved the project-member front door without
reopening any settled `ai_washing` workflow migration lane.

## Direction check

### Are we still moving in the right direction?

Yes.

Why:
- the queue stayed bounded to navigation and planning-note hygiene
- it reduced repo-visible clutter at the `ai_washing` member front door
- it did not reopen a closed migration lane for momentum alone

### Are we still on a safe path?

Yes.

Why:
- Queue V28 changed no code behavior
- moved-file references were updated deliberately
- the queue stayed entirely in the hygiene/polish lane
- Atlas/private spillover stayed clean

## What Queue V28 changes in practice

Queue V28 leaves `projects/ai_washing` in a cleaner late-stage shape:

- older planning notes now live in `projects/ai_washing/planning_notes/`
- migration sheets remain in `projects/ai_washing/migration_sheets/`
- the project README is a front-door guide instead of a mixed migration note

## Current ballpark

Current estimated progress:
- `labcore`: ~95-100%
- `director`: ~98-100%
- `ai_washing` active member migration: ~85-93%
- full clean final lab structure: ~90-96%

## Recommended posture after Queue V28

Recommended posture:
- keep Protocol V2
- keep hygiene separate from active authority migration unless explicitly
  chosen
- do not reopen `ai_washing` immediately for another navigation cleanup
- choose the next queue from either:
  - a bounded hygiene follow-on with real leverage elsewhere
  - or a deliberately chosen late-stage polish class

## Bottom line

Queue V28 was worth doing.

It did not move code authority, but it made the repo tell the `ai_washing`
story more clearly at the front door. That is exactly the kind of late-stage
progress we want now.
