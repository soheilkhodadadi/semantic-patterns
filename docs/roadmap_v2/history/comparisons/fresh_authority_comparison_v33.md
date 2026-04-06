# Fresh Authority Comparison V33

## Purpose

Choose the next bounded late-stage polish queue after Queue V29.

## Candidates

### Option A
- `hygiene.repo_root_navigation_polish`

### Option B
- `hygiene.roadmap_history_archive_export_prep`

## Comparison

### Repo-root navigation polish

Pros:
- improves the actual front door most collaborators will hit first
- reduces mixed-era signaling between the legacy project story and the current
  lab structure
- aligns `README.md`, `packages/README.md`, and `docs/projects/README.md` with
  the now-cleaner `roadmap_v2` front door

Cons:
- mostly documentation posture, not a structural move
- needs care to avoid rewriting stable delivery context too aggressively

### Roadmap history archive/export prep

Pros:
- would continue reducing documentation-management debt
- keeps the history lane disciplined

Cons:
- lower immediate leverage after Queue V29
- risks polishing the audit layer again while the repo front door still tells a
  mixed story
- archive/export prep is useful later, but not yet the bottleneck

## Decision

Choose:
- `hygiene.repo_root_navigation_polish`

## Why

Queue V29 already made the roadmap history layer legible. The stronger next
move is to make the repo root and shared workspace entry points reflect that new
navigation model so contributors do not have to infer it indirectly.
