# Migration Round CY

## Queue

Queue V28

## Batch

`hygiene.ai_washing_readme_frontdoor_polish`

## Purpose

Turn `projects/ai_washing/README.md` into a true front-door document now that
older planning notes have moved into a dedicated subfolder.

## Gate

Required gate:
- front-door docs updated
- `git diff --check`

## Outcome

Completed cleanly.

Changes:
- replaced the older `projects/ai_washing/README.md` front door with a cleaner
  project-member guide
- pointed navigation to `planning_notes/README.md` and current queue/checkpoint
  anchors
- made the project posture explicit as late-stage wrapper/history/hygiene work

Validated with:
- manual front-door navigation review
- `git diff --check`
