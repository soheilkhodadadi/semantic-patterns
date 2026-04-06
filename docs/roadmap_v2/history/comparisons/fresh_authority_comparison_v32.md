# Fresh Authority Comparison V32

## Purpose

Choose Queue V29 after Queue V28 completed cleanly.

## Candidates compared

1. `hygiene.roadmap_history_bucketing`
2. `hygiene.repo_root_navigation_polish`

## Candidate A: `hygiene.roadmap_history_bucketing`

Representative surfaces:
- queue docs in `docs/roadmap_v2/`
- fresh-authority comparisons in `docs/roadmap_v2/`
- migration rounds in `docs/roadmap_v2/`
- progress checkpoints in `docs/roadmap_v2/`

Why it is attractive:
- `docs/roadmap_v2/` still has a very large flat history footprint
- the artifact classes are already defined in the operational history index
- bucketing them now would improve navigation without reopening code migration

Risk shape:
- medium
- there are many files, but the path patterns are mechanical and explicit
- safe if the queue is limited to bucketing plus reference refresh

## Candidate B: `hygiene.repo_root_navigation_polish`

Representative surfaces:
- root `README.md`
- `packages/README.md`
- `projects/README.md`

Why it is attractive:
- root-level navigation always matters
- a smaller pass would be quick and safe

Risk shape:
- low
- but the current root-level clutter is much smaller than the roadmap-history
  clutter
- less leverage right now than reducing the 200+ file flat history layer

## Decision

Chosen Queue V29 opener:
- `hygiene.roadmap_history_bucketing`

## Why this wins now

The docs history layer is now the biggest remaining navigation problem.

Queue V27 and Queue V28 already cleaned the `director` and `ai_washing` front
doors. `docs/roadmap_v2/` is now the most obvious remaining flat clutter
surface, so a bounded history-bucketing pass has the highest end-state
leverage.
