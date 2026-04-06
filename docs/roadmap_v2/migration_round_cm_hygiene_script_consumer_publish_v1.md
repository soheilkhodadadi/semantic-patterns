# Migration Round CM

## Queue

Queue V24

## Batch

`hygiene.script_consumer_registry_publish`

## Purpose

Regenerate the package-owned script inventory snapshot and rendered script
registry after the Queue V24 consumer-deprecation rule update.

## Surfaces updated

Generated snapshot:
- `director/snapshots/script_inventory.json`

Generated registry:
- `docs/director/script_registry.md`

## Expected effect

The six flat `src/data/*` shim consumers for historical data utilities should
still appear as transitional surfaces, but now with an explicit
script-consumer cleanup posture.

## Result

The published registry now renders the six flat shims with explicit consumer
language such as:
- `legacy flat shim; prefer python -m semantic_ai_washing.data.clean_compustat`

That makes the rendered control-plane posture match the intended Queue V24
outcome instead of reading like a generic compatibility lane.

## Gate

Required gate:
- regenerate inventory + registry from package-owned functions
- focused script-inventory tests
- `git diff --check`
