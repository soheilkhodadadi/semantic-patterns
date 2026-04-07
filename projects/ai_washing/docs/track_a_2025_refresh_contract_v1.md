# AI-Washing Track A 2025 Refresh Contract V1

Date: `2026-04-06`

## Purpose

This note locks the refresh namespace and the first bounded execution contract
for the `2025` extension lane.

It exists so we can index and extract in a controlled way without mutating the
accepted March 2026 backbone or reusing the older mixed-form preliminary lane.

## Contract summary

### Raw refresh window

Use this identifier for the staged raw `2025` annual lane:
- `annual_10k_2025_refresh_v1`

Meaning:
- bounded raw refresh scope
- annual filing policy
- `2025` only
- first execution version

### Extended clean backbone target

Use this identifier for the eventual refreshed clean analysis lane:
- `annual_10k_2016_2025_refresh_v1`

Meaning:
- the accepted clean `2016-2024` annual backbone plus the new `2025` extension
- this is the target analysis namespace, not the raw-source index namespace

## Annual filing policy

First-pass canonical annual policy:
- include `10-K`
- exclude `10-Q`
- exclude `10-Q-A`
- keep `10-K-A` visible in the raw annual index
- do not include `10-K-A` in the first extraction pass unless we explicitly
  choose a fallback extension rule later

This gives us:
- annual-only indexing
- strict `10-K` first extraction
- a documented place for fallback amendments later if needed

## First bounded refresh artifacts

### Raw index and source-window metadata

- `data/metadata/available_filings_index_2025_refresh_v1.csv`
- `data/metadata/source_windows_2025_refresh_v1.json`
- `reports/data/source_index_summary_2025_refresh_v1.json`

### Extraction manifests

- directory:
  - `data/manifests/filings/annual_10k_2025_refresh_v1/`
- quarter manifests:
  - `manifest_y2025_q1.csv`
  - `manifest_y2025_q2.csv`
  - `manifest_y2025_q3.csv`
  - `manifest_y2025_q4.csv`
- manifest summary:
  - `reports/data/annual_10k_2025_refresh_manifest_summary_v1.json`

### Raw sentence extraction lane

- batch outputs under:
  - `data/processed/sentences_refresh_2025_v1/year=2025/_batches/`
- combined year output:
  - `data/processed/sentences_refresh_2025_v1/year=2025/ai_sentences.parquet`
- progress report:
  - `reports/data/annual_10k_2025_refresh_extraction_progress_v1.json`
- final extraction report:
  - `reports/data/annual_10k_2025_refresh_extraction_v1.json`

## Execution policy

### Why quarter manifests

Quarter manifests are required because they give us:
- checkpointed extraction progress
- lower blast radius on failure
- reuse of completed quarter outputs on rerun

This matches the successful earlier pattern where we avoided one monolithic run
with no recovery surface.

### Why the refresh lane is separate

We keep the refresh lane separate because:
- the accepted paper backbone already exists and should remain stable
- the old active-window sentence lane is mixed-form
- the `2025` extension should be reviewable before any promotion into the
  accepted clean analysis backbone

## Current helper surfaces

Refresh-specific helpers now available:
- `projects/ai_washing/src/ai_washing_member/data/index_refresh_window.py`
- `projects/ai_washing/src/ai_washing_member/data/build_refresh_extraction_manifests.py`
- `projects/ai_washing/src/ai_washing_member/data/extract_refresh_year_batches.py`

These are intentionally bounded helpers.
They do not replace the earlier general-purpose surfaces.

## Next step after this contract

After locking this contract, the next honest move is:
1. run the refresh-specific annual index
2. build the quarter extraction manifests
3. run quarter-batch raw sentence extraction for `2025`
4. only then decide the clean-sentence refresh step
