# AI-Washing Track A Deferred Classifier Design V1

## Purpose

This note evaluates a possible next-step architecture for the classifier lane:

- keep the local two-stage model as the primary engine
- defer only hard edge cases to a bounded external API lane

This is a serious design option, not just a convenience hack.

## What this idea is called

The closest technical names are:
- `learning to defer`
- `selective classification`
- `abstention`
- `deferred prediction`
- `classifier cascade`

In our specific case, the clearest description is:

`a two-stage local classifier with selective deferral on edge cases`

If the fallback is an API model, it is also fair to describe it as:

`a hybrid cascaded classifier with API escalation`

## Why this idea makes sense here

The current selected model already does two things reasonably well:
- binary relevance is fairly strong
- many easy A/S rows are not the problem

The failure audit suggests the hardest rows are concentrated in:
- mixed current vs future clauses
- investment / build / integrate language
- risk or competition context
- generic tooling vs real operating use

That is exactly the pattern where selective deferral can help.

We do not necessarily need a stronger model on **all** sentences.
We may only need help on the narrow tail where the local model is least stable.

## Recommended three-stage version

### Stage 1. Relevance gate

Use the local classifier to distinguish:
- `Irrelevant`
- `Non-Irrelevant`

### Stage 2. Local A/S decision

For rows that are not irrelevant, use the local A/S head to predict:
- `Actionable`
- `Speculative`

### Stage 3. Deferral on edge cases

Only defer rows that meet one or more hard-case triggers, such as:
- very small `Actionable` vs `Speculative` probability margin
- low top-class confidence
- conflict between model prediction and revised rubric heuristics
- mixed-clause sentence pattern flagged by rules
- known failure-mode categories from the audit pack

Fallback target:
- an API-only arbitration lane using more than one API call when needed

## What this is not

It is **not** a replacement for:
- a clear rubric
- proper held-out evaluation
- human IRR for benchmark construction

It is a way to:
- spend stronger-model capacity only where it matters
- preserve the local model as the default reusable lab asset
- keep the live classification path reproducible without manual tie-breaking

## Why this could be valuable beyond this paper

If this works, it becomes a reusable Semantic Lab pattern:
- local low-cost classifier handles easy/high-confidence cases
- stronger expert model handles ambiguity
- cost stays bounded
- accuracy can improve without abandoning the local pipeline

That would be useful well beyond AI-washing:
- greenwashing or ESG disclosure work
- ERI-style reliability tagging
- AllocationLab document or project scoring

## How to test this safely

Start small.

### Phase 1. Offline simulation on reviewed assets

Use:
- `held_out_v2`
- the fixed `16`-row A/S probe benchmark
- the `34`-row A/S audit pack

For each row:
1. run the local selected model
2. compute edge-case triggers:
   - top-class confidence
   - A/S margin
   - relevance probability
   - rule conflict
3. mark rows as:
   - auto-accept
   - defer

Then simulate a fallback label using:
- revised benchmark labels on the fixed slice
- optionally a stronger model on a very small sample

Output:
- coverage without deferral
- deferral rate
- hybrid accuracy
- hybrid A/S accuracy
- approximate cost per `100` sentences

### Phase 2. Tiny live API benchmark

Only after offline simulation looks promising:
- pick `10-30` deferred rows
- send them to a lighter API model under a fixed rubric prompt
- compare:
  - local model
  - API model
  - revised benchmark label

Then repeat on the same deferred rows with a stronger API model to estimate how
much extra gain the second-stage call is likely to buy.

### Phase 3. API arbitration design

If the deferred API lane looks promising, test this production posture on the
same fixed deferred slice:

1. local model produces a label
2. API `A` labels the deferred row under the fixed rubric using a cheaper,
   lighter model
3. if API `A` agrees with the local model:
   - accept that label
4. if API `A` disagrees:
   - call API `B` in isolation under the same rubric using a stronger model
5. final label is determined by majority agreement:
   - local + API `A`
   - or API `A` + API `B`
   - or local + API `B`

This keeps the lane:
- reproducible
- fully automated
- free of manual tie-breaking in the live classification path

The intended posture is:
- API `A` is the cheaper high-throughput check
- API `B` is the more expensive escalation only for real disagreements
- the live path never depends on human adjudication

### Phase 4. Decide posture

If the hybrid setup improves A/S accuracy materially at modest deferral rate,
then:
- keep local-only as the baseline
- add deferred hybrid as a robustness or upgrade lane

If it does not improve enough, then:
- do not complicate the pipeline yet

## Suggested first deferral triggers

Start simple.

Use any of:
- `abs(score_actionable - score_speculative) < 0.10`
- `max(score_actionable, score_speculative, score_irrelevant) < 0.60`
- model label conflicts with the revised rubric tie-breakers
- sentence falls into a known high-risk failure bucket:
  - `future_intent_or_expectation`
  - `in_progress_build_or_integrate`
  - `risk_or_competition_reference`

These thresholds should be treated as starting points, not final settings.

## Critical caution

The hybrid architecture only helps if:
- the deferral policy is selective
- the fallback model is actually better on the hard cases
- we measure the cost / coverage tradeoff honestly
- the arbitration logic stays reproducible and does not depend on ad hoc human
  intervention
- API `A` and API `B` are meaningfully different enough that the second call
  adds information rather than just repeating the same error pattern

If we defer too much, the local model stops mattering.
If we defer too little, the hybrid gain will be small.

So the real object to optimize is not just accuracy.
It is:
- accuracy
- deferral rate
- cost
- operational simplicity

## Bottom line

Yes, this is a real and promising direction.

The most precise description is:

`a selective-defer hybrid classifier, where the local two-stage model handles easy cases and a stronger expert model handles edge cases`

That is worth testing after the rubric benchmark, and it could become a very
useful reusable pattern for the lab.
