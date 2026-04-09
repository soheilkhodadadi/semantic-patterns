# Track A Selective-Defer Results V1

## Purpose

Record the first full selective-defer benchmark cycle after the layered local
model benchmark.

This note answers three questions:
1. does a bounded API-A defer layer clear the minimum gate?
2. what is the best practical operating point?
3. does a second stronger API layer currently add value?

## Base setup

Local base model:
- `layered_binary_relevance_logreg_as_v1`

Local logic:
1. use `binary_relevance_then_as_v1` for `Irrelevant` vs `Non-Irrelevant`
2. use `mpnet_logreg_prelim_v1` to resolve `Actionable` vs `Speculative`
3. combine them into a three-class local prediction

Deferred API lane:
- API A: `gpt-5-mini`
- API A labels come from the reviewed benchmark review sheets
- API A is assistive only and is never treated as canonical label truth

Primary benchmark inputs:
- `data/validation/held_out_v3/held_out_sentences_v3_review_sheet_labelled.csv`
- `reports/evaluation/selective_defer_heldout_v3_v1.json`
- `reports/evaluation/selective_defer_heldout_v3_confidence_sweep_v1.csv`

Secondary benchmark inputs:
- `data/validation/irr_boundary_benchmark_v1_review_sheet_scored.csv`
- `reports/evaluation/selective_defer_irr_boundary_v1.json`
- `reports/evaluation/selective_defer_irr_boundary_confidence_sweep_v1.csv`

## Fixed-policy simulation results

### `held_out_v3`

Local only:
- accuracy: `0.6893`
- macro F1: `0.6371`
- binary relevance accuracy: `0.7853`
- conditional A/S accuracy: `0.7778`

Best fixed deployable policy by accuracy:
- `api_a_conf_or_margin`
- accuracy: `0.9266`
- macro F1: `0.9167`
- binary relevance accuracy: `0.9435`
- conditional A/S accuracy: `0.9444`
- deferred rows: `77`
- deferred rate: `0.4350`

Interpretation:
- the defer lane is clearly useful
- but the best fixed rule is too expensive as the default operating posture

### `irr_boundary_benchmark`

Local only:
- accuracy: `0.8083`
- macro F1: `0.8043`
- binary relevance accuracy: `0.8750`
- conditional A/S accuracy: `0.8714`

Best fixed deployable policy by accuracy:
- `api_a_low_as_margin_015`
- accuracy: `0.8250`
- macro F1: `0.8216`
- binary relevance accuracy: `0.8750`
- conditional A/S accuracy: `0.9000`
- deferred rows: `10`
- deferred rate: `0.0833`

Interpretation:
- the IRR surface is already much stronger locally
- a very light defer layer is enough to improve it further

## Confidence-sweep operating points

The fixed rules were useful diagnostics, but the confidence sweep is the
actual operational decision surface.

### Unified low-cost operating point

Use:
- defer when `local_confidence < 0.49`

Results on `held_out_v3`:
- accuracy: `0.8079`
- macro F1: `0.7755`
- binary relevance accuracy: `0.8757`
- conditional A/S accuracy: `0.8333`
- deferred rows: `34`
- deferred rate: `0.1921`

Results on `irr_boundary_benchmark`:
- accuracy: `0.8250`
- macro F1: `0.8215`
- binary relevance accuracy: `0.8750`
- conditional A/S accuracy: `0.9000`
- deferred rows: `9`
- deferred rate: `0.0750`

Interpretation:
- this is the first unified threshold that clears the minimum gate on both
  reviewed benchmark surfaces
- it does so at a materially lower defer rate than the max-accuracy fixed rule

### Higher-accuracy operating point

Use:
- defer when `local_confidence < 0.54`

Results on `held_out_v3`:
- accuracy: `0.8644`
- macro F1: `0.8333`
- binary relevance accuracy: `0.9153`
- conditional A/S accuracy: `0.8667`
- deferred rows: `52`
- deferred rate: `0.2938`

Results on `irr_boundary_benchmark`:
- accuracy: `0.8417`
- macro F1: `0.8362`
- binary relevance accuracy: `0.8917`
- conditional A/S accuracy: `0.9143`
- deferred rows: `18`
- deferred rate: `0.1500`

Interpretation:
- this is a stronger accuracy posture on both surfaces
- but it materially increases API dependence

## API-A quality

Observed direct API-A score on the adjudicated IRR boundary sheet:
- accuracy: `0.8083`
- macro F1: `0.8032`
- binary relevance accuracy: `0.8750`
- conditional A/S accuracy: `0.8429`

Interpretation:
- API A is not perfect
- but it is strong enough on hard rows to make the defer architecture useful
- this is exactly why selective defer is the right design, not API-only

## API-B probe

Two bounded `gpt-5` probes were run on the disagreement lane.

First attempt:
- loose JSON prompt
- failed due malformed / incomplete JSON response

Second attempt:
- strict schema
- higher output budget
- clean 5-row disagreement smoke completed

Observed 5-row disagreement smoke:
- local model: `0 / 5`
- API A (`gpt-5-mini`): `5 / 5`
- API B (`gpt-5` high-output): `4 / 5`

Interpretation:
- API B is now serializing correctly under the higher-output strict-schema
  posture
- but it did not improve over API A on the bounded disagreement probe
- there is no current evidence that majority arbitration with API B improves
  the selected deferred lane

## Decision

The selective-defer lane is now validated.

Promote as the current best automated publication candidate:
- local layered base model
- one deferred API-A lane
- no human intervention in the live path

Recommended main operating point:
- `local_confidence < 0.49`

Reason:
- clears the minimum gate on both reviewed benchmark surfaces
- keeps defer rate materially lower than the max-accuracy posture
- is simpler and cheaper to defend operationally

Recommended robustness operating point:
- `local_confidence < 0.54`

Reason:
- stronger accuracy on both surfaces
- useful as a higher-API-use sensitivity run

Do not promote API B yet.

Reason:
- bounded evidence does not show incremental value over API A
- the extra layer adds complexity without demonstrated gain

## Next step

Use the selected selective-defer posture as the benchmark backdrop for the next
human-reliability phase:
1. review the revised IRR second-rater pack
2. send the revised pack under the tightened rubric
3. compute new IRR against the selected automated posture
