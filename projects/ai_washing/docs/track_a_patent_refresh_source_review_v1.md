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
- `g_application.tsv`
- `g_patent.tsv`
- `g_patent_abstract.tsv`
- `g_assignee_disambiguated.tsv`
- `PV_grant_data_dictionary.pdf`

Observed headers:

### `g_application.tsv`
- `application_id`
- `patent_id`
- `patent_application_type`
- `filing_date`
- additional application-level fields

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

### 4b. No direct CIK bridge was found in the current local grant tables

The local `g_*` PatentViews tables expose:
- `patent_id`
- `application_id`
- assignee identifiers / organization names

They do **not** expose a direct public-firm identifier such as:
- CIK
- GVKEY
- PERMNO

This means the current local PatentViews batch does not remove the need for an
external firm-identity layer.

### 5. Application-level filing dates are available locally

The local source root already includes:
- `g_application.tsv`

and it exposes:
- `patent_id`
- `filing_date`

Implication:
- we can adapt the current filtered patent workflow to join
  `g_application.tsv` on `patent_id`
- we do **not** need to pause for an API-based patent source just to build the
  application-timing series

## API / future automation review

### 6. Bulk-download automation is feasible and worth documenting

The most useful future automation path is not a patent-by-patent query API.
It is USPTO bulk-data discovery/download automation.

Official source reviewed:
- USPTO BDSS Services User Guide:
  https://developer.uspto.gov/sites/default/files/bdss_ug.pdf
- PatentsView 2.x release docs:
  https://search.patentsview.org/docs/2024/02/16/2.0-release/

Useful takeaway:
- the BDSS API can search and retrieve USPTO bulk data product metadata and file
  download URLs
- this is a good fit for discovering and versioning future PatentViews/bulk
  products without relying on ad hoc manual browsing
- it does **not** change the current identity problem by itself; for now we
  still need WRDS / SEC-backed firm identity and name enrichment outside the
  local PatentViews grant tables

### 7. A direct API may still be useful later, but not as the main historical refresh lane

There are official USPTO data APIs, but they are better suited to search/access
workflows than to replacing a full historical bulk refresh.

For our use case, the best near-term posture is:
- keep bulk files as the canonical refresh input
- optionally use API-based discovery later to find the newest product files

## Track A decision update

The initial working preference was:
- main patent series = application filing timing
- robustness patent series = grant timing

That preference was conceptually sound, but the live rebuild taught us an
important constraint:
- `g_application.tsv` inside a **grant-centered** PatentViews drop is not a
  complete application-side source
- it right-censors late-sample activity because it only covers applications
  attached to patents already present in the granted universe

So the current Track A posture is more precise:
- full-span panel backbone = refreshed **grant-timed** series
- preferred filing-timed upgrade = **true pregrant** application tables
- grant-derived `g_application.tsv` timing = useful diagnostic / comparison
  lane, but not the final application backbone

## Recommended Track A decision

### Immediate operational choice

Keep the modern filtered extractor lane patched so it accepts either:
- `patent.tsv` or `g_patent.tsv`
- `patent_abstract.tsv` or `g_patent_abstract.tsv`
- `patent_assignee.tsv` or `g_assignee_disambiguated.tsv`

This remains the right grant-side posture and keeps the repo compatible with
more than one PatentViews vintage.

### Timing decision recorded for Track A

Refined decision:
- use the refreshed **hybrid grant-timed** series as the panel backbone
- build a separate **true application-timed** lane from PatentsView pregrant
  tables
- do not treat grant-derived application dates as the final paper-grade
  application backbone

## April 2026 live-run update

The first corrected application-timing rebuild surfaced an important practical
constraint:

- lookup undercoverage was real and was repaired using SEC-header company names
- after that repair, the application-timing series still collapsed sharply in
  `2023-2025`

That remaining collapse is not a lookup bug. It is the expected right-censoring
pattern when we use **application dates from a granted-patent dataset**.

Practical implication for Track A:
- the repaired **application-timing** series should be kept as the conceptually
  cleaner patent-timing lane
- but it should not be treated as the only full-span `2016-2025` backbone
- Track A should also maintain a corrected **grant-timing** series so the
  refreshed annual panel can still be rebuilt on a less-censored patent series

Working posture now:
1. full-span panel backbone = corrected grant-timing series
2. grant-derived application-timing series = diagnostic comparison lane
3. true filing-timed application series = next upgrade lane via pregrant tables

### Hybrid grant validation update

The first WRDS-only grant rebuild still under-matched the old validated patent
series. A hybrid lookup that combines:
- old patent-validated names
- refreshed WRDS-backed firm identity
- SEC-header company names

recovered the count pattern much better.

Current comparison:
- old validated `2024`: `38,191` total / `2,205` AI
- WRDS-only refreshed `2024`: `34,252` total / `1,703` AI
- hybrid refreshed `2024`: `40,931` total / `2,122` AI

Interpretation:
- the hybrid grant lane is now credible enough to support the refreshed panel
  backbone
- the application upgrade should now focus on **source completeness**, not just
  more name matching

### True pregrant application update

The true pregrant extraction has now been run successfully against:
- `pg_published_application`
- `pg_published_application_abstract`
- `pg_assignee_disambiguated`
- `pg_granted_pgpubs_crosswalk`
- `pg_applicant_not_disambiguated` as fallback matching support

Resulting aggregate application counts:
- `2021`: `47,540` total / `2,749` AI
- `2022`: `45,332` / `2,711`
- `2023`: `42,072` / `3,206`
- `2024`: `27,597` / `1,850`
- `2025`: `6,881` / `395`

Interpretation:
- this is far more credible than both:
  - the older grant-derived application series
  - the first assignee-only pregrant run
- but it still likely understates the latest filing cohorts because the source
  is built from **published** applications
- so application timing is now substantially cleaner, but not fully free of
  end-of-sample censoring

### Bounded fuzzy sensitivity update

A bounded fuzzy-matching sensitivity run was then executed for `2024` at:
- `0.90`
- `0.95`

Result:
- the fuzzy supplement produced implausibly large jumps in both grant and
  pregrant counts
- manual spot checks showed obvious false positives driven by generic tokens
  such as:
  - `city`
  - `new`
  - `one`
  - `discovery`
  - `view`

Interpretation:
- the current fuzzy supplement is too permissive even at high thresholds
- exact normalized hybrid matching should remain the live baseline
- the current fuzzy supplement should be treated as a rejected stress test, not
  as a lane to scale across the full sample


## Immediate next tasks

1. Keep the patched grant-side extractor lane as the running default.
2. Use the hybrid grant-timed rebuild as the patent input for the refreshed
   annual panel.
3. Keep the true pregrant application lane as the conceptually cleaner timing
   series.
4. Decide whether the main application-timed paper lane should truncate the
   most recent years because of publication lag.
5. Keep exact normalized hybrid matching as the baseline method.
6. Do not scale the current fuzzy supplement across the full sample.

## Bottom line

The new PatentViews grant drop is usable for the panel backbone once name
matching is repaired, but a serious application-timing lane should move to
true pregrant tables rather than leaning on `g_application.tsv` alone.

The real issues are:
- filename-contract drift
- an unresolved timing-definition decision between grant date and filing date

That timing decision matters more than the filename patch.
