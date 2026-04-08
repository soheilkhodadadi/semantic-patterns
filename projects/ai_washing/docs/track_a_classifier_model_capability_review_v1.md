# AI-Washing Track A Classifier Model Capability Review V1

## Purpose

This note separates two questions that can easily get conflated:

1. `Is the rubric clear enough?`
2. `Is the current model architecture capable of learning that clearer rubric?`

The current answer is:
- the rubric needed tightening
- the current model still looks capable enough to justify another serious
  benchmark cycle before we escalate to an API-only robustness lane

## Current baseline

Current selected model:
- `binary_relevance_then_as_v1`

Current held-out benchmark:
- `held_out_v2`

Published metrics:
- overall accuracy: `0.7062`
- macro F1: `0.6729`
- binary relevance accuracy: `0.8192`
- conditional `Actionable` / `Speculative` accuracy: `0.7556`

## What the current model actually is

The current selected classifier is not an LLM and not a clause-level reasoning
system.

It is:
1. MPNet sentence embeddings
2. binary logistic regression for:
   - `Irrelevant`
   - `Non-Irrelevant`
3. conditional binary logistic regression for:
   - `Actionable`
   - `Speculative`

This matters because the model can only learn distinctions that are visible in:
- sentence-level embedding geometry
- training labels
- the two-stage decomposition

It does **not** explicitly reason over:
- clause hierarchy
- dominant vs trailing clauses
- modal scope
- acquisition/risk context as discourse structure

So if the labels are noisy or the rubric is vague, the model will not rescue us
by “thinking harder.”

## Strengths of the current architecture

### 1. The relevance split is already reasonably strong

Binary relevance accuracy above `0.81` suggests the architecture is not failing
everywhere. It can separate a large share of:
- true AI business/operational claims
from:
- clearly irrelevant material

That is encouraging because it means we are not rebuilding from zero.

### 2. The A/S subgroup is weak but not hopeless

Conditional `Actionable` / `Speculative` accuracy around `0.756` is below the
 final target, but it is not random.

That level is consistent with:
- a model that is seeing real signal
- but is being limited by boundary ambiguity and training examples

### 3. The two-stage design is conceptually aligned with the task

The project logic already treats the problem as:
1. `Relevant` vs `Irrelevant`
2. `Actionable` vs `Speculative` conditional on relevance

That is still the right basic structure.

## Limitations of the current architecture

### 1. Sentence-level embeddings are blunt on mixed-clause sentences

The hard cases in the probe slice are exactly the kinds of sentences that
embedding + logistic models struggle with:
- current capability plus trailing risk clause
- strategic priority plus example use cases
- implementation in progress plus implied future benefit

These cases require a strong label rule because the model itself is not parsing
the sentence at a deep discourse level.

### 2. The model is very sensitive to rubric instability

If humans disagree about whether a row is:
- `Irrelevant` vs `Speculative`
- or `Speculative` vs `Actionable`

then the training signal for a simple supervised classifier becomes noisy very
quickly.

That means:
- rubric cleanup has unusually high leverage here

### 3. The architecture will probably not recover from vague labels by tuning alone

Probability tuning or threshold tuning may help at the margin.
It will not solve:
- boundary ambiguity
- mislabeled training rows
- missing subtypes in the reviewed sample

## My current judgment

The current architecture still deserves another real attempt.

Why:
- binary relevance is already strong enough to suggest the pipeline is viable
- A/S conditional performance is weak but not broken
- the failure audit shows structured conceptual error, not random noise

So the next best move is **not** to abandon the local model immediately.

The next best move is:
1. sharpen the rubric
2. benchmark on the fixed A/S slice
3. clean or expand training rows in the exact failure categories
4. retrain and re-evaluate

## When to escalate to an API robustness lane

We should open an API-based robustness lane if one of these becomes true:

1. revised-rubric retraining still cannot lift overall held-out accuracy above
   `0.80`
2. the revised-rubric retraining improves overall accuracy only by harming
   relevance or another class badly
3. repeated benchmark cycles show that the same mixed-clause A/S rows remain
   unstable even after cleaner labels
4. the second human-review pass confirms that the refined rubric is clear, but
   the local model still underperforms badly

If that happens, the right posture is:
- keep the local model as an important reusable lab asset
- add an API-driven robustness classifier for the paper package

That would be a supplement, not an admission that the local work was wasted.

## Recommended next sequence

1. finish the revised-rubric probe benchmark on the fixed `16`-row slice
2. create a slightly larger reviewed benchmark pack for the boundary cases
3. retrain the local two-stage model on revised labels
4. re-run:
   - overall held-out accuracy
   - binary relevance accuracy
   - conditional A/S accuracy
5. only then decide whether the API robustness lane is necessary

## Bottom line

The current model is limited, but not clearly exhausted.

Its main weakness is not “the model is too simple to ever work.”
Its main weakness is that a simple sentence-level model cannot reliably learn a
boundary that humans have not yet defined sharply enough.

That means rubric cleanup and targeted retraining still have a real chance to
get us meaningfully closer to publication grade.
