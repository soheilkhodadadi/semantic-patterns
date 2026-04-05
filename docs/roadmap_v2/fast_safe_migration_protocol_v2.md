# Fast but Safe Migration Protocol V2

## Purpose

This protocol upgrades the earlier fast-safe guidance using the restructure work
that has now validated cleanly in practice.

It is designed for the current repo state, where:
- shared packages are real
- project-member seeds are real
- compatibility shims are an accepted transition device
- larger batches have already passed under focused gates

## What V2 changes

V1 assumed the default fast batch should stay close to:
- one authority move
- one caller family
- one focused gate

V2 keeps the same safety spine, but recognizes two proven batch shapes:

### Shape A: two-family batch
- one authority move
- two adjacent caller families in one lane
- one shared regression gate

### Shape B: four-family batch
- one authority move
- up to four tightly related families in one lane
- one shared regression gate
- at most one family may be the direct validation/import edge rather than a
  separate production-facing caller family

The four-family shape is now proven, but only under explicit constraints.

## Hard constraints

Every fast batch must still satisfy all of these:
1. one authoritative home changes in the batch
2. all touched callers stay in one lane
3. rollback is obvious from one diff or one small commit stack
4. the worktree is clean before edits begin
5. the validation gate is declared before edits begin

If any of these stop being true, the batch is too large.

## Allowed batch shapes

### 1. Authority seed batch

Use when a member- or package-owned surface is not yet canonical.

Contents:
- copy canonical implementation into the destination
- replace legacy path with a compatibility shim
- migrate one or two direct caller families
- add member/package-local tests
- run one shared gate

### 2. Established-authority caller batch

Use when the authority is already canonical and proven.

Contents:
- no new authority decision
- migrate up to four tightly related families
- keep the legacy shim intact
- run one shared gate

This is the fastest safe shape currently justified in this repo.

## What counts as a family

A family is valid when it shares:
- the same authority surface
- the same lane
- the same dependency edge
- the same regression story

Examples of valid families:
- one production caller cluster
- one benchmark caller cluster
- one direct contract/test import cluster

Examples of invalid family grouping:
- mixing two different authorities
- mixing shared-package extraction with project-member migration
- mixing unrelated domains just because the tests overlap

## Validation design

The acceptance gate should be ordered like this:

1. `make doctor` if import or workspace behavior changed
2. targeted `ruff format --check`
3. targeted `ruff check`
4. targeted `py_compile`
5. one shared pytest bundle
6. `git diff --check`
7. package build smoke only when a shared package changed

The gate should be written down before code moves start.

## Handling blocker fixes inside a batch

A blocker fix may stay inside the active batch only if:
- it is surfaced by the declared gate
- it is low blast radius
- it restores the intended migration rather than broadening scope

If a fix changes the authority decision, package identity, or lane boundary,
stop and split the work.

## Parallel work under V2

Read-only parallel help is encouraged for:
- dependency mapping
- candidate family enumeration
- validation-bundle drafting
- migration-note drafting

Write-parallel work is still restricted.

Only run write-parallel work when:
- file ownership is disjoint
- the authority decision is already locked
- the shared gate can still be evaluated as one batch

In practice, this means:
- docs and read-only audit work can run in parallel
- authority moves and caller rewrites should remain serialized

## Current proven upper bound

The current proven upper bound is:
- one authority move
- up to four tightly related families in one lane
- one shared regression gate

That does **not** justify:
- mixed authority batches
- package extraction plus project-member migration in the same code batch
- broad cleanup/deletion while import rewrites are active

## Recommended cadence

1. lock the authority and lane
2. name the families
3. declare the gate
4. move the canonical implementation if needed
5. keep or add the legacy shim
6. migrate the caller families
7. update the docs and checkpoints
8. run the gate once
9. commit immediately if clean

## Bottom line

V2 allows us to move faster because we now have real evidence for larger
batches.

But the speed comes from:
- staying inside one authority
- staying inside one lane
- making the gate stronger

not from loosening the safety boundary.
