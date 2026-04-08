# AI-Washing Track A Classifier A/S Boundary Audit Pack V1

## Purpose

This note records the first compact audit pack for the classifier-upgrade lane.
It is deliberately focused on the `Actionable` / `Speculative` boundary, because
that is where both the held-out evaluation and the IRR results show the most
meaningful instability.

## Built artifact

- `reports/final/ai_washing_classifier_as_boundary_audit_pack_v1.csv`
- `reports/final/ai_washing_classifier_as_boundary_audit_pack_v1.json`

## Composition

The pack combines two sources:
1. IRR disagreement rows with transitions in `A->S` or `S->A`
2. held-out model misses where both the true and predicted labels are in
   `{Actionable, Speculative}`

Current counts:
- IRR A/S disagreement rows: `12`
- held-out A/S model misses: `22`
- combined audit-pack rows: `34`

## Why this is the right first pack

Current evidence already says:
- binary relevance is stronger than the full three-way headline
- human disagreement is concentrated in `A/S`
- model misses are also concentrated in `A/S`

So the next upgrade pass should begin with:
- rubric stability on the `A/S` boundary
- sentence-level inspection of long, clause-heavy, or commercialization-leaning
  cases
- only then a smaller revisit of `Relevant` vs `Irrelevant`

## Immediate next use

Use this pack to:
1. tag failure modes
2. build tiny rubric-probe slices
3. decide whether the next classifier improvement should focus on:
   - clearer rules
   - cleaner training examples
   - model/probability adjustments
   - or some combination of the three
