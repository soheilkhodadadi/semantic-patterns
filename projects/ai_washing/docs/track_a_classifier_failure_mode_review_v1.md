# AI-Washing Track A Classifier Failure-Mode Review V1

## Purpose

This note is the first actual review pass over the `34`-row A/S audit pack.
Its job is to move us from a general statement that the `Actionable` /
`Speculative` boundary is weak to a more practical view of *which* boundary
cases are driving that weakness.

## Tagged audit artifacts

Working artifacts:
- `reports/final/ai_washing_classifier_as_boundary_audit_pack_tagged_v1.csv`
- `reports/final/ai_washing_classifier_rubric_probe_slice_v1.csv`

Source pack:
- `reports/final/ai_washing_classifier_as_boundary_audit_pack_v1.csv`

## First-pass failure-mode split

Current tagged counts across the `34` A/S audit rows:
- `future_intent_or_expectation`: `9`
- `in_progress_build_or_integrate`: `6`
- `risk_or_competition_reference`: `6`
- `current_capability_or_enabled_use`: `5`
- `generic_metric_or_tooling_reference`: `5`
- `acquisition_or_exposure_reference`: `2`
- `current_capability_or_product_packaging`: `1`

## What these categories are telling us

### 1. The biggest confusion is not random

Most of the mistakes are concentrated in a small set of recurring discourse
patterns:
- future intention vs present capability
- investment/build/integration language vs already-deployed use
- risk/competition/dependency references where AI is context, not evidence of
  current operational capability
- generic algorithm/model/tooling references where AI is real, but the sentence
  is not really making a commercialization or deployment claim

That is encouraging. It means the problem is structured enough to attack.

### 2. Rubric clarity matters more than threshold tuning right now

A lot of these rows are not “barely wrong because the probability was a little
off.” They are conceptually unstable because the rubric boundary itself needs to
say more clearly what counts as:
- actionable current use
- implementation in progress
- future-oriented intent
- generic AI context without a real operational claim

That suggests probability tuning alone is unlikely to be the first best move.

### 3. Training-set cleanup still matters, but after the boundary is clarified

Once the rubric is tightened, we should expand or clean the training material in
exactly these boundary categories. But doing that before the rule set is clearer
would risk adding more inconsistent labels.

## Recommended first probe slice

The first review slice should be small but deliberately mixed. The current
`16`-row probe slice does that by including:
- strong current-capability examples
- in-progress integration examples
- clean future-intent examples
- risk/competition references
- generic metric/tooling references
- one acquisition/ownership reference

That is a better calibration set than a random sample because it forces the
rubric to answer the main boundary questions directly.

## Recommendation

Recommended order for the next classifier-upgrade step:
1. rubric rewrite / boundary clarification first
2. then targeted training-set cleanup or expansion using the clarified rubric
3. only then probability tuning or threshold tuning

Why:
- the evidence points to repeated conceptual boundary problems
- those are usually upstream of threshold issues
- tuning probabilities before clarifying the labels would likely improve the
  metric less than we want and leave the core ambiguity in place

## Bottom line

The next classifier move should start with a clearer boundary definition, not a
blind model tweak. The A/S audit pack is telling us that the main issue is how
we distinguish current deployed capability from future intent, in-progress build
language, risk references, and generic model/tooling mentions.
