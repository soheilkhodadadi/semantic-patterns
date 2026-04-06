# Restructure Progress Checkpoint V2

## Purpose

This checkpoint updates the earlier progress note after the recent sequence of
successful `director` fresh-authority rounds. The goal is to give us a better
working picture of:

- what is already stable
- what is still missing in each lane
- where the next speed-up should come from

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Recent commits that matter for the current shape:
- `8d7b703` `refactor: seed ai-washing benchmark utils authority`
- `829fbeb` `refactor: seed director roadmap model authority`
- `c537a88` `refactor: seed director render authority`
- `2b854d5` `refactor: seed director task graph authority`
- `05c87b4` `refactor: seed director config authority`
- `c9b7664` `refactor: seed ai-washing filing manifest authority`

## What is materially real now

### Shared package layer

`packages/labcore` is stable as the shared low-level package for:
- runtime
- audit
- security
- OpenAI Responses transport
- registry lanes and adapters

`packages/director` is now a real higher-level package, not just a shell. It
has canonical package code for:
- schema/export surface
- default policy templates
- roadmap-model loading/query helpers
- roadmap rendering helpers
- task-graph helpers
- config/path loading helpers
- readiness evaluation helpers

### Project-member layer

`projects/ai_washing` now has real member-owned code in three meaningful
clusters:
- labeling common surface
- classification support surface
- data index/sentence-table support surface

The active `ai_washing` member-owned authorities now include:
- `ai_washing_member.labeling.common`
- `ai_washing_member.labeling.ff12_mapping`
- `ai_washing_member.classification.preliminary_pipeline`
- `ai_washing_member.classification.model_runtime`
- `ai_washing_member.classification.benchmark_utils`
- `ai_washing_member.data.build_filing_manifest`
- `ai_washing_member.data.index_sec_filings`
- `ai_washing_member.data.extract_sentence_table`

### Control-plane layer

The control plane now has enough structure to support faster execution:
- manifest/evidence contracts
- workspace-member contract
- package/member acceptance checklist
- extraction protocol
- fast-safe migration protocol V2

## What is proven now

The repo now has repeated evidence for all of these:

1. authority seeding into a canonical package/member destination
2. legacy compatibility shim retention
3. caller-family rewrites under one authority
4. one shared acceptance gate per batch
5. clean package build smoke after shared-package changes

This is now proven for:
- `labcore`
- `director.schemas`
- `director.policies`
- `director.roadmap_model`
- `director.render`
- `director.task_graph`
- `director.config`
- `director.readiness`
- `ai_washing` labeling common family
- `ai_washing` classification support family
- `ai_washing` SEC index family
- `ai_washing` sentence-table family
- `ai_washing` benchmark-utils authority
- `ai_washing` build-filing-manifest authority
- `ai_washing` FF12 mapping authority

## Lane-by-lane state

### `director`

Current condition:
- hot lane
- repeated success under Protocol V2
- package boundary is getting cleaner with each round

What is now strongest:
- downstream orchestration helpers are clustering naturally around the package

What remains clearly root-owned:
- `branching`
- `snapshot`
- `state`
- `decision`
- `executor`
- `playbooks`
- `sensors`
- `gates`
- `llm`
- `cost`

Interpretation:
- `director` has enough momentum that more package work is justified
- but continuing indefinitely in only this lane would starve the flagship
  project-member lane

### `ai_washing`

Current condition:
- member-owned code is real and stable
- earlier member-owned authority moves have mostly shallow direct-root tails now

What is now strongest:
- the next meaningful acceleration is a fresh authority move, not more cleanup

What just closed cleanly:
- `build_filing_manifest`
- `ff12_mapping`

What likely follows next:
- the next fresh authority should be re-scanned after this queue reset rather
  than assumed in advance

Interpretation:
- `ai_washing` is ready for another member-owned authority round
- it is now the best lane to rotate into if we want balanced progress

## What should change in our execution style

We should now stop treating each round as an isolated choice.

Instead, we should work in short execution cycles with:
- an ordered queue
- explicit lane rotation
- one checkpoint after a small series of rounds

## Recommended execution rule set

### Rotation rule

Do not run more than two fresh-authority rounds in the same lane without a
checkpoint or an explicit reason.

Reason:
- it preserves momentum
- it prevents `director` from outpacing `ai_washing`
- it makes the repo more balanced as a lab rather than a single-package pivot

### Cycle rule

Use cycles of three rounds:

1. one fresh-authority round
2. one follow-on fresh-authority round in the stronger lane
3. one lane-rotation round

Then stop for a checkpoint.

### Gate rule

Keep the existing Protocol V2 per round, but add a cycle-close gate:

- `make doctor`
- touched-package tests
- touched root regression bundles
- package build smoke for any touched package
- `git diff --check`

Use a broader repo-wide suite only when its baseline is known clean for the
affected lanes.

## Current cycle result

The current three-round cycle has now completed cleanly:

1. `ai_washing_member.data.build_filing_manifest`
2. `semantic_director.config`
3. `semantic_director.readiness`

That means the original queue checkpoint was reached before Batch 4, and the
provisional Batch 4 round has now also completed cleanly.

## Queue-close note

The provisional Batch 4 authority also completed cleanly:

4. `ai_washing_member.labeling.ff12_mapping`

That closes the current queued cycle and puts us at a new selection point for
the next execution board.

## Bottom line

The restructure is now in a stronger position than the earlier checkpoint
captured.

The most important shift is:
- we now have enough repeated success to manage by ordered execution cycles,
  not just one-off migration decisions

That is the right foundation for the next phase of faster, still-safe work.
