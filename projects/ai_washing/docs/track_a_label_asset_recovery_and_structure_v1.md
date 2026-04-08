# AI-Washing Track A Label Asset Recovery And Structure V1

## Purpose

This note records what survived the repo restructure in the label lane, what is
missing, what can be recovered, and how the classifier assets should now be
treated.

It is the live control note for:
- training data
- validation data
- IRR / adjudication data
- primary held-out benchmark rebuild
- layered-classifier preparation

## Bottom line

The repo-side label lane is in better shape than it looked at first.

The important assets that survived cleanly are:
- the canonical label backbone
- the revised-rubric label backbone
- the train / validation split registry
- the full IRR chain
- the machine-readable adjudication result

The important asset that is still missing is:
- the frozen `held_out_v2` benchmark CSV

But the best rebuild source for that benchmark has now been recovered and staged
locally in the repo:
- `data/validation/recovery_sources/held_out_sentences_v2_review_sheet_10k_only_clean_prelabeled_recovered.csv`

So this is now a controlled benchmark-rebuild problem, not a blind recovery
problem.

## Selected playbook

Curated playbook used:
- `director/playbooks/prompt_boundary_benchmark.yaml`

Why:
- the current classifier weakness is concentrated on the
  `Actionable` / `Speculative` boundary
- we already have a fixed reviewed slice and a small reviewed benchmark pack
- prompt / rubric boundary work is cheaper and lower-blast-radius than broad
  model or extraction churn

No curated playbook currently covers label-asset recovery or benchmark
reconstruction directly.

So the asset-recovery posture in this note is intentionally project-local until
it is stable enough to promote into the playbook library.

## Canonical assets that survived

### Training backbone

Current repo-local canonical training assets:
- `data/labels/v1/labels_master.parquet`
- `data/labels/v1/labels_master_review.csv`
- `data/labels/v1/labels_master_boundary_revised_v1.parquet`
- `data/labels/v1/labels_master_boundary_revised_v1_review.csv`

Current status:
- `labels_master.parquet`: `551` rows
- `labels_master_boundary_revised_v1.parquet`: `551` rows
- revised-rubric changes relative to the original backbone: `8` rows

Label counts:
- original backbone:
  - `Irrelevant`: `344`
  - `Actionable`: `108`
  - `Speculative`: `99`
- revised backbone:
  - `Irrelevant`: `347`
  - `Actionable`: `106`
  - `Speculative`: `98`

Interpretation:
- the label backbone is intact
- the revised-rubric backbone already exists
- we are not starting retraining cleanup from scratch

### Train / validation split

Current split source:
- `data/metadata/splits/split_registry_v1.csv`

Counts:
- total: `551`
- `train`: `440`
- `validation`: `111`

Important caution:
- this split registry was frozen from the older `labels_master` posture
- if `labels_master_boundary_revised_v1.parquet` becomes the canonical
  training backbone, the split registry should be refrozen deliberately rather
  than reused by inertia

### IRR and adjudication chain

Current IRR chain:
- `data/labels/v1/irr_subset.parquet`
- `data/labels/v1/irr_subset_master.csv`
- `data/labels/v1/irr_subset_rater2_completed.xlsx`
- `data/labels/v1/irr_adjudication_completed.xlsx`
- `data/labels/v1/adjudication.parquet`
- `data/validation/irr_boundary_benchmark_v1.csv`

Counts:
- IRR sample: `120`
- completed second-rater rows: `120`
- adjudicated disagreement rows: `26`
- final adjudication rows: `120`
- resolution split:
  - `94` agreement
  - `26` third-adjudicator

Important quality signal:
- reported human-human kappa in `reports/labels/irr_report.json`: `0.675`
- configured gate there: `0.7`

Interpretation:
- the IRR chain is recoverable and usable
- but it is evidence of a boundary problem, not evidence that the labeling lane
  was already publication-grade

## Missing historical assets

The old registry files in `reports/validation/` still reference assets that are
not present in the current checkout:
- `data/validation/held_out_sentences.csv`
- `data/validation/held_out_sentences_v2.csv`
- `data/validation/CollectedAiSentencesClassifiedCleaned.csv`
- `data/validation/hand_labeled_ai_sentences_with_embeddings_revised.csv`

Interpretation:
- the old registry files remain useful as historical evidence
- they are not the live source of truth for the current repo tree

This is why `reports/final/ai_washing_validation_asset_registry_v3.json` now
exists:
- it records the live current asset map instead of relying on stale historical
  registry paths

## Recovered primary held-out benchmark source

Recovered file:
- `data/validation/recovery_sources/held_out_sentences_v2_review_sheet_10k_only_clean_prelabeled_recovered.csv`

Status:
- recovered from external storage and staged into the repo
- rows before exclusions: `180`
- invalid rows listed in the old freeze report: `3`
- effective benchmark-rebuild pool after exclusions: `177`

Important caveat:
- the recovered file is a candidate review sheet only
- its final `label` column is blank
- so it is a benchmark rebuild source, not a frozen benchmark

Why it is still valuable:
- it has very low overlap with the current training backbone
- it preserves the sampling intent of the missing benchmark lane
- it gives us a controlled way to rebuild a publication-grade benchmark under
  the revised rubric rather than guessing

## Filled tranche files and merge behavior

