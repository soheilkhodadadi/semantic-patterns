# AI-Washing Track A Held-out V3 Rebuild Workflow V1

## Purpose

This note records the current rebuilt primary benchmark lane for the revised
rubric.

`held_out_v3` replaces the missing `held_out_v2` freeze as the working
publication-grade benchmark rebuild path.

## Why `held_out_v3`

The older frozen benchmark lane is not trustworthy as a live control surface:
- the frozen `held_out_v2` CSV is missing from the repo
- older benchmark labels were tied to an older rubric posture
- the revised boundary rubric is materially sharper now

So the honest posture is:
- keep `held_out_v2` as historical evidence only
- rebuild the current publication benchmark as `held_out_v3`

## Current file flow

Recovery source:
- `data/validation/recovery_sources/held_out_sentences_v2_review_sheet_10k_only_clean_prelabeled_recovered.csv`

Prepared outputs:
- `data/validation/held_out_v3/held_out_sentences_v3_candidate_pool.csv`
- `data/validation/held_out_v3/held_out_sentences_v3_review_sheet.csv`
- `data/validation/held_out_v3/held_out_sentences_v3_review_slice40.csv`

Runtime reports:
- `reports/final/ai_washing_heldout_v3_preparation_v1.json`
- `reports/final/ai_washing_heldout_v3_assistive_prelabel_progress_v1.json`
- `reports/final/ai_washing_heldout_v3_assistive_prelabel_dry_run_v1.json`
- `reports/final/ai_washing_heldout_v3_freeze_v1.json`

Future frozen benchmark:
- `data/validation/held_out_v3/held_out_sentences_v3.csv`

## Current status

Preparation status:
- rows before exclusions: `180`
- excluded invalid rows: `3`
- rows after exclusions: `177`
- first review slice: `40`

Assistive status:
- dedicated policy exists:
  - `director/config/api_assistive_policy_heldout_v3.yaml`
- dry-run passed
- live run has not been executed in this shell because `OPENAI_API_KEY` is not
  currently present

Freeze status:
- current status: `pending_review`
- rows pending review: `177`

## Design choices

### Historical context is preserved, not reused blindly

The recovered source had historical:
- `candidate_label`
- `assistive_*`

Those values are preserved under `legacy_*` columns in the `held_out_v3`
candidate pool.

Reason:
- they are useful context
- but they should not silently act as the live current-rubric assistive labels

### Current review fields start blank

The active `held_out_v3` review sheet has blank:
- `label`
- `review_note`
- `assistive_*`

Reason:
- live current-rubric assistive prelabels should be generated explicitly
- final frozen labels should remain human-verified

## Practical next steps

1. run live API assistive prelabels on `held_out_v3` when `OPENAI_API_KEY` is
   available
2. review and correct the `177` rows
3. freeze `held_out_v3`
4. use it as the primary benchmark for local layered-model reruns

## Bottom line

The benchmark rebuild lane is no longer abstract.

It now exists as a concrete repo-local structure with:
- a normalized candidate pool
- an active review sheet
- a bounded slice
- a freeze authority

That is enough to move from recovery into execution.
