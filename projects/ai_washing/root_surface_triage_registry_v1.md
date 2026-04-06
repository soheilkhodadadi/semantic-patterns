# AI-Washing Root Surface Triage Registry V1

## Purpose

This registry tracks the meaningful root-owned `semantic_ai_washing` surfaces
that still remain outside the canonical member-owned `ai_washing_member`
authorities.

It exists to keep future queues grounded.

## Status classes

- `active_migration_candidate`: still part of an active current-stage workflow;
  a good candidate for future bounded queues
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

## Labeling surfaces still root-owned

### Active migration candidate
- none

Reason:
- the active labeling benchmark edge is now canonical under
  `ai_washing_member.labeling.build_irr_boundary_benchmark`
- the remaining root-owned labeling surfaces are wrappers rather than the next
  strong authority moves

### Wrapper or runner
- `src/semantic_ai_washing/labeling/run_assistive_prelabel_restartable.py`
  - restartable wrapper around the now-member-owned assistive prelabel surface
- `src/semantic_ai_washing/labeling/sample_heldout_v2_restartable.py`
  - restartable wrapper around the now-member-owned heldout sampling surface

## Classification surfaces still root-owned

### Active migration candidate
- none

Reason:
- the active preliminary classification/reporting lane is now canonical under
  the member-owned `ai_washing_member.classification` surface

### Wrapper or runner
- none

### Dormant but relevant
- `src/semantic_ai_washing/classification/classify_all_ai_sentences.py`
- `src/semantic_ai_washing/classification/classify_with_centroids.py`
- `src/semantic_ai_washing/classification/compute_centroids.py`
- `src/semantic_ai_washing/classification/compute_centroids_mpnet.py`
- `src/semantic_ai_washing/classification/embed_labeled_sentences.py`
- `src/semantic_ai_washing/classification/embed_labeled_sentences_mpnet.py`
- `src/semantic_ai_washing/classification/utils.py`

Reason:
- these belong to broader classifier-training or older baseline lanes
- they still matter historically and may matter again, but they are not the
  cleanest next authority moves

## Data surfaces still root-owned

### Active migration candidate
- none

Reason:
- the active data lane is now largely canonical under `ai_washing_member.data`
- remaining root-owned data surfaces are now better treated as dormant,
  peripheral, or hygiene candidates rather than next live migration targets

### Dormant but relevant
- `src/semantic_ai_washing/data/build_active_filing_company_universe.py`
- `src/semantic_ai_washing/data/build_company_list.py`
- `src/semantic_ai_washing/data/clean_sentence_tables.py`
- `src/semantic_ai_washing/data/extract_ai_sentences.py`
- `src/semantic_ai_washing/data/extract_sample_filings.py`
- `src/semantic_ai_washing/data/pull_compustat_controls.py`

Reason:
- these are still part of real data processing or diagnostic lanes, but they are
  not the strongest next migration targets

### Legacy/template candidate
- `src/semantic_ai_washing/data/clean_compustat.py`
- `src/semantic_ai_washing/data/clean_crsp.py`
- `src/semantic_ai_washing/data/clean_sec.py`
- `src/semantic_ai_washing/data/download_compustat.py`
- `src/semantic_ai_washing/data/download_crsp.py`
- `src/semantic_ai_washing/data/download_sec.py`

Reason:
- these look more like peripheral acquisition/cleanup utilities than current
  restructure priorities
- they should be reviewed by the separate hygiene queue before any migration
  effort is spent on them

## What is intentionally not in this registry

This registry focuses on `ai_washing` root-owned surfaces.

It does not duplicate:
- `labcore` low-level helpers already externalized to `semantic_labcore`
- `director` surfaces already externalized to `semantic_director`
- compatibility shims whose canonical authority already exists elsewhere

## Recommended use before the next `ai_washing` queue

Choose the next `ai_washing` queue opener from:
- `active_migration_candidate` only if this list is non-empty again after a
  deliberate re-triage

Do not migrate `legacy_template_candidate` surfaces forward until they have been
reviewed by the separate hygiene queue.
