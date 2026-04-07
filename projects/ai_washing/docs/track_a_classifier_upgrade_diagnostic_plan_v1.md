# AI-Washing Track A Classifier Upgrade Diagnostic Plan V1

## Purpose

This note turns the current classifier-upgrade discussion into a concrete
diagnostic and redesign plan.

It is meant to answer:
- why the current classifier is not yet strong enough for the final paper
- what we should diagnose before retraining
- where sub-agents or API-assisted rubric probes are useful
- what should stay human-only

## Current status

### Current selected model

- selected runtime:
  - `binary_relevance_then_as_v1`
- latest published held-out metrics from the selected-model report:
  - accuracy: `0.7062`
  - macro F1: `0.6729`
  - conditional A/S accuracy: `0.7556`

### Current thresholds

- repo code currently encodes a publication-grade threshold of `0.80`
- Track A should treat `0.80` as the hard minimum gate
- `0.85` is a reasonable **stretch target** for the final paper if the rubric
  and training data support it

## Critical view

### What I agree with

1. The core problem is not just “train another model.”
   We still do not fully know whether the main failure source is:
   - rubric ambiguity
   - sentence-quality noise
   - label inconsistency
   - class imbalance
   - model design
   - thresholding

2. The `Irrelevant` vs `Relevant` boundary may be the biggest conceptual weak
   point.
   That is consistent with:
   - the current two-stage model design
   - the IRR structure already used in the project
   - the spot-check results on risk/compliance/generic-AI sentences

3. The A/S/I task should keep being treated as:
   - first: `Relevant` vs `Irrelevant`
   - second: `Actionable` vs `Speculative` conditional on relevance

That is likely cleaner than forcing all ambiguity through a flat three-way
framing.

### What I would not do

1. I would not use sub-agents or LLM/API outputs as a substitute for human IRR.
   They are useful diagnostics, not evidence.

2. I would not jump straight into relabeling hundreds of sentences before we run
   a smaller diagnostic loop.

3. I would not rerun the full final panel/regression/event-study stack using the
   current classifier and then “fix accuracy later.”

## Recommended diagnostic sequence

### B1. Failure audit on existing held-out and IRR assets

Review:
- held-out errors by class
- binary relevance misses
- conditional A/S misses
- disagreement concentration from the IRR diagnostic

Questions:
- Are most misses actually boundary failures at the relevance step?
- Are A/S misses concentrated in a smaller, more fixable subset?
- Are long or segmented sentences overrepresented among errors?

### B2. Rubric-stability probe on small samples

Use small random samples such as `10-20` sentences at a time and test:
- current rubric
- simplified relevance-first rubric
- stricter irrelevance exclusions
- sharper A vs S definitions

This is where sub-agents or API-assisted labeling can help.

Use them as:
- fast rubric stress tests
- cheap disagreement detectors
- not as the official second rater

Output:
- a short rubric-stability note each round
- concrete examples where instructions change the result

### B3. Human review pack redesign

Once the rubric is sharper:
- prelabel a review slice
- send a cleaner, better-specified sheet to the human second rater
- preserve the two-question structure:
  - `Relevant` vs `Irrelevant`
  - `Actionable` vs `Speculative` conditional on relevance

This should reduce wasted human passes compared with sending another ambiguous
large sheet too early.

### B4. Retraining candidate matrix

Only after B1-B3:
- rebuild or expand the adjudicated training slice
- compare candidate retraining paths
- revisit thresholds or probability calibration

Possible candidate families:
- improved two-stage classical baseline
- rubric-aware relabel + retrain
- confidence-threshold / abstention variants
- API-assisted prelabeling only as a helper for human review acceleration

## Suggested sub-agent / API role

Good use:
- classify tiny blinded samples under different rubric versions
- explain why a sentence was treated as irrelevant vs relevant
- surface sentences where two rubric variants disagree

Bad use:
- claiming that agent-agent agreement is IRR
- replacing the human adjudication lane

## Exit criteria for this planning lane

Before retraining or final reruns, we should have:
1. a written diagnosis of where the current `~70.6%` accuracy is failing
2. a revised relevance-first rubric or explicit confirmation that the current
   rubric is already sharp enough
3. a decision on the next human review pack design
4. a retraining candidate plan with evaluation gates
5. a target metric posture:
   - hard minimum: `>= 0.80`
   - stretch target: `~0.85` if feasible

## Bottom line

The current model is good enough to finish the `2025` data-refresh lane.
It is **not** good enough to silently become the final-paper classifier.

The right next move after the patent/panel rebuild is a deliberate
classifier-upgrade diagnostic lane, starting with failure audit and
rubric-stability probes rather than blind retraining.
