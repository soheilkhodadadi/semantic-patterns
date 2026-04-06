# Roadmap History Navigation Posture Refresh V1

## Purpose

This note closes Queue V29 and records the intended navigation posture for
`docs/roadmap_v2/` after the history-bucketing pass.

## New default posture

Use these as the front door:
- `docs/roadmap_v2/README.md`
- `docs/roadmap_v2/current_state_navigation_v1.md`
- `docs/roadmap_v2/operational_history_index_v1.md`

Use `docs/roadmap_v2/history/` for audit and traceability:
- `history/queues/`
- `history/comparisons/`
- `history/rounds/`
- `history/checkpoints/`

## Why this is better

- top-level roadmap docs now read as navigation and posture, not as a flat log
- operational history is still preserved, but it no longer competes with the
  front door
- the restructure story is easier to follow for new contributors

## What did not change

- no historical content was deleted
- no code behavior changed
- the migration audit trail remains available in-repo

## Recommended posture after Queue V29

- keep using the front-door docs first
- treat `history/` as the audit layer, not the starting point
- continue choosing only bounded late-stage queues with clear leverage
