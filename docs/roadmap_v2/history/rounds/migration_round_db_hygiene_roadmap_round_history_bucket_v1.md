# Migration Round DB

## Queue

Queue V29

## Batch

`hygiene.roadmap_round_history_bucket`

## Purpose

Move the `migration_round_*` artifact class into a dedicated history bucket so
the `docs/roadmap_v2/` top level no longer mixes front-door docs with per-batch
execution traces.

## Expected surfaces

Target folder:
- `docs/roadmap_v2/history/rounds/`

## Gate

Required gate:
- direct-reference scan for moved files
- `git diff --check`

## Outcome

Completed:
- created `docs/roadmap_v2/history/rounds/`
- moved all `migration_round_*` docs into the new round-history bucket
- updated direct markdown references to the new round-history paths

Validation:
- direct-reference scan found no remaining `docs/roadmap_v2/migration_round_*`
  links
- `git diff --check` passed
