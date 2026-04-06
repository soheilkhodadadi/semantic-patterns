# Fresh Authority Comparison V25

## Purpose

Choose Queue V22 after Queue V21 completed cleanly.

## Candidates compared

1. `semantic_director.utility_followon_bundle`
2. `hygiene.active_legacy_inventory`

## Candidate A: `semantic_director.utility_followon_bundle`

Representative surfaces:
- `semantic_ai_washing.director.core.utils`
- `semantic_ai_washing.director.core.security`
- `semantic_ai_washing.director.core.openai_responses`

Why it is attractive:
- package-owned `semantic_director` modules still import these helpers
- they are the clearest remaining root-only `director` utility pressure
- a follow-on here could further reduce compatibility imports inside the package

Risk shape:
- medium
- the pressure is real, but it is not clean package-boundary pressure anymore
- all three surfaces are already deliberate compatibility shims backed by
  `semantic_ai_washing.labcore.*`
- forcing them into `semantic_director` would blur the shared-labcore boundary
  rather than clarify it

## Candidate B: `hygiene.active_legacy_inventory`

Why it is attractive:
- the migration lanes are now late-stage enough that hygiene clarity has become
  a higher-leverage need than another marginal `director` extraction
- the separate hygiene queue is already defined and intentionally bounded
- an explicit inventory/review pass can reduce future queue guesswork without
  mixing deletion into active authority work

Risk shape:
- low
- docs-only and scan-backed
- no canonical authority changes
- no destructive cleanup unless a later hygiene batch explicitly proves a
  surface is retire-ready

## Decision

Chosen Queue V22 opener:
- `hygiene.active_legacy_inventory`

## Why this wins now

It is the more honest next move.

After Queue V21, the remaining `director` utility pressure is shallow and mostly
intentional. The utility surfaces still referenced by `semantic_director` are
already labcore-backed compatibility layers, not strong remaining `director`
authorities.

That means the higher-value next queue is the first deliberate hygiene-class
queue: update the live-vs-legacy inventory, review the repo-visible scaffolds,
and only then test whether any candidate surfaces are actually ready for a later
quarantine/retirement pass.
