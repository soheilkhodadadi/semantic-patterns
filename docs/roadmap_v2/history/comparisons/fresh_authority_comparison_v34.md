# Fresh Authority Comparison V34

## Purpose

Choose the next bounded late-stage polish queue after Queue V30.

## Candidates

### Option A
- `hygiene.repo_root_clutter_review`

### Option B
- `hygiene.roadmap_history_archive_export_prep`

## Comparison

### Repo-root clutter review

Pros:
- addresses the remaining repo-visible ambiguity at the real top-level entry
  surface
- can distinguish tracked root artifacts that still matter from ones that are
  now only historical or low-signal
- creates a clean decision base for a safe V32 cleanup queue if a real retire
  candidate exists

Cons:
- mostly posture and inventory, not structural code change
- may conclude that only a very small cleanup is justified

### Roadmap history archive/export prep

Pros:
- would continue to formalize the audit layer
- may help future export/archive work if the history corpus keeps growing

Cons:
- lower immediate leverage after Queue V29
- the history layer is already readable enough for current use
- does less for first-contact clarity than cleaning the actual repo root story

## Decision

Choose:
- `hygiene.repo_root_clutter_review`

## Why

The repo root still mixes clearly canonical files with a small number of
legacy-looking or local-only surfaces. That is the more honest next late-stage
problem. Reviewing it now gives us a bounded way to decide whether V32 should
perform a real cleanup or stop at posture.
