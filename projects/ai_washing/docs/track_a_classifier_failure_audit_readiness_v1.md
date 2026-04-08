# AI-Washing Track A Classifier Failure Audit Readiness V1

## Purpose

This note turns the existing held-out and IRR artifacts into a concrete first
failure-audit handoff.

The goal is to avoid starting the classifier-upgrade lane with vague
intuitions. We already have enough evidence to focus the first diagnostic pass.

## Core source artifacts

Held-out evaluation:
- `reports/evaluation/heldout_eval_prelim_v2.json`
- `artifacts/models/prelim_selected_model_v1.json`

IRR / disagreement assets:
- `reports/labels/irr_report.json`
- `reports/labels/irr_disagreement_diagnostic_v1.json`
- `reports/labels/irr_confusion_matrix.csv`
- `reports/labels/irr_disagreement_rows_v1.csv`
- `data/labels/v1/irr_subset_master.csv`
- `data/labels/v1/irr_subset_rater2_completed.xlsx`

Current `2025` spot-check anchor:
- `projects/ai_washing/docs/track_a_2025_classification_spot_check_v1.md`

## What the current evidence already says

### Held-out evaluation

Current selected model:
- `binary_relevance_then_as_v1`

Current headline metrics:
- overall accuracy: `0.7062`
- macro F1: `0.6729`
- binary relevance accuracy: `0.8192`
- conditional actionable/speculative accuracy: `0.7556`

Interpretation:
- the relevance gate is not perfect, but it is materially stronger than the
  full three-way headline
- most of the remaining damage is downstream of the relevance step

### IRR evidence

Headline three-class IRR:
- kappa: `0.675`

Decomposed IRR:
- binary relevance kappa: `0.7586`
- conditional actionable/speculative kappa: `0.6364`

Transition pattern:
- `A->S`: `6`
- `A->I`: `7`
- `S->A`: `6`
- `S->I`: `7`
- `I->A`: `0`
- `I->S`: `0`

Interpretation:
- the worst conceptual instability is not `Irrelevant` swallowing everything
- it is the actionable/speculative boundary plus some spillover into
  relevance-vs-nonrelevance for sentences already near that edge
- disagreement is concentrated in `Actionable` / `Speculative`, not
  `Irrelevant`

## Practical implication for the next diagnostic round

The first classifier-upgrade pass should **not** start from:
- a blind model swap
- a huge new human-labeling batch
- a generic “improve relevance detection” story

It should start from:
1. targeted review of `A/S` disagreement rows
2. review of long / clause-heavy sentences among held-out misses
3. a smaller check on the `Relevant` vs `Irrelevant` boundary only where the
   current rubric is obviously unstable

## First-pass audit tasks

### FA1. Error slice assembly

Prepare one compact audit pack containing:
- held-out `A->S` errors
- held-out `S->A` errors
- held-out `I->A` and `I->S` false-positive relevance rows
- IRR disagreement rows from:
  - `reports/labels/irr_disagreement_rows_v1.csv`

### FA2. Sentence-quality flags

For the same audit pack, add simple QC flags:
- unusually long sentence
- obvious header/list artifact
- clause-heavy segmentation
- generic risk/compliance wording
- future-plan / commercialization wording
- current-use / deployment wording

### FA3. Rubric-stability probe setup

Build tiny `10-20` sentence packs for:
- `A/S` border cases
- relevance border cases

Those packs are the right place for:
- sub-agent rubric probes
- API-assisted rubric probes
- not for IRR claims

## Recommendation

Treat the first classifier-upgrade cycle as:
- primarily an `Actionable` vs `Speculative` diagnosis pass
- secondarily a relevance-boundary cleanup pass

That is a more evidence-based starting point than assuming the whole problem is
uniformly distributed across all three classes.

## Bottom line

We already know enough to focus the next classifier lane:
- the relevance gate is comparatively stronger
- the `A/S` boundary is where the most meaningful instability remains
- the first audit pack should be built around that fact
