# Migration Round DA

## Queue

Queue V29

## Batch

`hygiene.roadmap_history_bucket_seed`

## Purpose

Create dedicated history buckets under `docs/roadmap_v2/` and move the queue,
comparison, and checkpoint artifact classes out of the top level.

## Expected surfaces

Target folders:
- `docs/roadmap_v2/history/queues/`
- `docs/roadmap_v2/history/comparisons/`
- `docs/roadmap_v2/history/checkpoints/`

Supporting doc:
- `docs/roadmap_v2/history/README.md`

## Gate

Required gate:
- direct-reference scan for moved files
- `git diff --check`

## Outcome

Completed cleanly.

Changes:
- created `docs/roadmap_v2/history/`
- moved queue docs into `history/queues/`
- moved fresh-authority comparisons into `history/comparisons/`
- moved progress checkpoints into `history/checkpoints/`
- added `docs/roadmap_v2/history/README.md`
- updated direct references to those three history classes

Validated with:
- direct-reference scan for old top-level queue/comparison/checkpoint paths
- `git diff --check`
