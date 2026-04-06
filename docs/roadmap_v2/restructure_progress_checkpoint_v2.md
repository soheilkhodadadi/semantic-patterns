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
- `816f367` `refactor: seed director readiness authority`
- `c9b7664` `refactor: seed ai-washing filing manifest authority`
- `010e24d` `refactor: seed ai-washing ff12 mapping authority`
- `6cfb7fe` `refactor: seed director branching authority`
- `205f010` `refactor: seed director state authority`

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
- branching helpers
- state compilation helpers

### Project-member layer

`projects/ai_washing` now has real member-owned code in three meaningful
clusters:
- labeling common surface
- classification support surface
- data index/sentence-table support surface

The active `ai_washing` member-owned authorities now include:
- `ai_washing_member.labeling.common`
- `ai_washing_member.labeling.ff12_mapping`
- `ai_washing_member.labeling.freeze_heldout_v2`
- `ai_washing_member.labeling.freeze_split_registry`
- `ai_washing_member.labeling.publish_rubric_freeze`
- `ai_washing_member.labeling.sample_heldout_v2_candidates`
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
- `director.branching`
- `director.state`
- `director.decision`
- `director.sensors`
- `director.playbooks`
- `director.snapshot`
- `director.gates`
- `ai_washing` labeling common family
- `ai_washing` classification support family
- `ai_washing` SEC index family
- `ai_washing` sentence-table family
- `ai_washing` benchmark-utils authority
- `ai_washing` build-filing-manifest authority
- `ai_washing` FF12 mapping authority
- `ai_washing` build-labeling-batch authority
- `ai_washing` held-out freeze authority
- `ai_washing` held-out sampler authority
- `ai_washing` audit sentence integrity authority
- `ai_washing` prepare IRR subset authority
- `ai_washing` adjudicate IRR labels authority

## Lane-by-lane state

### `director`

Current condition:
- hot lane
- repeated success under Protocol V2
- package boundary is getting cleaner with each round

What is now strongest:
- downstream orchestration helpers are clustering naturally around the package

What remains clearly root-owned:
- `snapshot`
- `decision`
- `executor`
- `playbooks`
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

## Queue V3 note

Queue V3 has now started cleanly with:

1. `semantic_director.branching`
2. `semantic_director.state`
3. `ai_washing_member.labeling.build_labeling_batch`

That confirms the next cycle reset is working as intended.

## Queue V3 close note

Queue V3 has now completed cleanly through its planned three-round cycle:

1. `semantic_director.branching`
2. `semantic_director.state`
3. `ai_washing_member.labeling.build_labeling_batch`

That put the repo back at a real checkpoint before choosing Queue V4.

## Queue V4 note

Queue V4 has now started cleanly with:

1. `ai_washing_member.labeling.sample_heldout_v2_candidates`

This restores lane balance at the start of the next cycle and sets up a clean
held-out workflow follow-on round.

## Queue V5 note

Queue V5 has now opened cleanly with:

1. `semantic_director.sensors`

This starts the next cycle with a high-leverage package-boundary cleanup in
`director` after the migrated-surface relevance audit confirmed that the
already-promoted authorities are active and worth keeping.

## Queue V5 progress note

Queue V5 Batch 1 has now completed cleanly:

1. `semantic_director.sensors`

This tightened the `director` package boundary further by removing a root
`director.core.sensors` dependency from `semantic_director.readiness` while
leaving the cross-lane `ai_washing` edge on the compatibility shim for a later
separate round.

## Queue V5 second-batch note

Queue V5 Batch 2 has now completed cleanly:

2. `ai_washing_member.labeling.freeze_split_registry`

This kept the split-freeze workflow current in the member-owned lane while
leaving the stable root command surface in `tests/test_director_roadmap_model.py`
unchanged on purpose.

## Queue V5 close note

Queue V5 has now completed cleanly through its planned three-round cycle:

1. `semantic_director.sensors`
2. `ai_washing_member.labeling.freeze_split_registry`
3. `semantic_director.playbooks`

That closes the queue at a real checkpoint before choosing the next cycle.

## Queue V6 note

Queue V6 has now opened with the next clean `ai_washing` follow-on authority:

1. `ai_washing_member.labeling.publish_rubric_freeze`

A separate legacy/template hygiene queue is now tracked independently so cleanup
does not get mixed into active authority moves.

## Queue V6 progress note

Queue V6 Batch 1 has now completed cleanly:

1. `ai_washing_member.labeling.publish_rubric_freeze`

This extends the member-owned split-freeze workflow while deliberately leaving
the stable root command assertion in `tests/test_director_roadmap_model.py` on
the compatibility path for now.

## Queue V6 second-batch note

Queue V6 Batch 2 has now completed cleanly:

2. `semantic_director.snapshot`

This moves the snapshot ingest authority into the package lane while keeping
the Atlas-adjacent adapter boundary explicit and unchanged for now.

