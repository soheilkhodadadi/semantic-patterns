# Migrated Surface Relevance Audit V1

## Purpose

Do a quick relevance check on the already-migrated authorities before opening
Queue V5.

The goal is not to prove the whole repo is clean. The goal is narrower:
- confirm that the surfaces we have already promoted are still active
- confirm they are not obviously template leftovers or dead legacy carry-forward
- decide whether Queue V5 can proceed without stopping for a broad hygiene pass

## Audit rule

A migrated authority is treated as `active` when it satisfies all of these:
- has non-trivial implementation size
- has at least one live reference in `src/`, `packages/`, `projects/`, or `tests/`
- has a direct package/member test present

## Result

The migrated authorities inspected in this quick audit all passed the active-use
screen.

Sample results:
- `ai_washing_member.labeling.common`: active, 135 lines, 37 references, direct test present
- `ai_washing_member.data.build_filing_manifest`: active, 366 lines, 4 references, direct test present
- `ai_washing_member.labeling.freeze_heldout_v2`: active, 108 lines, 1 reference, direct test present
- `semantic_director.roadmap_model`: active, 155 lines, 14 references, direct test present
- `semantic_director.decision`: active, 308 lines, 7 references, direct test present
- `semantic_director.readiness`: active, 385 lines, 6 references, direct test present

Broader conclusion:
- the already-migrated authorities do not currently look like template junk
- they do not currently look like irrelevant carry-forward surfaces
- they look active enough to justify staying in the new structure

## Decision

Proceed into Queue V5 without pausing for a broad cleanup sweep.

Do not treat this as a substitute for later hygiene work.

The legacy/template concern is still real, but it should be handled by:
- separate bounded hygiene batches
- lane-local retirement review
- explicit archival or deletion decisions after active authorities are stable

## Operational consequence

Queue V5 can keep the current protocol:
- fresh-authority comparison
- batched queue selection
- one clean Protocol V2 batch at a time

A broader repo usefulness/relevance pass should happen later as a dedicated
hygiene cycle, not as a hidden side quest inside active migration batches.
