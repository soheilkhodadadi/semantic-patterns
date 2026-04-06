# Fresh Authority Comparison V30

## Purpose

Choose Queue V27 after Queue V26 completed cleanly.

## Candidates compared

1. `hygiene.director_migration_sheet_consolidation`
2. `semantic_director.export_surface_polish`

## Candidate A: `hygiene.director_migration_sheet_consolidation`

Representative surfaces:
- top-level grouped migration sheets in `packages/director/`
- `packages/director/README.md`

Why it is attractive:
- `packages/director/` still has a noisy top-level migration-sheet footprint
- this is the same front-door clutter pattern we already cleaned up
  successfully in `projects/ai_washing`
- the cleanup would make the package easier to scan without reopening code
  migration pressure

Risk shape:
- low
- mostly file moves and navigation cleanup
- safe if direct references are updated and the change stays explicitly in the
  hygiene lane

## Candidate B: `semantic_director.export_surface_polish`

Representative surfaces:
- `packages/director/src/semantic_director/__init__.py`
- `packages/director/tests/test_exports.py`

Why it is attractive:
- Queue V26 made the package boundary cleaner
- a follow-on could make the package front door expose more of the current
  canonical surface explicitly

Risk shape:
- low to medium
- this is polish, not boundary cleanup
- it is only worth doing if we deliberately want a broader package export
  surface, not just more movement

## Decision

Chosen Queue V27 opener:
- `hygiene.director_migration_sheet_consolidation`

## Why this wins now

The hygiene lane has stronger current leverage than export polish.

`semantic_director` is already in a strong late-stage package state after Queue
V26. By contrast, `packages/director/` still presents migration operational
artifacts as top-level clutter. Consolidating those sheets into a dedicated
folder improves the end-state story more than broadening exports right now.
