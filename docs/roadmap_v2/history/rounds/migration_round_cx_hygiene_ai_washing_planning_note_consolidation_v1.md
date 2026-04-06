# Migration Round CX

## Queue

Queue V28

## Batch

`hygiene.ai_washing_planning_note_consolidation`

## Purpose

Move older planning/reference notes for `projects/ai_washing` into a dedicated
subfolder so the project-member top level reads more clearly.

## Expected surfaces

Target folder:
- `projects/ai_washing/planning_notes/`

Affected front-door doc:
- `projects/ai_washing/README.md`

## Gate

Required gate:
- direct-reference scan for moved files
- `git diff --check`

## Outcome

Completed cleanly.

Changes:
- moved older planning/reference notes from `projects/ai_washing/` into
  `projects/ai_washing/planning_notes/`
- added `projects/ai_washing/planning_notes/README.md`
- updated direct references to the moved files

Validated with:
- direct-reference scan for old top-level planning-note paths
- `git diff --check`
