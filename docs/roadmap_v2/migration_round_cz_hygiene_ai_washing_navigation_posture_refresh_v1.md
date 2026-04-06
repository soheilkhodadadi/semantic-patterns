# Migration Round CZ

## Queue

Queue V28

## Batch

`hygiene.ai_washing_navigation_posture_refresh`

## Purpose

Close Queue V28 with an explicit note about how `projects/ai_washing` should be
navigated now that the planning notes are consolidated and the project README
has been simplified.

## Outcome

Completed cleanly.

Queue V28 ends with:
- `projects/ai_washing/` cleaned at the top level
- `projects/ai_washing/planning_notes/` as the early-stage note folder
- `projects/ai_washing/migration_sheets/` as the operational-history folder
- `projects/ai_washing/README.md` as a cleaner project-member guide

## Gate

Required gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`
