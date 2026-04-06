# Batched Execution Queue V22

## Purpose

This queue starts after Queue V21 completed cleanly.

It is the first deliberate hygiene-class queue. The goal is to improve the
clarity of what is still live, what is merely compatible, and what may later be
retired, without mixing deletion into active authority migration.

## Planning assumptions

- keep Protocol V2 as the discipline spine where applicable
- keep hygiene separate from active authority migration
- keep one bounded hygiene batch per commit
- do not delete or quarantine code surfaces unless direct-reference checks are
  clean and the rationale is explicit
- keep Atlas/private spillover watch active even though this queue is docs-first

## Immediate execution queue

### Batch 1

Name:
- `hygiene.active_legacy_inventory`

Why next:
- the `ai_washing` live-vs-legacy picture should be current before any further
  queue selection
- active migration pressure in `ai_washing` is now low enough that stale triage
  creates more confusion than speed

Default gate:
- scan-backed inventory note
- `git diff --check`

Status:
- complete

### Batch 2

Name:
- `hygiene.repo_visible_scaffold_review`

Why next:
- the repo now has enough migration history that top-level visibility matters
- we need a clear distinction between canonical front doors, active historical
  lanes, compatibility scaffolds, and low-signal placeholders

Default gate:
- scan-backed scaffold review note
- `git diff --check`

Status:
- complete

### Batch 3

Name:
- `hygiene.quarantine_readiness_shortlist`

Why next:
- the right hygiene question is no longer "what looks old?"
- it is "what is actually ready for retire/quarantine without breaking docs,
  shims, or script inventory expectations?"

Default gate:
- direct-reference scan for targeted legacy candidates
- written rationale for every not-ready verdict
- `git diff --check`

Status:
- complete
