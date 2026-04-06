# Batched Execution Queue V31

## Purpose

This queue starts after Queue V30 completed cleanly.

It is a bounded hygiene/polish queue for repo-root clutter posture. The goal is
to classify the remaining repo-visible root surfaces and decide whether any of
those artifacts are safe cleanup candidates.

## Planning assumptions

- keep hygiene separate from active authority migration
- prefer review and posture before any deletion
- only surface a V32 cleanup if the review produces a real low-risk candidate

## Immediate execution queue

### Batch 1

Name:
- `hygiene.repo_root_clutter_review`

Why next:
- the repo root is now one of the last high-visibility places where mixed-era
  artifacts can still confuse first-contact navigation

Default gate:
- direct-reference scan for reviewed candidates
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `hygiene.repo_root_clutter_posture_refresh`

Why next:
- after the review, the hygiene lane should explicitly record what is keep,
  local-only noise, or retire-ready

Default gate:
- posture docs updated
- `git diff --check`

Status:
- complete

### Batch 3

Name:
- `hygiene.repo_root_clutter_checkpoint`

Why next:
- the queue should close with an explicit statement about whether V32 cleanup is
  justified and safe

Default gate:
- queue/checkpoint docs updated
- `git diff --check`

Status:
- complete