## Queue V6 close note

Queue V6 has now completed cleanly through its planned three-round cycle:

1. `ai_washing_member.labeling.publish_rubric_freeze`
2. `semantic_director.snapshot`
3. `ai_washing_member.labeling.audit_sentence_integrity`

This closes the cycle with a small IRR workflow move in the flagship lane while
leaving the roadmap-model command surface on the compatibility path for a later
control-plane round.

## Queue V7 note

Queue V7 has now opened cleanly with:

1. `ai_washing_member.labeling.prepare_irr_subset`

This starts the next cycle inside the current-stage IRR workflow cluster while
leaving the roadmap-model command strings on the compatibility path for now.

## Queue V7 second-batch note

Queue V7 Batch 2 has now completed cleanly:

2. `ai_washing_member.labeling.adjudicate_irr_labels`

This keeps the IRR workflow moving inside the member-owned lane while still
leaving roadmap-model command strings on the compatibility path for now.

## Queue V7 close note

Queue V7 has now completed cleanly through its planned three-round cycle:

1. `ai_washing_member.labeling.prepare_irr_subset`
2. `ai_washing_member.labeling.adjudicate_irr_labels`
3. `semantic_director.gates`

This closes the cycle with two current-stage IRR workflow moves in the flagship
lane and one compact downstream `director` package cleanup that sets up a
future `executor` round.

## Queue V8 note

Queue V8 has now opened cleanly with:

1. `ai_washing_member.labeling.compute_irr_metrics`

This continues the current-stage IRR reporting workflow in the member-owned
lane while keeping the roadmap-model command surface on the compatibility path
for now.

## Queue V8 progress note

Queue V8 Batch 1 has now completed cleanly:

1. `ai_washing_member.labeling.compute_irr_metrics`

This moves the IRR metrics authority into the member-owned lane and keeps the
direct regression pressure concentrated in the IRR workflow bundle before the
next `diagnose_irr_disagreements` follow-on round.

## Queue V8 second-batch note

Queue V8 Batch 2 has now completed cleanly:

2. `ai_washing_member.labeling.diagnose_irr_disagreements`

This keeps the IRR reporting workflow inside the member-owned lane while
deliberately leaving roadmap-model command strings on the compatibility path
for now.

## Queue V8 close note

Queue V8 has now completed cleanly through its planned three-round cycle:

1. `ai_washing_member.labeling.compute_irr_metrics`
2. `ai_washing_member.labeling.diagnose_irr_disagreements`
3. `semantic_director.executor`

This closes the cycle with two current-stage IRR reporting workflow moves in
the flagship lane and one compact `director` control-runtime move that keeps
the package boundary moving downstream without touching Atlas-adjacent adapter
surfaces.

## Queue V9 note

Queue V9 has now opened cleanly with:

1. `ai_washing_member.labeling.publish_preliminary_results_readiness`

This continues the current-stage preliminary-results workflow in the
member-owned lane before rotating into a compact `director` cost/LLM cleanup.

## Queue V9 progress note

Queue V9 Batch 1 has now completed cleanly:

1. `ai_washing_member.labeling.publish_preliminary_results_readiness`

This moves the preliminary-results publisher into the member-owned lane and
keeps the direct regression pressure concentrated in the IRR/preliminary
workflow bundle before the `director` rotation.

## Queue V9 second-batch note

Queue V9 Batch 2 has now completed cleanly:

2. `semantic_director.cost`

This rotates into the `director` lane with a compact control-runtime budget
surface while deliberately leaving the ai-washing assistive callers on the
compatibility path for a later separate round.

## Queue V9 close note

Queue V9 has now completed cleanly through its planned three-round cycle:

1. `ai_washing_member.labeling.publish_preliminary_results_readiness`
2. `semantic_director.cost`
3. `semantic_director.llm`

This closes the cycle with one current-stage preliminary-results move in the
flagship lane and a compact two-step `director` runtime chain that now has a
cleaner package-owned budget and LLM refinement boundary.

## Queue V4 progress note

Queue V4 has now completed its first two `ai_washing` rounds cleanly:

1. `ai_washing_member.labeling.sample_heldout_v2_candidates`
2. `ai_washing_member.labeling.freeze_heldout_v2`

That leaves one planned lane-rotation round before the next checkpoint:

3. `semantic_director.decision`

## Queue V4 close note

Queue V4 has now completed cleanly through its planned three-round cycle:

1. `ai_washing_member.labeling.sample_heldout_v2_candidates`
2. `ai_washing_member.labeling.freeze_heldout_v2`
3. `semantic_director.decision`

That puts the repo back at a real checkpoint before choosing Queue V5.

## Bottom line

The restructure is now in a stronger position than the earlier checkpoint
captured.

The most important shift is:
- we now have enough repeated success to manage by ordered execution cycles,
  not just one-off migration decisions

That is the right foundation for the next phase of faster, still-safe work.
