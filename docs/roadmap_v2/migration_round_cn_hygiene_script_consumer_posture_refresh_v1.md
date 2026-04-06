# Migration Round CN

## Queue

Queue V24

## Batch

`hygiene.script_consumer_posture_refresh`

## Purpose

Make the Queue V24 consumer-side cleanup outcome explicit in a human-readable
note so the registry update does not remain only a generated artifact change.

## Surfaces updated

Primary note:
- `docs/roadmap_v2/script_consumer_posture_refresh_v1.md`

## Result

The six flat `src/data/*` scripts are now explicitly treated as legacy consumer
shims for already-downgraded historical data utilities, not as front-door
workflow scripts.

## Gate

Required gate:
- posture note updated
- `git diff --check`
