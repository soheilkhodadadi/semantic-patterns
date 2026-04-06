# Current State Navigation V1

## Purpose

This is the quickest way to understand the current restructure state without
reading the full queue history.

## Start here

If you want the current picture, read these first:
- `docs/roadmap_v2/lab_end_state_architecture_review_v2.md`
- `docs/roadmap_v2/target_repo_layout_v2.md`
- `docs/roadmap_v2/fast_safe_migration_protocol_v2.md`
- `docs/roadmap_v2/history/checkpoints/restructure_progress_checkpoint_v25.md`
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
- `director`: ~98-100%
- `ai_washing` active member migration: ~85-93%
- full clean final lab structure: ~94-99%

### Labcore

Current posture:
- effectively complete for the intended low-level shared-helper scope
- legacy `src/semantic_ai_washing/labcore/*` paths are compatibility shims

### Director

Current posture:
- late-stage package migration
- most active control-plane authorities are now canonical under
  `semantic_director`
- the snapshot-adapter lane is now canonical under package-owned authorities
- the runtime-entrypoint lane is now canonical under package-owned authorities
- the remaining wrapper normalization pressure is now closed
- remaining work is now optional package polish and separate hygiene, not
  foundational seeding, runtime moves, or real package-boundary cleanup
- repo-visible package navigation is now also substantially cleaner

### AI-washing

Current posture:
- late-stage migration for active workflows
- labeling is heavily migrated
- the active preliminary classification lane is now largely canonical
- the active data lane is now largely canonical
- the remaining root-owned `ai_washing` surfaces are now mostly wrappers or
  dormant-but-relevant historical/project utilities
- repo-visible project-member navigation is now also substantially cleaner

See:
- `projects/ai_washing/root_surface_triage_registry_v2.md`
- `projects/ai_washing/migration_sheets/README.md`

## What still matters operationally

Latest queue closed cleanly:
- `docs/roadmap_v2/history/queues/batched_execution_queue_v32.md`
- `docs/roadmap_v2/history/checkpoints/restructure_progress_checkpoint_v25.md`

Operational history is still kept in the repo, but it is now secondary.
Use this index for the categories and retention logic:
- `docs/roadmap_v2/operational_history_index_v1.md`
- `docs/roadmap_v2/history/README.md`

Current archive/export stance:
- keep the history layer in repo for now
- do not open a separate export pass unless history volume becomes a real
  repo-use problem

## Recommended posture before next queue

- keep Protocol V2
- keep the hygiene queue separate from active authority moves
- use the refreshed root-surface triage registry before choosing the next queue
- do not reopen already-canonical `director` runtime-entrypoint surfaces
- do not treat visual legacy candidates as retire-ready until registry and
  inventory dependencies are cleared
- do not auto-open another tiny `director` cleanup queue; the remaining
  `director` work should be chosen as polish or hygiene on purpose
- prefer late-stage leverage over queue momentum for its own sake
- prefer intuitive navigation over adding more top-level tracker files
- treat `docs/roadmap_v2/history/` as the audit layer, not the front door
- use the repo root and workspace lane docs as the default start points
- if a root cleanup queue is opened, keep it limited to the explicit retire
  candidate identified in `docs/roadmap_v2/repo_root_clutter_review_v1.md`
