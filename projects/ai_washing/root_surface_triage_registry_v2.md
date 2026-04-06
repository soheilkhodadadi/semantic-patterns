# AI-Washing Root Surface Triage Registry V2

## Purpose

This registry tracks the remaining root-owned `semantic_ai_washing` surfaces
that still exist outside the canonical member-owned `ai_washing_member`
authorities.

This version refreshes the picture after Queues V14-V21 and makes one point
explicit: there are currently no strong active `ai_washing` migration openers
left. The remaining root surfaces are wrappers, dormant-but-relevant utilities,
or legacy/template candidates.

## Status classes

- `active_migration_candidate`: still part of an active current-stage workflow;
  a good candidate for a future bounded queue
- `wrapper_or_runner`: thin restartable or orchestration surface that may remain
  a wrapper even after deeper authorities move
- `dormant_but_relevant`: not the best next migration target, but still part of
  the project's real workflow history or plausible future work
- `legacy_template_candidate`: should be reviewed by the separate hygiene queue
  before any effort is spent migrating it forward

## Current counts

- labeling still root-owned: 2
- classification still root-owned: 7
- data still root-owned: 12
- active migration candidates remaining across all three lanes: 0

## Labeling surfaces still root-owned

### Active migration candidate
- none

Reason:
- the active labeling, heldout, IRR, review-sheet, and assistive calibration
  lanes are now canonical under `ai_washing_member.labeling`

### Wrapper or runner
- `src/semantic_ai_washing/labeling/run_assistive_prelabel_restartable.py`
  - restartable wrapper around the member-owned assistive prelabel surface
- `src/semantic_ai_washing/labeling/sample_heldout_v2_restartable.py`
  - restartable wrapper around the member-owned heldout sampling surface

## Classification surfaces still root-owned

### Active migration candidate
- none

Reason:
- the active preliminary classification, benchmarking, evaluation, reporting,
  and restartable lanes are now canonical under `ai_washing_member.classification`

### Dormant but relevant
- `src/semantic_ai_washing/classification/classify_all_ai_sentences.py`
- `src/semantic_ai_washing/classification/classify_with_centroids.py`
- `src/semantic_ai_washing/classification/compute_centroids.py`
- `src/semantic_ai_washing/classification/compute_centroids_mpnet.py`
- `src/semantic_ai_washing/classification/embed_labeled_sentences.py`
- `src/semantic_ai_washing/classification/embed_labeled_sentences_mpnet.py`
- `src/semantic_ai_washing/classification/utils.py`

Reason:
- these belong to older classifier-training, baseline, or broader evaluation
  lanes that still matter historically and may matter again
- they are not the strongest next authority moves for the current lab
  restructure

## Data surfaces still root-owned

### Active migration candidate
- none

Reason:
- the active manifest, indexing, sentence-table, pool-expansion, materialization,
  backfill, and tranche-rebuild lanes are now canonical under
  `ai_washing_member.data`

### Dormant but relevant
- `src/semantic_ai_washing/data/build_active_filing_company_universe.py`
- `src/semantic_ai_washing/data/build_company_list.py`
- `src/semantic_ai_washing/data/clean_sentence_tables.py`
- `src/semantic_ai_washing/data/extract_ai_sentences.py`
- `src/semantic_ai_washing/data/extract_sample_filings.py`
- `src/semantic_ai_washing/data/pull_compustat_controls.py`

Reason:
- these are still part of real data-processing or diagnostic history
- they may still be useful, but they are not the cleanest next migration
  targets

### Legacy template candidate
- `src/semantic_ai_washing/data/clean_compustat.py`
- `src/semantic_ai_washing/data/clean_crsp.py`
- `src/semantic_ai_washing/data/clean_sec.py`
- `src/semantic_ai_washing/data/download_compustat.py`
- `src/semantic_ai_washing/data/download_crsp.py`
- `src/semantic_ai_washing/data/download_sec.py`

Why these are candidates:
- they look more like older acquisition/cleanup utilities than current
  restructure priorities
- they already have legacy flat shims under `src/data/`
- they are better handled by a future retire/quarantine pass than by migration
  promotion

Queue V23 posture:
- the generated script inventory and script registry now treat these six
  utilities as script-deprecation candidates instead of current canonical
  front-door entrypoints
- they still are not retire-ready because registry, inventory, and flat-shim
  dependencies remain live

## What is intentionally not in this registry

This registry focuses on root-owned `ai_washing` member surfaces.

It does not duplicate:
- `labcore` low-level helpers already externalized to `semantic_labcore`
- `director` package surfaces already externalized to `semantic_director`
- compatibility shims whose canonical authority already exists elsewhere

## Recommended use before the next `ai_washing` queue

Recommended posture:
- do not open a new `ai_washing` active migration queue unless a real new
  `active_migration_candidate` appears after explicit re-triage
- treat the remaining root-owned `ai_washing` surfaces as wrappers,
  dormant-but-relevant utilities, or later hygiene candidates
- use the separate hygiene queue before spending migration effort on the six
  legacy/template data utilities
