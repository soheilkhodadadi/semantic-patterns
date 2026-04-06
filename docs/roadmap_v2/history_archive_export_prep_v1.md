# Roadmap History Archive Export Prep V1

## Purpose

Define the intended long-term retention and export posture for
`docs/roadmap_v2/history/` now that the history layer has been bucketed and the
late-stage restructure is nearly complete.

## Current state

The history layer now contains four stable buckets:
- `history/queues/`
- `history/comparisons/`
- `history/rounds/`
- `history/checkpoints/`

It remains useful in-repo because it still provides:
- auditability for past authority and hygiene moves
- rationale for why specific queue winners were chosen
- checkpointed progress estimates across the restructure

## Retention classes

### Keep in repo by default

These should remain in the repo unless a later explicit archive/export pass says
otherwise:
- latest checkpoints
- latest queue records for the final queues
- latest comparison records that explain the final late-stage choices
- durable posture notes that still affect navigation or cleanup decisions

### History that is archive-export eligible later

These are still useful now, but could later move to an exported archive bundle
without harming day-to-day navigation:
- older queue records from early and middle restructure phases
- older authority comparisons whose decision context is no longer active
- older migration-round traces whose only purpose is historical audit

### Not a current export target

These should stay in-place for now:
- `docs/roadmap_v2/README.md`
- `docs/roadmap_v2/current_state_navigation_v1.md`
- `docs/roadmap_v2/operational_history_index_v1.md`
- `docs/roadmap_v2/history/README.md`
- the latest restructure checkpoints

## What a later export pass should do

A later bounded export pass should:
- preserve filenames and ordering
- export archive-eligible history to a clearly named archive bundle or lane
- keep the current front-door docs pointing to the retained in-repo history
- avoid rewriting historical content except for index pointers

A later export pass should not:
- re-bucket files again
- mix with code migration or cleanup
- remove the latest checkpoints and final navigation anchors from the repo

## Recommendation

No immediate export move is needed.

The right posture now is:
- keep the history layer in-repo
- treat it as a stable audit archive
- only open a later export queue if history volume becomes an active repo-use
  problem rather than a theoretical one
