# Operational History Index V1

## Purpose

This index explains what the restructure tracking files are for and how to use
them without treating every file as a front-door document.

## Artifact classes

### Queue docs

Pattern:
- `docs/roadmap_v2/history/queues/batched_execution_queue_v*.md`

Role:
- record the planned three-batch queue for a given cycle
- show queue order and queue completion state

Use when:
- you want to see how a specific queue was structured
- you need the per-queue execution order

### Fresh-authority comparisons

Pattern:
- `docs/roadmap_v2/history/comparisons/fresh_authority_comparison_v*.md`

Role:
- explain why one authority was chosen over another before a queue opened

Use when:
- you want the rationale behind the chosen queue opener

### Migration rounds

Pattern:
- `docs/roadmap_v2/history/rounds/migration_round_*.md`

Role:
- per-batch execution trace
- records the moved authority, caller updates, and validation gate

Use when:
- you need an audit trail for one specific authority move

### Progress checkpoints

Pattern:
- `docs/roadmap_v2/history/checkpoints/restructure_progress_checkpoint_v*.md`

Role:
- summarize the queue-level result
- test whether the restructure is still moving safely in the right direction

Use when:
- you want the current migration posture without reading every batch trace

## Retention posture

These operational docs are still useful, but they are history artifacts, not
front-door navigation.

For day-to-day navigation, prefer:
- `docs/roadmap_v2/current_state_navigation_v1.md`
- `projects/ai_washing/README.md`
- `projects/ai_washing/migration_sheets/README.md`
- `projects/ai_washing/root_surface_triage_registry_v2.md`

## Current state

Latest completed queue:
- `docs/roadmap_v2/history/queues/batched_execution_queue_v29.md`

Latest queue checkpoint:
- `docs/roadmap_v2/history/checkpoints/restructure_progress_checkpoint_v22.md`

Latest protocol anchor:
- `docs/roadmap_v2/fast_safe_migration_protocol_v2.md`

## Future cleanup

These history files are now bucketed formally under `docs/roadmap_v2/history/`.
Any later archive/export pass should still happen as its own bounded
documentation-hygiene class rather than being mixed into active authority
migrations.
