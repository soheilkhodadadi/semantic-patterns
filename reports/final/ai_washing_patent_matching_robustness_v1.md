# AI-Washing Patent Matching Robustness Note V1

## Purpose

This note records the current patent and pregrant application matching logic
used for the refreshed AI-washing panel and gives a critical view of its
strengths, limitations, and robustness.

The goal is to make the matching procedure explainable to a skeptical reader.
This is not just a workflow note. It is a short methods note we can reuse later
in results packaging and paper drafting.

## Bottom line

The current refreshed patent lane is materially stronger than the preliminary
lane because it now uses:
- a refreshed ever-speaker firm universe
- a hybrid firm-identity backbone built from older validated lookup assets,
  WRDS identities, and SEC header company names
- strict normalized exact matching rather than loose fuzzy thresholds
- pregrant applicant fallback when assignee-only matching undercounts
- an explicit distinction between grant timing and pregrant publication timing

Current status:
- grant timing is the safest full-span backbone
- pregrant application timing is now strong enough to use seriously
- application counts in the latest years still need a publication-lag caveat

## What the current panel covers

Refreshed panel:
- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2025_refresh_hybrid_grant_pregrant_v1.csv`

Coverage confirmed:
- `50,840` firm-year rows
- `5,084` ever-speaking firms
- panel years `2016-2025`
- grant and application fields present in the panel for those firm-years

Upstream annual patent/application series:
- grant counts: `data/processed/patents/ai_patent_counts_filtered_ever_speaker_2016_2025_hybrid_grant_2014plus.csv`
- pregrant counts: `data/processed/patents/ai_application_counts_filtered_ever_speaker_2016_2025_hybrid_pregrant_2014plus.csv`

Those upstream series run from `2014-2025`, which is what allows the `2016-2025`
panel to carry lagged patent and application variables without losing the early
sample years mechanically.

Important precision:
- the panel currently carries annual counts and lag/lead features
- it does not store every raw patent or application date at the row level
- raw timing is preserved upstream through the source tables and the matched
  year assignment used in the count builders

## Current matching logic

### 1. Firm universe and identity layer

The current ever-speaker universe is built from refreshed narrative measures,
then enriched with:
- legacy validated patent lookup assets
- WRDS-backed firm identities and controls
- SEC header company names and former names extracted from the 10-K source

This matters because patent matching is not performed from a bare CIK list.
It is performed from a hybrid identity layer that carries cleaned names and
curated aliases.

### 2. Name normalization

Core normalization helper:
- `src/semantic_ai_washing/patents/keyword_matching.py`

Normalization does the following:
- lowercase text
- remove punctuation
- split into tokens
- strip trailing legal suffixes such as `inc`, `corp`, `llc`, `ltd`, `plc`,
  `holdings`, and similar
- join back into a normalized organization string

Examples:
- `Snowflake Inc.` -> `snowflake`
- `QUALCOMM Incorporated` -> `qualcomm`
- `International Business Machines Corp.` -> `international business machines`

This is not fuzzy matching. It is exact equality after normalization.

### 3. No loose fuzzy matching in the live patent lane

The current refreshed patent and pregrant extractors do **not** use a fuzzy
similarity threshold.

They do not use:
- Levenshtein thresholds
- cosine similarity over names
- `rapidfuzz`
- `difflib.SequenceMatcher`
- trial-and-error cutoffs like `0.80` or `0.90`

Instead, they use:
- exact equality on normalized terms
- alias expansion from curated lookup sources
- a uniqueness screen that drops normalized terms shared by more than one CIK

That last piece is important. The current hybrid lookup generated:
- `8,670` normalized terms total
- `8,622` unique terms retained
- `48` ambiguous terms excluded from direct matching

That is a conservative design choice. It lowers false positives at the cost of
some recall.

### 4. Grant matching

Grant-side extractor:
- `src/semantic_ai_washing/patents/extract_filtered_patents_lightweight.py`

Current grant matching uses:
- PatentsView granted patent tables
- disambiguated assignee organization names
- exact normalized matching into the unique-term index

This refreshed hybrid grant lane is consistent with the earlier validated grant
results.

### 5. Pregrant application matching

Pregrant extractor:
- `src/semantic_ai_washing/patents/extract_filtered_pregrant_applications_lightweight.py`

Current pregrant matching uses:
1. `pg_assignee_disambiguated.tsv` first
2. `pg_applicant_not_disambiguated.tsv` as fallback for unmatched `pgpub_id`
3. exact normalized term matching in both passes
4. deduplication at `(cik, application_id)`
5. preference for current publication identifiers and later publication dates
   when multiple `pgpub_id` rows map to the same application

This fallback was necessary. Assignee-only pregrant matching materially
undercounted applications for several obvious firms.

## What the sensitivity checks showed

### Grant-side identity sensitivity

A cleaner but narrower WRDS-only name source was not enough for patent matching.
For `2024`:
- refreshed WRDS-only grant lane: `34,252` total patents / `1,703` AI patents
- refreshed hybrid grant lane: `40,931` total patents / `2,122` AI patents
- old validated reference: `38,191` total patents / `2,205` AI patents

Interpretation:
- hybrid identity construction is not cosmetic
- it materially restores recall and brings the refreshed grant lane back into a
  plausible range relative to the preliminary benchmark

### Pregrant matching sensitivity

Assignee-only pregrant matching was too low.
For `2024`:
- assignee-only pregrant: `6,432` total applications / `447` AI applications
- assignee + applicant fallback: `27,597` total applications / `1,850` AI applications

And firm coverage improved from:
- `1,303` firms with any applications
- to `1,881` firms with any applications

Interpretation:
- applicant fallback is not a cosmetic enhancement
- it fixes a real undercounting problem in the pregrant lane

### Remaining late-sample drop

Even after the fallback repair, pregrant application counts still drop in the
latest years:
- `2023`: `42,072` total / `3,206` AI
- `2024`: `27,597` total / `1,850` AI
- `2025`: `6,881` total / `395` AI

That remaining drop is now more plausibly explained by publication lag rather
than by a matching collapse.

## Critical view

### What is strong about the current method

1. It is conservative.
- The live lane does not depend on opaque fuzzy thresholds.
- Ambiguous normalized terms are excluded rather than forced into matches.

2. It is triangulated.
- The firm identity layer is not built from one source only.
- It combines older validated lookup assets, WRDS firm identity, and SEC header
  names.

3. The major pregrant undercount was diagnosed and repaired explicitly.
- The fix is now documented and reproducible.

4. Grant and application timing are both available.
- This lets us present grant timing as a stable full-span comparison while using
  pregrant timing for the conceptually cleaner application-based view.

### What a critic could still say

1. There is still no official PatentsView-to-CIK bridge in the working lane.
- Matching still depends on names and aliases.
- That is common in this kind of work, but it remains a real limitation.

2. Exact matching trades recall for precision.
- By avoiding fuzzy matching, we likely miss some valid organizational variants.
- This is a deliberate choice, not an accident.

3. Applicant fallback uses a non-disambiguated file.
- That improves coverage, but it can introduce extra noise if a raw applicant
  string is broad or inconsistently formatted.
- The exact normalized-term match and deduplication rules help contain that
  risk.

4. Pregrant publication data are still subject to timing censoring.
- Near the end of the sample, published-application counts are likely below the
  eventual full application universe.

## Are there plausible alternatives we are missing?

Yes, but none is clearly better as an immediate replacement.

Possible alternatives:
1. A probabilistic entity-resolution layer over names, addresses, and assignee
   metadata.
- Likely higher recall
- also higher false-positive risk
- harder to explain cleanly in the paper

2. A commercial or official external assignee-to-public-company bridge.
- Potentially attractive
- not currently available in the local sources we audited

3. A more aggressive alias expansion from firm-history sources.
- Worth considering later if specific firms still look undercounted
- not necessary to keep the current lane defensible

Given the tradeoffs, the current approach is a reasonable and defensible paper
method:
- normalized exact matching
- hybrid identity enrichment
- applicant fallback where needed
- explicit publication-lag caveat

## Recommended paper posture

Recommended current posture:
- keep grant timing in the portfolio of reported results because it is the most
  stable full-span backbone
- use pregrant application timing as the conceptually cleaner lane, but state
  clearly that late-sample years may be publication-lag affected
- if needed for a final main-spec decision, compare full-span application
  results against a truncated-late-year robustness version rather than hiding
  the issue

## One-sentence summary

The refreshed patent pipeline is now robust enough to defend: it uses strict
normalized exact matching plus hybrid identity enrichment and pregrant applicant
fallback, and the remaining weakness is publication-lag censoring in the latest
application years rather than a broken matching process.
