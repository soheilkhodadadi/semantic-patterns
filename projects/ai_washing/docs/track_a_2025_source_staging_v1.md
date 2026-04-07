# AI-Washing Track A 2025 Source Staging V1

Date: `2026-04-06`

## Purpose

This note records the first bounded execution move after the `2025` refresh
readiness pass:
- lock the annual filing policy
- normalize the raw `2025` SEC source into the expected `YEAR/QTR*` shape
- keep the accepted `2016-2024` clean backbone untouched

## Decision

Status: `staged_for_2025_extension`

The source-staging step is intentionally `2025`-only.

Reason:
- the old local SEC source hint currently points to a non-existent path:
  - `data/metadata/sec_source_dir.txt`
  - `/Users/soheilkhodadadi/DataWork/10-X_C_2021-2124`
- so a combined raw `2021-2025` restaging is not currently possible from local
  raw sources alone
- the authoritative paper backbone already exists separately as the accepted
  clean annual `2016-2024` lane

That means the right move is:
- normalize raw `2025`
- extend the clean annual backbone forward
- avoid pretending we can reconstitute the full raw `2021-2024` source tree

## Annual filing policy locked for Track A

Canonical policy for the `2025` extension:
- include `10-K`
- exclude `10-Q`
- exclude `10-Q-A`
- treat `10-K-A` as fallback-only and not part of the first-pass canonical lane

This keeps the refresh aligned with the accepted annual clean backbone rather
than the older mixed-form preliminary lane.

## Staged source root

Raw quarter source used:
- `/Users/soheilkhodadadi/DataWork/2025`

Staged canonical root created:
- `/Users/soheilkhodadadi/DataWork/10-X_C_2025_staged_v1`

Staged year directory:
- `/Users/soheilkhodadadi/DataWork/10-X_C_2025_staged_v1/2025`

Quarter links created under that year root:
- `QTR1`
- `QTR2`
- `QTR3`
- `QTR4`

The stage is symlink-based rather than copy-based, so:
- the raw source is not duplicated
- the indexer can read the expected `YEAR/QTR*` layout
- reruns stay cheap and reversible

## Reproducibility surface

Canonical staging helper:
- `projects/ai_washing/src/ai_washing_member/data/stage_sec_year_root.py`

Helper test:
- `projects/ai_washing/tests/test_stage_sec_year_root_member.py`

Example command used for the local stage:

```bash
PYTHONPATH=projects/ai_washing/src:src .venv/bin/python -m ai_washing_member.data.stage_sec_year_root \
  --source-root /Users/soheilkhodadadi/DataWork/2025 \
  --output-root /Users/soheilkhodadadi/DataWork/10-X_C_2025_staged_v1 \
  --year 2025
```

## What we deliberately did not do

We did not:
- overwrite `data/metadata/sec_source_dir.txt`
- point the shared SEC hint at a `2025`-only root
- change active source-window naming yet
- run extraction or indexing yet

Reason:
- those changes belong to the next bounded prework step
- the current shared hint file is stale, but replacing it with a `2025`-only
  root would create a different kind of confusion

## Next step

The next honest move is:
- define the refreshed `2025` annual namespace and source-window contract
- then run a bounded `2025`-only index/manifest/extraction path against the
  staged root

That keeps Track A moving without blurring the accepted March 2026 backbone.
