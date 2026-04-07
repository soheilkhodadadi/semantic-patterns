# AI-Washing Track A Pregrant Source Review V1

## Purpose

This note reviews the newly downloaded pregrant documentation and identifies
which additional USPTO / PatentsView products are most useful for building a
more complete application-timing patent lane.

The goal is to avoid treating application timing from a granted-patent dataset
as the only application-timing source.

## Files reviewed

Local guide files:
- `/Users/soheilkhodadadi/DataWork/patentsview/Guide/PV_pregrant_data_dictionary.pdf`
- `/Users/soheilkhodadadi/DataWork/patentsview/Guide/2026BulkDataProductDescriptions.xlsx`

Supporting official source:
- PatentsView pregrant download tables:
  https://patentsview.org/download/pg-download-tables

## Main finding

There are two very different ways to build a stronger application-timing lane:

1. download **processed PatentsView pregrant tables**
2. download **raw USPTO patent-application XML bulk files** and parse them

The first is much better for the current project.

## What the pregrant dictionary confirms

The pregrant dictionary exposes direct analogs to the grant-side tables we have
already been using.

### Core pregrant tables

#### `pg_published_application`

This is the main application-level metadata table.

Useful fields:
- `pgpub_id`
- `application_id`
- `filing_date`
- `published_date`
- `application_title`

Interpretation:
- `application_id` is the stable application key
- `pgpub_id` is the publication key used by several other pregrant tables
- `filing_date` gives the application-timing variable we want

#### `pg_published_application_abstract`

This is the direct analog of the grant abstract table.

Useful fields:
- `pgpub_id`
- `application_abstract`

#### `pg_assignee_disambiguated`

This is the direct analog of the granted assignee-disambiguated table.

Useful fields:
- `pgpub_id`
- `assignee_id`
- `disambig_assignee_organization`

This gives us the organization-level assignee string needed for company-name
matching on the application side.

#### `pg_granted_pgpubs_crosswalk`

This is the key bridge between the pregrant and granted worlds.

Useful fields:
- `pgpub_id`
- `patent_id`
- `application_id`
- `current_pgpub_id_flag`
- `current_patent_id_flag`

This makes it possible to:
- compare grant-timed and application-timed series more explicitly
- align applications to granted patents when both exist
- avoid overcounting republications if we decide to use the crosswalk in a
  deduplication step

### Optional pregrant table

#### `pg_applicant_not_disambiguated`

This is not essential for the first rebuild, but it can help if application-side
assignee coverage is weak for some firms.

Useful fields:
- `pgpub_id`
- `raw_applicant_organization`

That makes it a plausible fallback-matching surface after
`pg_assignee_disambiguated`.

## What the bulk product spreadsheet shows

### Best raw USPTO product family

If we had to go to raw USPTO bulk files, the relevant family is:
- `appdt`
- description: Patent Application Data/XML

This is the raw full-text patent-application XML family.

The spreadsheet shows that it covers:
- patent applications published from March 15, 2001 onward
- weekly application publications
- full application text

### Why raw `appdt` is not the first choice

It is much heavier than what we need right now:
- yearly files are very large
- parsing would require a new XML extraction workflow
- we would be rebuilding tables that PatentsView already derived for us

So `appdt` is a fallback, not the preferred next step.

### `appblxml` is also not the first choice

The spreadsheet also lists:
- Patent Application Bibliographic Data/XML
- dataset family: `appblxml`

This is lighter than full application XML, but it is still a raw XML product.
For the current project it is less attractive than downloading the PatentsView
pregrant tables directly because:
- we already have a processed-table workflow
- the pregrant tables already expose application metadata, assignees, and
  abstracts in tabular form

## Recommended download plan

### Recommended now

Download these **PatentsView pregrant tables** if available from the pregrant
download tables page:

1. `pg_published_application`
2. `pg_published_application_abstract`
3. `pg_assignee_disambiguated`
4. `pg_granted_pgpubs_crosswalk`

### Recommended optional fallback

Download this only if application-side assignee coverage looks weak after the
first rebuild:

5. `pg_applicant_not_disambiguated`

### Practical scope for this project

For the current paper lane, the useful coverage is:
- applications/publications relevant to `2014-2025`
- enough history to support lagged patent measures for the `2016-2025`
  disclosure panel

If the PatentsView pregrant download page forces year-by-year pulls, that is
the span to prioritize first.

### Exact ask for the next download round

If you want the cleanest next pull, the download checklist is:

1. `pg_published_application`
2. `pg_published_application_abstract`
3. `pg_assignee_disambiguated`
4. `pg_granted_pgpubs_crosswalk`
5. `pg_applicant_not_disambiguated` only if convenient

That is enough to build a true application-side analog of the current
grant-side patent pipeline without introducing a new raw-XML ETL.

## Not recommended as the first move

Do **not** start by downloading:
- the raw `appdt` XML family
- the raw `appblxml` family

unless we confirm that the PatentsView pregrant tables are unavailable or too
incomplete for our use case.

## Recommended application-side workflow

If the four recommended pregrant tables are downloaded, the application-timing
lane should be rebuilt as follows:

1. use `pg_published_application` as the application metadata backbone
2. join `pg_published_application_abstract` on `pgpub_id`
3. join `pg_assignee_disambiguated` on `pgpub_id`
4. deduplicate at the `application_id` level rather than blindly counting every
   `pgpub_id`
5. carry:
   - `filing_date` for application timing
   - `published_date` for publication timing if needed later
6. optionally join `pg_granted_pgpubs_crosswalk` to compare application and
   grant outcomes for the same application stream

## Design implication for Track A

This means Track A can support two meaningful patent lanes:

1. **grant timing** from the current granted-patent tables
2. **application timing** from true pregrant publication tables

That is much stronger than using application dates pulled only from granted
patent tables, which right-censors late-sample application activity.

## Bottom line

The best next data pull is:
- **PatentsView pregrant tables**, not raw USPTO XML

Most useful files to download next:
1. `pg_published_application`
2. `pg_published_application_abstract`
3. `pg_assignee_disambiguated`
4. `pg_granted_pgpubs_crosswalk`

Optional fifth file:
5. `pg_applicant_not_disambiguated`

Current Track A posture:
- keep the refreshed **hybrid grant-timed** series as the panel backbone
- build the **true pregrant application-timed** lane next from the files above
- treat raw `appdt` / `appblxml` as fallback-only if the pregrant tables prove
  unavailable or materially incomplete
