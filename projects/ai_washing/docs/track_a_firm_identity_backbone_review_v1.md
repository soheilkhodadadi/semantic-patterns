# AI-Washing Track A Firm Identity Backbone Review V1

## Purpose

This note records the current decision on how the refreshed `2016-2025`
AI-washing panel should define its firm universe and identity backbone.

The goal is to avoid using the old panel as an implicit source of truth and to
avoid forcing the patent-matching layer to solve firm identity by itself.

## Trigger for this review

The corrected application-timing patent rebuild improved after the SEC-header
company-name repair, but the series still collapsed sharply in `2023-2025`.

That revealed two separate issues that need to stay conceptually distinct:

1. firm identity / company-universe coverage
2. patent timing coverage and right-censoring

The first can be repaired with a better firm backbone. The second cannot.

## What we checked

### 1. Refreshed speaker universe

We rebuilt the disclosure-side speaker universe from the refreshed narrative
measures rather than from the legacy panel.

Outputs:
- `data/processed/aggregates/firm_year_narrative_measures_2025_refresh_v1.parquet`
- `data/processed/aggregates/firm_year_narrative_measures_prelim_clean_2016_2025_refresh_v1.parquet`
- `data/metadata/company_list_ever_speaker_2016_2025_refresh_v1.csv`

Current refreshed speaker universe:
- firm-year rows: `13,777`
- unique speaker firms: `5,084`

### 2. WRDS firm-identity coverage

We verified live WRDS access and checked whether the refreshed speaker CIKs map
cleanly into `comp.company`.

Observed:
- refreshed speaker CIKs checked: `5,574` in the broader SEC-enriched working list
- direct `comp.company` CIK matches: `5,014`
- unmatched to `comp.company`: `560`

This is strong enough to make WRDS the primary firm-identity backbone for the
refreshed panel.

### 3. CRSP link coverage

For the matched WRDS firms, we checked `crsp_a_ccm.ccmxpf_lnkhist`.

Observed:
- matched `gvkey` values: `5,014`
- `gvkey` values with CRSP link coverage: `4,454`

This is also strong enough for the later event-study lane.

## Patent-series comparison

### Old validated baseline

Old baseline totals:
- `2021`: total `42,515`, AI `1,775`
- `2022`: total `37,585`, AI `2,014`
- `2023`: total `40,206`, AI `2,400`
- `2024`: total `38,191`, AI `2,205`

### Corrected application-timing series

Corrected application-timing totals:
- `2021`: total `40,138`, AI `1,832`
- `2022`: total `29,316`, AI `1,330`
- `2023`: total `17,690`, AI `856`
- `2024`: total `4,716`, AI `210`
- `2025`: total `122`, AI `12`

Interpretation:
- the company-lookup repair helped
- but the late-sample collapse remains
- this is consistent with right-censoring from using application dates drawn
  from a granted-patent dataset

### Corrected grant-timing series

Corrected grant-timing totals:
- `2021`: total `45,539`, AI `1,506`
- `2022`: total `40,721`, AI `1,812`
- `2023`: total `43,149`, AI `2,251`
- `2024`: total `40,715`, AI `2,048`
- `2025`: total `30,409`, AI `1,774`

Interpretation:
- `2021-2024` now stay in the same neighborhood as the old validated series
- coverage is materially better than the broken application-timing series
- `2025` is still partial because the local PatentViews grant drop is not a
  complete end-of-year census

## Decision

### Primary firm-identity backbone

Use:
- refreshed disclosure-side speaker universe
- WRDS `comp.company` for firm identity
- WRDS `comp.funda` for annual controls

Why:
- this is cleaner than deriving firm identity from patent matches
- it lets patents remain an enrichment step instead of the place where we infer
  the firm universe

### Patent timing posture

Use:
- corrected **grant timing** for the full-span refreshed panel backbone
- corrected **application timing** as the conceptually cleaner robustness /
  comparison lane

Why:
- application timing is more conceptually aligned with disclosure timing
- but the currently available local application dates come from granted-patent
  tables and are therefore right-censored near the end of the sample
- using them as the only full-span backbone would quietly understate late-sample
  patenting

## Recommended rebuild order

1. Build refreshed narrative measures through `2025`
2. Build refreshed speaker-firm universe from narrative measures
3. Pull WRDS crosswalk + annual controls for that speaker universe
4. Rebuild the patent lookup against that refreshed firm universe
5. Build the full refreshed panel on:
   - refreshed narrative measures
   - WRDS controls
   - corrected grant-timing patent series
6. Keep the application-timing patent panel as the main timing-comparison /
   robustness lane

## Bottom line

The panel should now be rebuilt from the disclosure side outward:
- disclosure universe first
- WRDS identity and controls second
- patents third

That is a more defensible path than trying to merge refreshed patent outputs
into the legacy panel and hoping the identity layer still lines up.
