# Current State Navigation V1

## Purpose

This is the quickest way to understand the current restructure state without
reading the full queue history.

## Start here

If you want the current picture, read these first:
- `docs/roadmap_v2/lab_end_state_architecture_review_v2.md`
- `docs/roadmap_v2/target_repo_layout_v2.md`
- `docs/roadmap_v2/fast_safe_migration_protocol_v2.md`
- `docs/roadmap_v2/restructure_progress_checkpoint_v6.md`
- `docs/roadmap_v2/legacy_template_hygiene_queue_v1.md`

## Canonical code layers

Shared low-level package:
- `packages/labcore/README.md`
- canonical code under `packages/labcore/src/semantic_labcore/`

Shared control-plane package:
- `packages/director/README.md`
- canonical code under `packages/director/src/semantic_director/`

Project member:
- `projects/ai_washing/README.md`
- canonical member-owned code under `projects/ai_washing/src/ai_washing_member/`

## Current migration position

Ballpark progress:
- `labcore`: ~95-100%
- `director`: ~90-95%
- `ai_washing` active member migration: ~60-70%
- full clean final lab structure: ~60-65%

### Labcore

Current posture:
- effectively complete for the intended low-level shared-helper scope
- legacy `src/semantic_ai_washing/labcore/*` paths are compatibility shims

### Director

Current posture:
- late-stage package migration
- most active control-plane authorities are now canonical under
  `semantic_director`
- remaining work is smaller follow-on selection, not foundational seeding

### AI-washing

Current posture:
- mid-to-late member migration
- labeling is heavily migrated
- classification and data still contain the largest remaining root-owned
  surfaces
- the next decision pressure is not just more queues; it is root-surface triage
  plus clearer navigation

See:
- `projects/ai_washing/root_surface_triage_registry_v1.md`
- `projects/ai_washing/migration_sheets/README.md`

## What still matters operationally

Latest queue closed cleanly:
- `docs/roadmap_v2/batched_execution_queue_v13.md`
- `docs/roadmap_v2/restructure_progress_checkpoint_v6.md`

Operational history is still kept in the repo, but it is now secondary.
Use this index for the categories and retention logic:
- `docs/roadmap_v2/operational_history_index_v1.md`

## Recommended posture before Queue V14

- keep Protocol V2
- keep the hygiene queue separate from active authority moves
- use the root-surface triage registry before choosing the next fresh authority
- prefer intuitive navigation over adding more top-level tracker files
