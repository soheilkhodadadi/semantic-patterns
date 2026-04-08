# AI-Washing Track A Classifier Upgrade Execution Roadmap V1

## Purpose

This is the working roadmap for the next classifier-improvement phase.

It turns the current diagnosis into an execution order.

## Current baseline

Selected model:
- `binary_relevance_then_as_v1`

Published benchmark:
- overall accuracy: `0.7062`
- binary relevance accuracy: `0.8192`
- conditional A/S accuracy: `0.7556`

Interpretation:
- relevance is not the main bottleneck
- the main bottleneck is the `Actionable` / `Speculative` boundary

## Phase 1. Revised rubric benchmark

Goal:
- test whether the revised A/S rubric improves boundary clarity on the fixed
  probe slice

Inputs:
- `projects/ai_washing/docs/track_a_as_rubric_rewrite_v1.md`
- `reports/final/ai_washing_classifier_as_probe_benchmark_v2.csv`
- `reports/final/ai_washing_classifier_rubric_probe_slice_revised_labels_v1.csv`

Output:
- a benchmark note on whether the revised rubric resolves the known failure
  categories more cleanly than the older posture

Current status:
- completed on the fixed `16`-row slice
- both blinded rubric variants reproduced the revised benchmark labels exactly
- Phase 2 is now the deciding step because the fixed slice is no longer
  discriminating enough to choose between Variant A and Variant B

## Phase 2. Small benchmark pack

Goal:
- move from the fixed `16`-row slice to a slightly larger reviewed benchmark
  pack focused on the same failure modes

Focus categories:
- future intent
- build / integrate / invest
- risk / competition context
- internal operating use vs generic tooling

Output:
- a stable reviewed boundary pack for retraining and later API comparison

Current status:
- completed on the `34`-row reviewed boundary pack
- Variant A and Variant B both matched the reviewed labels exactly
- the benchmark did not separate the two rubric variants
- proceed with Variant A as the default revised rubric and move to retraining

## Phase 3. Retraining decision

Goal:
- decide whether to:
  - retrain directly under the revised rubric
  - first clean or expand the training set
  - also test probability tuning after retraining

Priority order:
1. rubric rewrite
2. targeted training-set cleanup / expansion
3. threshold or probability tuning

Current posture:
- `1` and `2` are now effectively complete at the rubric-benchmark level
- the first controlled retraining tranche is now built:
  - `34` reviewed boundary rows
  - `12` training-eligible overlap rows
  - `8` actual label updates in `labels_master`
- the next live execution step is local retraining on the revised labels-master
  tranche

## Phase 4. Local-model rerun

Goal:
- rerun the local model with the revised benchmark posture

Required outputs:
- overall held-out accuracy
- macro F1
- binary relevance accuracy
- conditional A/S accuracy

Current constraint:
- the frozen `held_out_v2` report exists, but the underlying
  `data/validation/held_out_sentences_v2.csv` asset is currently missing from
  the repository tree
- so the immediate honest rerun surfaces are:
  - revised frozen validation split
  - regenerated IRR boundary benchmark
- a fresh publication-grade held-out rerun still requires recovering or
  regenerating the frozen `held_out_v2` CSV

Current result:
- the first revised-rubric retraining tranche did not improve the local binary
  model
- `binary_relevance_then_as_boundary_v2` underperformed
  `binary_relevance_then_as_v1` on both available secondary surfaces
- the observed pattern is:
  - slightly better binary relevance behavior
  - noticeably worse actionable/speculative behavior
- so the next step is not promotion
- it is a larger reviewed A/S tranche plus another controlled retraining pass

Decision gate:
- if we meaningfully improve and approach `0.80+`, continue optimizing the
  local model
- if gains stall, open the selective-defer hybrid lane

## Phase 5. Selective-defer simulation

Goal:
- test whether a hybrid classifier improves hard-case accuracy without giving
  up the local pipeline

Design:
1. local model handles easy cases
2. edge cases are deferred
3. API `A` labels deferred rows with a lighter lower-cost model
4. if API `A` disagrees with the local model, API `B` arbitrates
   with a stronger model
5. majority vote determines the final label on deferred rows

This keeps the system:
- reproducible
- fully automated
- free of manual intervention in the live labeling path

Critical caution:
- API `A` and API `B` need enough independence in capability or prompting
  posture that the second call adds real arbitration value

## Phase 6. API lane decision

Only open the live API lane if:
- the local model still cannot clear the publication-grade threshold after the
  revised-rubric cycle
- or the hybrid simulation clearly improves A/S accuracy at a reasonable
  deferral rate and cost

## Success criteria

Minimum:
- overall held-out accuracy `>= 0.80`

Stretch:
- overall held-out accuracy around `0.85`
- materially stronger conditional A/S accuracy

## Bottom line

The next step is not blind retraining.

The next step is:
1. benchmark the revised rubric
2. enlarge the reviewed boundary pack
3. retrain locally
4. only then test the selective-defer hybrid design
