# AI-Washing Track A Patent Matching Validation V1

## Purpose

This note records the main patent-matching blockers surfaced during the `2025`
refresh and the concrete fixes that resolved them.

The goal is to preserve the reasoning so future reruns do not have to rediscover
the same issues.

## Why this note exists

Patent timing is not a side variable in this project. It is part of the core
AI-washing construct.

That means large changes in patent counts should always be treated as a
methodology question first, not just a data-refresh inconvenience.

## Blocker 1: grant-derived application timing collapsed in late years

### Symptom

When application timing was first rebuilt from `g_application.tsv` inside the
grant-centered PatentViews drop, the application series collapsed sharply:
- `2023`: `17,690` total / `856` AI
- `2024`: `4,716` / `210`
- `2025`: `122` / `12`

### Cause

That source only provides application dates for patents already present in the
granted-patent universe.

So it is not a full application-side source. It right-censors the latest filing
cohorts by construction.

### Resolution

Do not use grant-derived application dates as the serious application backbone.

Use:
- hybrid grant timing for the full-span panel backbone
- true pregrant tables for the application-timing lane

## Blocker 2: pregrant assignee-only matching still undercounted applications

### Symptom

The first true pregrant application run, using only:
- `pg_published_application`
- `pg_published_application_abstract`
- `pg_assignee_disambiguated`
- `pg_granted_pgpubs_crosswalk`

was directionally better than the grant-derived application proxy, but still too
low:
- firms with any applications: `1,303`
- firms with AI applications: `259`

Year totals:
- `2021`: `9,842` total / `498` AI
- `2022`: `9,603` / `532`
- `2023`: `9,135` / `625`

These levels were still too low relative to the validated grant-side reference.

### Deep check

The undercount was not only a timing issue.

Manual checks on large firms showed that many applications were visible under
`raw_applicant_organization` even when they were missing or thin under
`disambig_assignee_organization`.

Examples:
- `QUALCOMM`
  - assignee matches: `13,718`
  - applicant matches: `41,005`
- `PAYPAL`
  - assignee matches: `156`
  - applicant matches: `2,798`
- `SNOWFLAKE`
  - assignee matches: `0`
  - applicant matches: `915`
- `SKYWORKS`
  - assignee matches: `310`
  - applicant matches: `2,947`

### Cause

For pregrant publications, assignee-side organization coverage is not enough on
its own.

Many applications are better represented on the applicant side.

### Resolution

Use applicant-side organization as a **fallback matching surface** for pregrant
publications that do not already have an assignee-side match.

Operational rule:
1. assignee match first
2. applicant fallback only for unmatched `pgpub_id`
3. deduplicate at `(cik, application_id)` after crosswalk enrichment

This keeps the assignee surface as the cleaner primary layer while recovering
missing application activity without broad fuzzy matching.

## Effect of the fallback fix

### Matching-stage improvement

Before applicant fallback:
- matched pregrant publications: `389,037`
- matched firms: `1,303`

After applicant fallback:
- matched pregrant publications: `772,205`
- matched firms at match stage: `2,065`

### Final application-series improvement

Before fallback:
- firms with any applications: `1,303`
- firms with AI applications: `259`

After fallback:
- firms with any applications: `1,881`
- firms with AI applications: `539`

Updated aggregate counts:
- `2021`: `47,540` total / `2,749` AI
- `2022`: `45,332` / `2,711`
- `2023`: `42,072` / `3,206`
- `2024`: `27,597` / `1,850`
- `2025`: `6,881` / `395`

## Interpretation after the fix

The application series now passes the main reasonableness test much better:
- `2021-2023` applications are on the same order as, and often above, the
  grant counts
- `2024-2025` still fall off, but now that looks like publication-lag censoring
  rather than a matching collapse

So the current best reading is:
1. identity matching was a real blocker
2. applicant fallback was the key fix
3. remaining late-sample weakness is mostly publication timing, not name
   matching

## Current recommended posture

### Main working panel backbone

Use:
- hybrid grant timing
- refreshed WRDS controls
- refreshed `2016-2025` narrative backbone

### Application-timing lane

Use:
- true pregrant application series with applicant fallback

But make an explicit paper decision on whether:
- to keep the full span with a publication-lag caveat, or
- to truncate the latest application years for the main specification

## Reusable lesson

For this project, do **not** assume that one patent-side organization surface is
enough.

The safe workflow is:
1. build the disclosure-side speaker universe
2. enrich firm identity with WRDS and validated aliases
3. on grants, use assignee-side organization matching
4. on pregrant publications, use assignee-side matching plus applicant fallback
5. validate aggregate counts against the previously accepted series before using
   the refreshed outputs downstream

## Bottom line

The patent lane is now in a much stronger state than it was at the start of the
refresh.

The main blocker was not just timing. It was that pregrant matching needed
applicant fallback in addition to assignee matching.
