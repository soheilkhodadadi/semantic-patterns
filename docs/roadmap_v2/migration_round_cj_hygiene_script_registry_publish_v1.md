# Migration Round CJ

## Queue

Queue V23

## Batch

`hygiene.script_registry_publish`

## Purpose

Regenerate the package-owned script inventory snapshot and the rendered script
registry after the Queue V23 deprecation-rule update.

## Surfaces updated

Generated snapshot:
- `director/snapshots/script_inventory.json`

Generated registry:
- `docs/director/script_registry.md`

## Expected effect

The six historical data utilities reviewed in Queue V22 should no longer appear
as current canonical front-door entrypoints. They should be rendered as
transitional script-deprecation surfaces instead.

## Gate

Required gate:
- rerun the package-owned script inventory task
- focused script-inventory tests
- `git diff --check`
