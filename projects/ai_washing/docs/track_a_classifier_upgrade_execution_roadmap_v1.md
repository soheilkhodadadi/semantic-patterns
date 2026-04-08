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
- `reports/final/ai_washing_classifier_as_probe_benchmark_v1.csv`
- `reports/final/ai_washing_classifier_rubric_probe_slice_revised_labels_v1.csv`

Output:
- a benchmark note on whether the revised rubric resolves the known failure
  categories more cleanly than the older posture

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

## Phase 4. Local-model rerun

Goal:
- rerun the local model with the revised benchmark posture

Required outputs:
- overall held-out accuracy
- macro F1
- binary relevance accuracy
- conditional A/S accuracy

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
3. API `A` labels deferred rows
4. if API `A` disagrees with the local model, API `B` arbitrates
5. majority vote determines the final label on deferred rows

This keeps the system:
- reproducible
- fully automated
- free of manual intervention in the live labeling path

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
