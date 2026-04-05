# Larger Batch Readiness Checkpoint V1

## Purpose

This checkpoint asks whether the restructure is now mature enough to batch work
in larger chunks without giving up safety.

## Why this checkpoint is timely

A complete grouped migration family has now been finished for one real project
surface:
- Group 1 labeling callers
- Group 2 classification callers
- Group 3 aggregation, analysis, and data callers
- Group 4 director-adjacent validation caller

That is enough evidence to reassess batch size.

## What has now been proven

The current workflow repeatedly succeeds when we keep these stable:
- one authority already in force
- one coherent import edge
- one project or package lane
- one focused regression gate
- one clean commit

It is now also proven that we can absorb small blocker fixes inside a batch when
those fixes are:
- surfaced by the declared gate
- low blast radius
- directly necessary to restore the gate

## What is now safe to enlarge

The safest next enlargement is not multiple authority changes.
It is a broader caller-family batch under an already-established authority.

Safe larger-batch pattern:
- one existing authority
- up to two adjacent caller families
- one shared regression gate that already spans both families
- no package identity change
- no shared-package extraction in the same commit

Examples now likely safe:
- two adjacent `ai_washing` caller families that depend on the same member-owned
  surface and already share a regression bundle
- a `director` package slice plus its immediate direct callers only when no
  project-member migration is mixed into the same batch

## What is still not safe to enlarge

Still avoid combining:
- a shared-package extraction with a project-member migration
- two unrelated authorities in one batch
- package identity changes with caller migrations
- broad legacy cleanup/deletion with active import rewrites

## Recommended upgraded protocol

Use a "larger but still bounded" batch only when all of the following hold:
1. authority is already canonical and unchanged in the batch
2. all touched callers belong to the same project or package lane
3. one focused pytest bundle covers the full batch
4. rollback is obvious from one diff/commit
5. the worktree is clean before the batch starts

## Recommended next experiment

The next good place to try a larger batch is not another `labeling/common`
round, because that family is already complete.

The better candidate is the next project-local migration family where:
- authority is already clear
- the dependency map is known
- the regression gate is already narrow

That means we can probably start testing two-family batches selectively, but not
across mixed authority boundaries.

## Bottom line

Yes, we can start batching somewhat larger rounds now.

But the safe upgrade is:
- larger caller-family batches under one authority
not:
- mixed authority moves in one batch


## First experiment result

The first larger-batch experiment has now passed through:
- `docs/roadmap_v2/migration_round_n_ai_washing_classification_support_v1.md`

Observed result:
- one authority move
- two adjacent caller families
- one shared regression gate
- clean pass on the declared validation bundle

This confirms that the upgraded protocol is workable when it stays within one
project lane and one authority surface.

## Second experiment result

The second larger-batch experiment has now passed through:
- `docs/roadmap_v2/migration_round_o_ai_washing_index_sec_batch_v1.md`

Observed result:
- one authority move
- two adjacent caller families
- one shared regression gate
- clean pass on the declared validation bundle

This reinforces that the upgraded protocol is not a one-off success. It is now
repeatable for `ai_washing` project-member migrations when authority and the
gate are both explicit.
