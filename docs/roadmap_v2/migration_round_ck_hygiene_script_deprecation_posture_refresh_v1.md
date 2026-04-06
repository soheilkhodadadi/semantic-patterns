# Migration Round CK

## Queue

Queue V23

## Batch

`hygiene.script_deprecation_posture_refresh`

## Purpose

Make the Queue V23 script-deprecation outcome explicit in human-readable
project posture docs so the registry changes do not look like isolated metadata
edits.

## Surfaces updated

Primary note:
- `docs/roadmap_v2/script_deprecation_posture_refresh_v1.md`

Project triage:
- `projects/ai_washing/root_surface_triage_registry_v2.md`

## Result

The six historical data utilities remain in the repo, but they are now clearly
tracked as script-deprecation candidates rather than current canonical
front-door workflow surfaces.

## Gate

Required gate:
- posture note updated
- triage registry updated
- `git diff --check`
