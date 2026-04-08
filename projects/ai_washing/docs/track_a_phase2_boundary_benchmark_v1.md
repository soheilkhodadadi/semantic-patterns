# AI-Washing Track A Phase 2 Boundary Benchmark V1

## Purpose

This note records the larger reviewed boundary-pack benchmark that follows the
fixed `16`-row Phase 1 slice.

The goal is to decide whether Variant A and Variant B still converge once the
benchmark surface includes more difficult rows from the full `34`-row A/S audit
pack.

## Reviewed boundary pack

Reviewed asset:
- `reports/final/ai_washing_classifier_boundary_review_pack_v1.csv`

Blinded asset:
- `reports/final/ai_washing_classifier_boundary_review_pack_blinded_v1.csv`

Summary:
- `reports/final/ai_washing_classifier_boundary_review_pack_v1.json`

Label mix:
- `Actionable`: `9`
- `Speculative`: `16`
- `Irrelevant`: `9`

## Sanity check on the new rows

For the `18` rows added beyond the original fixed probe slice, an independent
blind pass agreed on `15 / 18`.

The remaining disagreement rows are the right ones to keep in the pack:
- continuing enhancement of already-existing ML models
- entering AI-related sectors vs actually using AI
- evolving methodologies that may incorporate ML

Those are exactly the boundary cases that should determine whether the stricter
posture adds value.

## Variant files

Variant A labels:
- `reports/final/ai_washing_classifier_boundary_pack_variant_a_labels_v1.csv`

Variant B labels:
- `reports/final/ai_washing_classifier_boundary_pack_variant_b_labels_v1.csv`

Variant A score:
- `reports/final/ai_washing_classifier_boundary_pack_variant_a_score_v1.json`

Variant B score:
- `reports/final/ai_washing_classifier_boundary_pack_variant_b_score_v1.json`

## Interpretation frame

What we want to learn here is narrow:
- does Variant B improve boundary clarity in a way that the `16`-row slice
  could not detect?

Useful signals:
- Variant B is stricter on the known ambiguous rows without harming obvious
  current-capability rows
- disagreement is concentrated in understandable places
- the stricter current-business-claim posture does not just relabel too much as
  `Irrelevant`

## Decision rule

If Variant A and Variant B still collapse to nearly the same predictions on the
`34`-row pack, then:
- keep Variant A as the default revised rubric
- keep Variant B as a stress-test posture
- move on to retraining rather than spending more cycles splitting hairs in the
  rubric

If Variant B improves the pack meaningfully without obvious over-pruning, then:
- promote Variant B or its tie-breakers into the main rubric before retraining

## Execution result

Completed artifacts:
- `reports/final/ai_washing_classifier_boundary_pack_variant_a_labels_v1.csv`
- `reports/final/ai_washing_classifier_boundary_pack_variant_b_labels_v1.csv`
- `reports/final/ai_washing_classifier_boundary_pack_variant_a_score_v1.json`
- `reports/final/ai_washing_classifier_boundary_pack_variant_b_score_v1.json`

Observed result:
- Variant A (`variant_a_two_gate_v1`): `34 / 34`, accuracy `1.00`
- Variant B (`variant_b_strict_current_claim_v1`): `34 / 34`, accuracy `1.00`

## Interpretation

This is a clear outcome.

The larger reviewed pack still does not separate Variant A from Variant B.
That means the stricter current-business-claim posture is not producing a
meaningfully different reviewed boundary on the rows that matter most here.

So the current conclusion is:
- keep Variant A as the default revised rubric
- keep Variant B as a documented stress-test posture
- stop spending additional cycles trying to separate these two rubric variants
  before retraining

## What this means for the next step

The next likely gain is no longer in micro-adjusting the rubric variants.

It is in:
1. targeted training-set cleanup and expansion under the revised rubric
2. local-model retraining
3. held-out rerun under the revised benchmark posture

If the local rerun still stalls after that, then the next escalation is the
selective-defer hybrid design, not another round of minor rubric surgery.
