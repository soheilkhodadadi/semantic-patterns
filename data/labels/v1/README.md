# Label Assets V1

This directory contains the current repo-local label backbone for the
AI-washing classifier lane.

## Canonical training assets

Use these as the default starting point for local-model work:

- `labels_master.parquet`
  - first canonical merged label backbone
  - `551` rows
  - built from the three verified filled batch CSVs
- `labels_master_review.csv`
  - review mirror of `labels_master.parquet`
- `labels_master_boundary_revised_v1.parquet`
  - revised-rubric version of the label backbone
  - same `551` rows
  - `8` row-level label updates relative to `labels_master.parquet`
- `labels_master_boundary_revised_v1_review.csv`
  - review mirror of the revised backbone

Important:
- if the revised backbone is promoted as the new canonical training source,
  refreeze the split registry rather than reusing the older split assignment
  blindly

## Canonical tranche inputs

These are the human-verified tranche files that feed the labels master:

- `labeling_batch_v1_filled_v2_4.csv`
- `labeling_batch_v2_filled.csv`
- `labeling_batch_v3_filled.csv`

Observed merge behavior:
- total tranche rows: `560`
- canonical labeled rows retained: `551`
- excluded during merge:
  - `3` blank-label rows
  - `6` historical held-out overlaps

## IRR and adjudication chain

Use these for disagreement analysis and benchmark rebuilding:

- `irr_subset.parquet`
  - canonical machine-readable IRR sample
  - `120` rows
- `irr_subset_master.csv`
  - first-rater IRR source sheet
- `irr_subset_rater2_blinded.csv`
- `irr_subset_rater2_blinded.xlsx`
  - second-rater handoff templates
- `irr_subset_rater2_completed.xlsx`
  - completed second-rater workbook
- `irr_adjudication_sheet.csv`
- `irr_adjudication_sheet.xlsx`
  - disagreement-only adjudication work sheets
- `irr_adjudication_completed.xlsx`
  - completed adjudication workbook
- `adjudication.parquet`
  - canonical machine-readable adjudication result
  - `120` rows
  - `94` agreement rows
  - `26` third-adjudicator rows

## Revised IRR pack

Use these for the revised-rubric second-rater handoff lane:

- `irr_subset_boundary_revised_v2.parquet`
  - revised-rubric IRR source subset
  - `120` rows
  - `40 / 40 / 40` class-balanced
- `irr_subset_boundary_revised_v2_master.csv`
  - rater-1 source sheet for the revised pack
- `irr_subset_boundary_revised_v2_rater2_blinded.csv`
- `irr_subset_boundary_revised_v2_rater2_blinded.xlsx`
  - second-rater handoff files for the revised pack

Important:
- this pack is currently `2024`-only because the revised label backbone it was
  sampled from is `2024`-only
- do not describe it as a multi-year IRR pack without first expanding the
  revised labeled source pool

## Manual-workflow residue

These files are useful as audit residue, but they are not the preferred inputs
 for training or benchmark freezes:

- `*_prelabeled*`
- `*_slice40*`
- `*_calibration*`
- `*_reextracted*`
- `*.bak*`
- `labeling_batch_v1_filled_v2_4.xlsx`
- `labeling_batch_v1_filled_v2_4.numbers`
- `labeling_batch_v1_filled_v2_notes.csv`
- `irr_adjudication_completed.xlsx.xlsx`

Known duplicates / clutter:
- `labeling_batch_v2_prelabeled_Verified.csv` duplicates
  `labeling_batch_v2_filled.csv`
- `labeling_batch_v3_prelabeled_filled.csv` duplicates
  `labeling_batch_v3_filled.csv`
- `irr_adjudication_completed.xlsx.xlsx` duplicates
  `irr_adjudication_completed.xlsx`

## Usage guidance

- local training backbone:
  - start from `labels_master_boundary_revised_v1.parquet`
- current split source:
  - `data/metadata/splits/split_registry_v1.csv`
- IRR / hard-case benchmark:
  - `adjudication.parquet`
- do not treat blinded or prelabel files as canonical labels