Verified tranche inputs that fed the label backbone:
- `data/labels/v1/labeling_batch_v1_filled_v2_4.csv`
- `data/labels/v1/labeling_batch_v2_filled.csv`
- `data/labels/v1/labeling_batch_v3_filled.csv`

Merge summary from `reports/labels/label_expansion_summary.json`:
- total tranche rows: `560`
- canonical labeled rows retained: `551`
- excluded:
  - `3` blank-label rows
  - `6` held-out overlaps

Important implication:
- tranche 1 contributes `231` rows to the canonical backbone, not `240`
- that is explained by merge control, not silent row loss

## Manual workflow residue

`data/labels/v1` contains a lot of useful audit residue, but it should not be
treated as clean pipeline input by default.

Manual residue includes:
- `*_prelabeled*`
- `*_slice40*`
- `*_calibration*`
- `*_reextracted*`
- `*.bak*`
- `.xlsx` handoff copies
- `.numbers` copies

Known duplicate examples:
- `labeling_batch_v2_prelabeled_Verified.csv` duplicates
  `labeling_batch_v2_filled.csv`
- `labeling_batch_v3_prelabeled_filled.csv` duplicates
  `labeling_batch_v3_filled.csv`
- `irr_adjudication_completed.xlsx.xlsx` duplicates
  `irr_adjudication_completed.xlsx`

Interpretation:
- the folder is not corrupt
- it is just carrying too much manual-process residue
- the right response is role clarity, not panic deletion

## Spot-check result

I manually spot-checked small stratified samples from:
- `labels_master_boundary_revised_v1.parquet`
- `adjudication.parquet`

Result:
- `Actionable` examples looked like present or already-deployed firm use
- `Speculative` examples looked future-oriented, investment-oriented, or
  contingent
- `Irrelevant` examples looked like risk, market, or contextual AI mention
  without a concrete current firm capability claim

This does not prove publication-grade accuracy.

But it does show that the surviving repo-local labels are directionally
coherent enough to support the next structured classifier pass.

## Proposed safe structure from here

### Training

Use:
- `data/labels/v1/labels_master_boundary_revised_v1.parquet`

Treat as:
- current local training backbone under the revised boundary rubric

### Validation

Use:
- `data/metadata/splits/split_registry_v1.csv`

Treat as:
- current frozen train / validation split registry

Important caveat:
- refreeze if the revised backbone is promoted as canonical rather than used
  only for controlled tranche experiments

### IRR / hard-case benchmark

Use:
- `data/labels/v1/adjudication.parquet`
- `data/validation/irr_boundary_benchmark_v1.csv`

Treat as:
- boundary benchmark only
- not the sole publication benchmark

### Primary publication benchmark

Use:
- `data/validation/recovery_sources/held_out_sentences_v2_review_sheet_10k_only_clean_prelabeled_recovered.csv`

Treat as:
- benchmark rebuild source only

Required action before use:
- review and label under the revised rubric
- freeze the resulting benchmark deliberately
- keep it benchmark-only

## Recommended execution order

1. Freeze the live asset map.
   - done via `reports/validation/validation_asset_registry_v3.json`
2. Preserve the recovered held-out v2 candidate pack in the repo.
   - done via `data/validation/recovery_sources/..._recovered.csv`
3. Rebuild the primary held-out benchmark under the revised rubric.
4. Keep that rebuilt benchmark separate from training.
5. Build a larger reviewed A/S training tranche from the clean corpus.
6. Evaluate both local candidates again:
   - binary relevance then A/S
   - MPNet logreg
7. Promote the layered local design:
   - binary relevance gate
   - MPNet A/S resolver
   - defer only true conflict or low-confidence cases
8. Only then open the API selective-defer lane if local gains still stall.

## Practical implication for the layered model

The data picture is now good enough to support the layered design.

What was missing was not “all label data.”

What was missing was:
- a live trustworthy asset map
- a repo-local recovery copy of the missing held-out v2 source
- clear separation between:
  - training backbone
  - split registry
  - IRR benchmark
  - publication benchmark rebuild source

Those separations now exist.

## Bottom line

The label lane is recoverable and usable.

The next honest move is:
1. rebuild and freeze the primary held-out benchmark from the recovered v2
   review sheet
2. keep it benchmark-only
3. expand the reviewed A/S training tranche separately
4. then rerun the local layered design against the rebuilt benchmark

## Current execution status

The rebuild lane is now initialized as `held_out_v3`.

Current repo-local assets:
- `data/validation/held_out_v3/held_out_sentences_v3_candidate_pool.csv`
- `data/validation/held_out_v3/held_out_sentences_v3_review_sheet.csv`
- `data/validation/held_out_v3/held_out_sentences_v3_review_slice40.csv`
- `reports/final/ai_washing_heldout_v3_preparation_v1.json`
- `reports/final/ai_washing_heldout_v3_assistive_prelabel_progress_v1.json`
- `reports/final/ai_washing_heldout_v3_assistive_prelabel_dry_run_v1.json`
- `reports/final/ai_washing_heldout_v3_freeze_v1.json`

Current status:
- candidate pool rows after exclusions: `177`
- current human-reviewed labels: `0`
- freeze status: `pending_review`

Practical implication:
- the data flow is now explicit and reproducible
- the next human step is review of the `held_out_v3` sheet
- the next model step after that is freezing the rebuilt benchmark and
  rerunning the local layered candidates against it
