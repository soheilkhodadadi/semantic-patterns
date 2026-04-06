# Migration Round CW

## Queue

Queue V27

## Batch

`hygiene.director_navigation_posture_refresh`

## Purpose

Close Queue V27 with an explicit note about how `packages/director` should be
navigated now that the migration sheets are consolidated and the package README
has been simplified.

## Outcome

Completed cleanly.

Queue V27 ends with:
- `packages/director/` cleaned at the top level
- `packages/director/migration_sheets/` as the operational-history folder
- `packages/director/README.md` as a front-door package guide

## Gate

Required gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`
