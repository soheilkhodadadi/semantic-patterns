# Track A Held-Out V4 And IRR V3 Results V1

## Purpose

Record the outcome of the adjudicated `IRR v2` cycle, the construction of
`held_out_v4`, the current hybrid-classifier tuning result on that benchmark,
and the creation of the next blinded `IRR v3` handoff pack.

## Inputs

Adjudication inputs:
- `data/labels/v2/irr_boundary_revised_v2_adjudication_sheet_filled.xlsx`
- `data/labels/v2/adjudication_boundary_revised_v2_final.parquet`
- `reports/labels/irr_boundary_revised_v2_final_report.json`
- `reports/labels/irr_boundary_revised_v2_final_status.json`

Held-out benchmark assets:
- `data/validation/held_out_v4/held_out_sentences_v4.csv`
- `data/validation/held_out_v4/held_out_sentences_v4_input.csv`
- `reports/final/ai_washing_heldout_v4_build_v1.json`

Classifier evaluation assets:
- `reports/evaluation/model_benchmark_matrix_heldout_v4_v1.json`
- `reports/evaluation/heldout_v4_selective_defer_conf49_v1.json`
- `reports/evaluation/heldout_v4_selective_defer_conf54_v1.json`
- `reports/evaluation/selective_defer_heldout_v4_gpt5mini_high_output_v1.json`
- `reports/evaluation/selective_defer_heldout_v4_api_a_api_b_v1.json`
- `reports/evaluation/selective_defer_heldout_v4_hybrid_api_upgrade_v2.json`

Next IRR pack assets:
- `data/labels/v2/labels_master_boundary_revised_v1_excluding_heldout_v4.parquet`
- `reports/labels/irr_subset_boundary_revised_v3_sampling_report.json`

## Finalized adjudication result

`IRR v2` adjudication is now complete.

Headline:
- rows reviewed: `120`
- disagreements resolved by third adjudicator: `27`
- final kappa: `0.6625`
- gate result: `fail`

Interpretation:
- the revised rubric produced a cleaner benchmark, but it did not clear the
  human-human reliability gate
- the adjudicated set is therefore useful as a benchmark surface, but not as
  evidence that the human IRR problem is solved

## Held-out V4

`held_out_v4` was built from the finalized adjudicated `IRR v2` pack.

Counts:
- rows: `120`
- `Actionable`: `43`
- `Speculative`: `31`
- `Irrelevant`: `46`
- rows with review note: `120`

Important caveat:
- `held_out_v4` fully overlaps the current training backbone
- overlap against both `labels_master.parquet` and
  `labels_master_boundary_revised_v1.parquet`: `120` unique rows

Meaning:
- `held_out_v4` is valid as an adjudicated development benchmark
- it is not an independent generalization benchmark for the current local model
  artifacts

## Local model result on held_out_v4

Best local candidate:
- `layered_binary_relevance_logreg_as_v1`

Development-surface score:
- accuracy: `0.7833`
- macro F1: `0.7709`
- binary relevance accuracy: `0.9000`
- conditional A/S accuracy: `0.7838`

Read:
- the layered local design remains the right local base
- the local-only stack is still below the desired practical ceiling

## Hybrid selective-defer result on held_out_v4

Published operating points:
- `conf49`: `reports/evaluation/heldout_v4_selective_defer_conf49_v1.json`
- `conf54`: `reports/evaluation/heldout_v4_selective_defer_conf54_v1.json`

Scores:
- `conf49`
  - accuracy: `0.8167`
  - macro F1: `0.8039`
  - conditional A/S accuracy: `0.8784`
- `conf54`
  - accuracy: `0.8333`
  - macro F1: `0.8212`
  - conditional A/S accuracy: `0.8514`

Read:
- the hybrid design clearly improves on the local base
- more defer helps on this development surface
- but the first published operating points still leave some recoverable error

## API-only and offline defer sweep

API-only baseline:
- model/policy: `gpt-5-mini` high-output policy
- source: `reports/final/ai_washing_heldout_v4_api_only_gpt5mini_high_output_score_v1.json`
- raw agreement: `97 / 120`
- raw accuracy equivalent: `0.8083`

This means API-only `gpt-5-mini` is not strong enough to replace the hybrid by
itself.

However, using those same API labels in an offline defer sweep yields a better
deployable policy:
- source: `reports/evaluation/selective_defer_heldout_v4_gpt5mini_high_output_v1.json`
- best deployable policy: `api_a_conf_or_margin`
- accuracy: `0.8500`
- macro F1: `0.8347`
- conditional A/S accuracy: `0.8649`
- deferred rows: `40 / 120`

This is the first operating point to hit the desired `85%` accuracy threshold on
the adjudicated development surface.

## API-B probe

I then tested the user's proposed stronger second API on only the `40` rows
used by the best deployable defer policy.

Setup:
- API A: existing `gpt-5-mini` high-output labels
- API B: `gpt-5` with rubric `V2`
- API B scope: only the `40` deferred rows

Findings:
- replacing API A on those `40` rows did not improve overall accuracy above
  `0.8500`
- majority voting among local, API A, and API B was slightly worse:
  - accuracy: `0.8417`
  - macro F1: `0.8288`

Interpretation:
- the second API is not useless
- but in the current bounded setup it does not beat the simpler single-API
  defer posture
- the best deployable policy remains:
  - local layered base
  - API A only
  - defer on low confidence or narrow A/S margin

## Rubric update

New prompt/rubric note:
- [track_a_as_rubric_rewrite_v2.md](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/projects/ai_washing/docs/track_a_as_rubric_rewrite_v2.md)

`V2` adds adjudication-derived tie-breakers for:
- client future-use claims
- market trend / demand statements
- existing platform plus expansion language
- completed acquisition of AI assets
- biography/expertise references

This note is the correct rubric to send with the next IRR pack.

## IRR v3 pack

A fresh blinded `IRR v3` pack has now been generated from the revised label
backbone after excluding every `held_out_v4` sentence.

Artifacts:
- `data/labels/v2/irr_subset_boundary_revised_v3.parquet`
- `data/labels/v2/irr_subset_boundary_revised_v3_master.csv`
- `data/labels/v2/irr_subset_boundary_revised_v3_rater2_blinded.csv`
- `data/labels/v2/irr_subset_boundary_revised_v3_rater2_blinded.xlsx`
- `reports/labels/irr_subset_boundary_revised_v3_sampling_report.json`
- `reports/labels/irr_subset_boundary_revised_v3_attestation.json`

Pack summary:
- `120` rows
- `40 / 40 / 40` class-balanced
- `120` unique firms
- excludes the full `held_out_v4` adjudicated benchmark surface

## Current recommendation

Use the following posture:

1. Treat `held_out_v4` as the adjudicated development benchmark, not as the
   final publication-grade held-out surface.
2. Treat the best current deployable classifier as:
   - layered local base
   - API A defer on `low_confidence OR narrow_A/S_margin`
   - empirical dev-surface score: `0.8500` accuracy
3. Send the new blinded `IRR v3` workbook with rubric `V2` to the second rater.
4. Do not rebuild the final paper panel on the new classifier until the `IRR v3`
   return is scored.

## What this means for the panel lane

It is reasonable to keep building downstream code and even shadow outputs using
the current hybrid winner.

It is not yet reasonable to claim the classifier lane is finished for the
publication panel until `IRR v3` comes back and is rescored.
