# AI-Washing Track A Patent Refresh Source Review V1

## Purpose

This note records the current patent-refresh source posture for Track A.

It answers four questions:
1. Are the newly downloaded PatentViews files locally accessible?
2. Will the current patent refresh scripts run against them?
3. Are we currently using grant timing or application filing timing?
4. Is there a better automation path for future updates?

## Local source files observed

Observed under `/Users/soheilkhodadadi/DataWork/patentsview`:
- `g_patent.tsv`
- `g_patent_abstract.tsv`
- `g_assignee_disambiguated.tsv`
- `PV_grant_data_dictionary.pdf`

Observed headers:

### `g_patent.tsv`
- `patent_id`
- `patent_type`
- `patent_date`
- `patent_title`
- additional grant-level fields

### `g_patent_abstract.tsv`
- `patent_id`
- `patent_abstract`

### `g_assignee_disambiguated.tsv`
- `patent_id`
- `assignee_sequence`
- `assignee_id`
- `disambig_assignee_organization`
- other assignee fields

## Current repo compatibility

### 1. The modern extractor lane is close to compatible

The later filtered patent scripts already expect the right **columns**:
- `disambig_assignee_organization`
- `patent_abstract`
- `patent_date`

Relevant scripts:
- `src/semantic_ai_washing/patents/extract_filtered_patents.py`
- `src/semantic_ai_washing/patents/extract_filtered_patents_lightweight.py`
- `src/semantic_ai_washing/patents/benchmark_keyword_sets.py`

### 2. The modern extractor lane still assumes old filenames

The current code still hardcodes:
- `patent.tsv`
- `patent_abstract.tsv`
- `patent_assignee.tsv`

The new local files are instead:
- `g_patent.tsv`
- `g_patent_abstract.tsv`
- `g_assignee_disambiguated.tsv`

Implication:
- the modern patent refresh lane will fail with `FileNotFoundError` until we
  either rename/symlink the new files or add filename resolution inside the
  extractor scripts

### 3. Older exploratory patent scripts are not the right refresh lane

These older scripts are either sample-grade or expect older schemas:
- `src/semantic_ai_washing/patents/extract_from_patentsview.py`
- `src/semantic_ai_washing/patents/extract_ai_patents.py`

They should not be used for the current refresh.

## Data-definition finding

### 4. The current local PatentViews drop is grant-oriented

The local dictionary is explicitly a **grant** data dictionary:
- `PV_grant_data_dictionary.pdf`

The currently downloaded tables are all `g_*` tables.

That means the current local batch is centered on granted-patent tables, and
our current scripts use:
- `patent_date`

from `g_patent.tsv`.

Based on the dictionary, `patent_date` is the patent grant date, not the
application filing date.

### 5. The dictionary indicates application-level filing dates exist, but they are not in the local three-file drop

The dictionary includes a `g_application` table and a `filing_date` field.

Implication:
- if we want yearly counts aligned to **application filing timing**, the current
  three-file local drop is not enough by itself
- we would need to add the relevant application-level table(s), or another
  authoritative application-timing source, before rebuilding the patent counts

## API / future automation review

### 6. Bulk-download automation is feasible and worth documenting

The most useful future automation path is not a patent-by-patent query API.
It is USPTO bulk-data discovery/download automation.

Official source reviewed:
- USPTO BDSS Services User Guide:
  https://developer.uspto.gov/sites/default/files/bdss_ug.pdf

Useful takeaway:
- the BDSS API can search and retrieve USPTO bulk data product metadata and file
  download URLs
- this is a good fit for discovering and versioning future PatentViews/bulk
  products without relying on ad hoc manual browsing

### 7. A direct API may still be useful later, but not as the main historical refresh lane

There are official USPTO data APIs, but they are better suited to search/access
workflows than to replacing a full historical bulk refresh.

For our use case, the best near-term posture is:
- keep bulk files as the canonical refresh input
- optionally use API-based discovery later to find the newest product files

## Recommended Track A decision

### Immediate operational choice

Use the modern filtered patent extractor lane, but patch filename resolution so
it accepts either:
- `patent.tsv` or `g_patent.tsv`
- `patent_abstract.tsv` or `g_patent_abstract.tsv`
- `patent_assignee.tsv` or `g_assignee_disambiguated.tsv`

This is lower-risk than manual renaming and keeps the repo compatible with more
than one PatentViews vintage.

### Timing choice that still needs an explicit decision

We need to decide between:

1. **Grant-date annual refresh first**
- fastest path
- closest to the current implemented scripts
- good enough if Track A needs a refreshed annual backbone quickly

2. **Application-filing-date annual refresh**
- conceptually closer to the paper language about filing timing
- requires additional source tables beyond the current local three-file drop
- should be chosen on purpose, not assumed accidentally

My recommendation:
- for immediate Track A panel refresh, do **not** pretend this is already a
  filing-date patent series
- document the current grant-date reality clearly
- then decide whether to upgrade the patent timing definition before the next
  panel rebuild

## Immediate next tasks

1. Patch patent filename resolution in the modern filtered extractor lane.
2. Decide whether the first refresh rebuild will use grant timing or be held
   until application-filing timing is added.
3. If filing timing is required, acquire the application-level PatentViews bulk
   table(s) that expose `filing_date`.
4. Extend the year window to at least `2014-2025` before rebuilding the annual
   panel.

## Bottom line

The new PatentViews drop is usable, but not plug-and-play.

The real issues are:
- filename-contract drift
- an unresolved timing-definition decision between grant date and filing date

That timing decision matters more than the filename patch.
