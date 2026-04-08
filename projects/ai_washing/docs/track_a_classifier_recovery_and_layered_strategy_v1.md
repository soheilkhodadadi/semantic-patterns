# AI-Washing Track A Classifier Recovery And Layered Strategy V1

## Purpose

This note records the recovery status of the benchmark assets and the recommended
next-stage classifier design after the first revised-rubric retraining tranche
failed to improve the live local binary model.

## Recovery findings

### 1. The frozen `held_out_v2` benchmark CSV is still missing

Missing canonical asset:
- `data/validation/held_out_sentences_v2.csv`

Still available:
- `reports/validation/held_out_sentences_v2_freeze.json`

Frozen summary from the surviving report:
- rows: `177`
- final label counts:
  - `Actionable`: `61`
  - `Speculative`: `29`
  - `Irrelevant`: `87`

So the benchmark state is known, but the frozen row-level CSV is not currently
present in the repository tree.

### 2. A recoverable candidate review pack exists in OneDrive

Recovered source:
- `/Users/soheilkhodadadi/Library/CloudStorage/OneDrive-ConcordiaUniversity-Canada/PhD-soheil/Thesis/Semantics/empirical/data/manual/held_out_sentences_v2_review_sheet_10k_only_clean_prelabeled.csv`

Key facts:
- `180` candidate rows before exclusion
- after excluding the three sentence IDs recorded in the freeze report:
  - `177` rows remain
- current `label` column is blank
- `candidate_label` is balanced:
  - `Actionable`: `60`
  - `Speculative`: `60`
  - `Irrelevant`: `57`

Interpretation:
- this appears to be the candidate review sheet that fed the frozen benchmark
- it is not the finalized benchmark, because its label mix does not match the
  frozen benchmark report

### 3. The recovered `177`-row pack is mostly cleanly separable from training

Overlap with current `labels_master`:
- `2` rows

Overlap with `adjudication.parquet`:
- `0` rows

Interpretation:
- the recovered candidate pack is strong enough to rebuild a revised held-out
  benchmark without leaking heavily into the current training backbone

### 4. The historical archived `held_out_sentences.csv` copy is not useful

Recovered historical file:
- `/Users/soheilkhodadadi/Library/CloudStorage/OneDrive-ConcordiaUniversity-Canada/PhD-soheil/Thesis/Semantics/Report & Guides/2025 July/ai-washing-july-2025-report/data/validation/held_out_sentences.csv`

Observed state:
- `12` rows only
- clearly a toy or report-support artifact, not the real benchmark used in the
  current preliminary lane

## Current benchmark assets we can trust

### A. Adjudicated IRR slice

Tracked file:
- `data/labels/v1/adjudication.parquet`

Published benchmark:
- `data/validation/irr_boundary_benchmark_v1.csv`

Properties:
- `120` rows
- final resolved labels from agreement or third-adjudicator resolution
- strong hard-case benchmark for relevance and A/S disagreement behavior

This is a real source-of-truth benchmark.

### B. Frozen split validation surface

Tracked files:
- `data/labels/v1/labels_master.parquet`
- `data/metadata/splits/split_registry_v1.csv`

Derived benchmark:
- `frozen_validation_split`

Properties:
- useful for model regression checks
- not a publication-grade external held-out surface

### C. Recoverable `held_out_v2` candidate pack

Recovered file:
- OneDrive `held_out_sentences_v2_review_sheet_10k_only_clean_prelabeled.csv`

Properties:
- best available source for rebuilding the missing primary benchmark under the
  revised rubric
- should remain benchmark-only

## Model findings that matter for design

### Binary two-stage model

Strength:
- better binary relevance behavior

Weakness:
- actionable/speculative head is still unstable

### MPNet logistic multiclass model

Strength:
- still competitive on the IRR boundary benchmark
- stronger A/S behavior than the binary model on the current hard-case surface

Weakness:
- weaker as a pure relevance gate than the binary model

## Recommended layered local design

The next design should use both local models rather than pretending one of them
has already won.

### Stage 1. Relevance gate

Use:
- `binary_relevance_then_as` relevance head

Reason:
- it remains the stronger local relevance discriminator

Output:
- `Irrelevant` vs `Non-Irrelevant`

### Stage 2. Local A/S resolver

Use:
- `mpnet_logreg_prelim` as the primary local actionable/speculative resolver
  on the non-irrelevant subset

Reason:
- its current IRR-boundary A/S performance is stronger than the binary model

Output:
- `Actionable` vs `Speculative`

### Stage 3. Defer only true hard cases

Defer when:
- binary and logreg disagree materially
- local confidence or margin is low
- sentence belongs to a known unstable category:
  - future intent
  - in-progress build or integration
  - risk or competition framing
  - mixed current-use plus future-plan clauses

### Stage 4. API arbitration

Recommended posture:
1. API `A`: cheaper first escalation
2. API `B`: stronger disagreement arbiter
3. no human in the live path

Decision rule:
- if local and API `A` agree, accept
- if API `A` disagrees, call API `B`
- final label by majority among local model, API `A`, API `B`

This keeps the system reproducible while limiting API cost to genuine boundary
cases.

## Recommended execution order

### Track 1. Rebuild the missing primary benchmark

1. import the recovered `177`-row held-out candidate sheet into the repo as a
   benchmark-recovery source
2. relabel it under the revised rubric
3. publish a new benchmark asset instead of pretending the old frozen CSV still
   exists

This is better than trying to keep the old benchmark name alive without its
actual rows.

### Track 2. Expand training data correctly

Do not use the recovered `177`-row held-out pack for training.

Instead:
1. sample a new reviewed A/S tranche from the clean classified corpus
2. prefer train-split additions over more validation relabeling
3. target the same hard categories seen in the reviewed boundary pack

### Track 3. Compare two local candidates again

Rerun both:
- binary two-stage
- MPNet logistic multiclass

Evaluate on:
- adjudicated IRR benchmark
- rebuilt revised held-out benchmark
- frozen validation split

### Track 4. Then open the selective-defer simulation

Only after the new benchmark is rebuilt and the larger training tranche is in
place.

## Bottom line

The right move is not another tiny binary retrain.

It is:
1. rebuild the missing primary benchmark from the recovered `177`-row review
   pack
2. expand the training tranche separately
3. compare binary and MPNet again on the rebuilt benchmark
4. then build the layered local-plus-defer design from the actual strongest
   pieces
