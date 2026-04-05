# Fast but Safe Migration Protocol V1

## Purpose

This protocol is for running larger restructure batches without compromising
control, continuity, or reviewability.

It is designed for the current repo state, where:
- workspace landing zones exist
- shared package seeds are real
- the first project-member code seed is real
- compatibility shims are an accepted transition device

## Batch unit

The default fast batch should contain exactly four parts:
1. one authoritative code move
2. one bounded caller family migration
3. one focused doc and authority-map update
4. one acceptance gate

This is the largest default chunk that has repeatedly validated cleanly.

## Batch design rules

### Rule 1. One authority change per batch

Only one canonical location should change per batch.

Examples:
- one shared package slice
- one member-owned code slice

Do not change two separate authoritative homes in the same batch.

### Rule 2. One caller family per batch

A caller family should be grouped by:
- same domain
- same import edge
- same regression bundle

Good examples:
- one labeling-family import rewrite
- one classification-family import rewrite
- one planner-facing `director` slice

Bad examples:
- mixing labeling callers with aggregation callers
- mixing `director` extraction with unrelated project-member code moves

### Rule 3. Compatibility first

When authority changes, preserve the legacy import or path through a shim unless
there is a strong reason not to.

The new canonical destination must exist before callers move.

### Rule 4. Validation must be localizable

Every batch must declare a focused validation bundle before edits begin.

The bundle should include only:
- the touched package/member tests
- the direct regression family
- `make doctor` when import-path behavior changed
- package build smoke only when a shared package changed

### Rule 5. Clean worktree checkpoint

Every batch ends with:
- `git diff --check`
- build/test leftovers removed
- one clean commit

## Serialized lane inside a fast batch

These remain serialized even when we speed up:
- authority decision
- import-path decision
- package/member identity decision
- final acceptance gate

## Parallelizable lane inside a fast batch

These can run in parallel when write scopes do not overlap:
- read-only dependency mapping
- test-bundle enumeration
- migration note drafting
- README pointer updates
- package-local test drafting for the new canonical destination

A read-only sub-agent is appropriate here.
A write-capable parallel lane is not appropriate unless file ownership is fully
non-overlapping.

## Acceptance gate

A fast batch is accepted only when all applicable checks pass.

### Core gate
- targeted `ruff format --check`
- targeted `ruff check`
- targeted `py_compile`
- `git diff --check`

### Import gate
- `make doctor` if workspace/member import paths changed

### Caller-family gate
- focused pytest bundle for the migrated family

### Package gate
- `python -m build <path>` when a shared package changed

### Continuity gate
- legacy compatibility imports still work where promised
- docs and mapping notes reflect the new authority state

## Recommended cadence

Use this cadence for larger chunks:
1. checkpoint the intended family and validation bundle
2. move the authoritative code
3. add or keep the compatibility shim
4. migrate the bounded caller family
5. update docs and authority map
6. run the full acceptance gate once
7. commit immediately if clean

## Current recommended next batch shape

For `ai_washing`, the best fast-safe batch shape is:
- authority already moved: `ai_washing_member.labeling.common`
- next caller family: Group 1 labeling callers
- validation bundle: Group 1 tests only
- commit immediately after the gate

## Bottom line

Move faster by increasing the size of the caller-family batch, not by mixing
multiple authority changes together.
