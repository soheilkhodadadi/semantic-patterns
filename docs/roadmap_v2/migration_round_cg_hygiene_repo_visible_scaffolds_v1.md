# Migration Round CG: Hygiene Repo-Visible Scaffolds V1

## Scope

Batch 2 from Queue V22.

Batch:
- review the repo-visible scaffold and placeholder surfaces that still make the
  workspace look noisier than it is
- separate canonical front doors from active historical lanes, compatibility
  scaffolds, and low-signal placeholders

## Pre-Scan Result

The scaffold review stayed clean enough to run as the second Queue V22 batch.

What made it clean:
- it is docs-only and classification-oriented
- it does not change canonical ownership or move files
- it gives later hygiene rounds a grounded before/after map instead of generic
  cleanup intent

## Validation Gate

Default gate for this round:
- scan-backed scaffold review note
- `git diff --check`
