# AI-Washing Navigation Posture Refresh V1

## Purpose

Record what Queue V28 changed in the repo-visible navigation story for
`projects/ai_washing`.

## What Queue V28 cleaned up

Queue V28 did two bounded hygiene/polish moves:

1. moved older planning/reference notes into
   `projects/ai_washing/planning_notes/`
2. turned `projects/ai_washing/README.md` into a cleaner project-member front
   door

## What this means now

`projects/ai_washing/` now reads more like a stable project member:
- top level contains the current README and the current root-surface triage note
- planning notes live in a dedicated folder
- migration sheets already live in a dedicated folder

## Remaining posture

The remaining late-stage work is now even clearer:
- active workflow migration is largely complete
- remaining root-owned surfaces are wrappers, dormant-but-relevant utilities,
  or future hygiene candidates
- the next queue should be chosen for real leverage, not to keep the history
  moving

## Recommended next-step posture

- do not reopen `ai_washing` immediately for another top-level navigation
  cleanup
- prefer the next queue from:
  - a bounded hygiene follow-on with real remaining leverage
  - or a deliberately chosen late-stage polish class elsewhere

Queue V28 therefore improves the end-state story without reopening any settled
project-member migration lane.
