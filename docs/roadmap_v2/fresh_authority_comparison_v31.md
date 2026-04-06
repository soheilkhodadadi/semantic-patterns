# Fresh Authority Comparison V31

## Purpose

Choose Queue V28 after Queue V27 completed cleanly.

## Candidates compared

1. `hygiene.ai_washing_planning_note_consolidation`
2. `hygiene.roadmap_history_bucketing`

## Candidate A: `hygiene.ai_washing_planning_note_consolidation`

Representative surfaces:
- `projects/ai_washing/planning_notes/member_seed_plan_v1.md`
- `projects/ai_washing/planning_notes/member_shell_readiness_v1.md`
- `projects/ai_washing/planning_notes/first_code_seed_decision_v1.md`
- `projects/ai_washing/planning_notes/labeling_common_impact_map_v1.md`
- `projects/ai_washing/planning_notes/root_surface_triage_registry_v1.md`

Why it is attractive:
- `projects/ai_washing/` still has a small but visible cluster of older
  planning/reference notes at the top level
- the current front door only really needs:
  - `README.md`
  - `root_surface_triage_registry_v2.md`
  - `migration_sheets/`
- this is a low-risk cleanup with clear navigation benefit

Risk shape:
- low
- mostly file moves plus reference updates
- direct references are limited and easy to update

## Candidate B: `hygiene.roadmap_history_bucketing`

Representative surfaces:
- top-level queue docs under `docs/roadmap_v2/`
- fresh-authority comparisons
- migration rounds

Why it is attractive:
- `docs/roadmap_v2/` still has a very large flat history footprint
- bucketing that history would eventually improve long-term navigation

Risk shape:
- medium
- there are many more files and many more historical references
- this is better as a later, deliberate documentation-archive queue

## Decision

Chosen Queue V28 opener:
- `hygiene.ai_washing_planning_note_consolidation`

## Why this wins now

It is the smaller, cleaner, higher-leverage hygiene move.

Like Queue V27 for `packages/director`, this queue improves a project-member
front door without reopening any settled migration lane or attempting a
repo-wide history re-bucketing pass too early.
