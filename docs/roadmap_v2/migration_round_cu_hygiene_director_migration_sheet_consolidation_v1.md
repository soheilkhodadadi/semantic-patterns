# Migration Round CU

## Queue

Queue V27

## Batch

`hygiene.director_migration_sheet_consolidation`

## Purpose

Move the grouped migration sheets for `packages/director` into a dedicated
subfolder so the package top level reads more clearly.

## Expected surfaces

Target folder:
- `packages/director/migration_sheets/`

Affected front-door doc:
- `packages/director/README.md`

## Gate

Required gate:
- direct-reference scan for moved files
- `git diff --check`

## Outcome

Completed cleanly.

Changes:
- moved grouped migration sheets from `packages/director/` into
  `packages/director/migration_sheets/`
- added `packages/director/migration_sheets/README.md`
- updated `packages/director/README.md` references to the new paths

Validated with:
- direct-reference scan for old top-level grouped-sheet paths
- `git diff --check`
