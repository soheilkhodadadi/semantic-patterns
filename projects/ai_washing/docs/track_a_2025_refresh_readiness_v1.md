# AI-Washing Track A 2025 Refresh Readiness V1

Date: `2026-04-06`

## Purpose

This note records the readiness state for the first Track A execution move:
refreshing the AI-washing filing backbone to include `2025` without polluting
the annual clean lane that currently supports the paper.

The goal is to decide the safe execution order before we run new extraction,
classification, or panel assembly work.

## Readiness verdict

Status: `scoped_prework_required`

The `2025` source is accessible and usable, but a direct rerun is not yet safe.

Three concrete reasons:
- the current `2025` SEC folder is mixed-form (`10-K`, `10-K-A`, `10-Q`,
  `10-Q-A`)
- the current active-window sentence-materialization path is not annual-form
  safe
- the current active-window indexing and source-window layer is still hard-coded
  to `2021-2024`

So the next step is not "run the old refresh command with a new folder."
The next step is a bounded prework pass to stand up a clean `2025` annual
refresh lane.

## Confirmed source access

Accessible source path:
- `/Users/soheilkhodadadi/DataWork/2025`

Observed directory shape:
- `/Users/soheilkhodadadi/DataWork/2025/QTR1`
- `/Users/soheilkhodadadi/DataWork/2025/QTR2`
- `/Users/soheilkhodadadi/DataWork/2025/QTR3`
- `/Users/soheilkhodadadi/DataWork/2025/QTR4`

Observed sample forms:
- `10-K`
- `10-K-A`
- `10-Q`
- `10-Q-A`

Important compatibility note:
- the current SEC indexer expects `root/YYYY/QTR*`
- the new `2025` source is currently `root/QTR*`
- that means the source is readable, but not plug-compatible with the current
  indexer without staging or a small ingest adaptation

## Important current-state findings

### 1. The old active-window index is mixed-form

Current indexed form counts in `data/metadata/available_filings_index.csv`:
- `10-Q = 78,024`
- `10-K = 29,217`
- `10-K-A = 3,713`
- `10-Q-A = 2,280`

That index is not an annual-only source of truth.

### 2. The old active-window sentence tables already contain `10-Q`

Current `data/processed/sentences/year=YYYY/ai_sentences.parquet` form mixes:

- `2021`: `10-K=6,432`, `10-Q=5,710`, `10-K-A=380`, `10-Q-A=62`
- `2022`: `10-K=9,760`, `10-Q=7,152`, `10-K-A=326`, `10-Q-A=205`
- `2023`: `10-K=12,200`, `10-Q=11,443`, `10-K-A=639`, `10-Q-A=182`
- `2024`: `10-K=28,365`, `10-Q=21,864`, `10-K-A=1,267`, `10-Q-A=349`

Conclusion:
- the old active-window sentence lane is mixed-form
- it should not be used as the canonical annual extension path for `2025`

### 3. The active-window materializer is the main form-safety risk

Relevant current behavior:
- `projects/ai_washing/src/ai_washing_member/data/index_sec_filings.py`
  indexes both `10-K` and `10-Q` style filings
- `projects/ai_washing/src/ai_washing_member/data/materialize_active_window_sentences.py`
  filters by `source_window_id` and `year`, but not by form

That is exactly the combination that allowed mixed-form sentence tables to be
materialized.

### 4. The final paper backbone is a separate clean annual lane

The current authoritative empirical backbone is not the mixed active-window
preliminary lane.

Current authoritative clean lane:
- narrative measures:
  - `data/processed/aggregates/firm_year_narrative_measures_prelim_clean_v1.parquet`
- source window id in that file:
  - `annual_10k_2016_2024_clean`
- model id in that file:
  - `binary_relevance_then_as_v1`
- ever-speaker panel:
  - `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- regression-ready ever-speaker panel:
  - `data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv`

This is good news.
It means the `2025` refresh should be treated as an extension of the clean
annual lane, not as a continuation of the mixed preliminary sentence lane.

### 5. The old active source-window contract is still hard-coded to `2021-2024`

Current hard-coded assumptions appear in multiple places, including:
- `projects/ai_washing/src/ai_washing_member/data/index_sec_filings.py`
- `projects/ai_washing/src/ai_washing_member/data/materialize_active_window_sentences.py`
- `src/semantic_ai_washing/analysis/audit_preliminary_panel_inputs.py`
- multiple tests and roadmap references

So `2025` is not just a new data drop.
It requires an explicit extension decision for:
- source window naming
- year coverage
- downstream audit expectations

## What the previous clean workflow effectively became

The paper-supporting clean lane now looks like this:

1. annual sentence extraction
2. post-extraction sentence cleanup
3. clean classification with the selected model
4. firm-year narrative measure construction
5. annual company universe / lookup refresh
6. controls refresh
7. patent refresh
8. panel assembly
9. ever-speaker panel assembly
10. regression-ready panel build

This matters because the safe `2025` job is not:
- "merge new sentences into the old final panel"

It is:
- "extend the clean annual backbone in the same order"

## Recommended execution policy

### Filing policy

Recommended canonical annual policy for the refresh:
- use `10-K` as the default canonical filing type
- do **not** include `10-Q` or `10-Q-A`
- treat `10-K-A` as a fallback-only exception lane, not the default

Reason:
- the current final clean backbone is explicitly annual and `10-K` oriented
- amendments can create duplicate annual firm-year disclosure rows
- we should only admit `10-K-A` if a firm-year lacks a usable `10-K` and we
  document that choice

### Namespace policy

Do not overwrite or blur the existing clean lane.

Recommended new namespace posture:
- preserve the current authoritative clean backbone as-is
- create a refreshed annual namespace for the extension work
- only promote refreshed outputs after the extension lane is validated

Suggested target naming direction:
- source window:
  - `annual_10k_2016_2025_refresh_v1`
- outputs:
  - refreshed sentence / clean sentence / narrative / panel artifacts that
    clearly distinguish the `2025` extension from the accepted March 2026
    backbone

### Source staging policy

Do not special-case `/Users/soheilkhodadadi/DataWork/2025` directly inside the
existing indexer without a deliberate reason.

Safer options:
1. create a staged combined SEC root with year directories, for example a
   `2021-2025` root where `2025/` points to the new quarter folders
2. or add a small bounded ingest adaptation that can mount a single-year
   `QTR*` root as `year=2025`

Recommendation:
- prefer staged source-root normalization first
- keep the indexer logic simple if we can

## Safe execution order

### A1.1 Source staging and annual-policy lock

Deliverables:
- a staged `2025`-compatible SEC root shape
- explicit annual filing policy (`10-K` default, no `10-Q`)
- explicit decision on how `10-K-A` is treated

Do not run extraction before this is locked.

### A1.2 Bounded source-window extension

Tasks:
- extend the indexing/source-window contract so `2025` is representable
- avoid mutating the accepted `active_2021_2024` lane in place
- define the `2025` refresh namespace and artifact names before execution

Deliverable:
- a refreshable annual source-window contract for the `2025` extension

### A1.3 2025 annual sentence build

Tasks:
- index the staged annual source
- build a bounded `2025` annual manifest
- extract `2025` sentence tables
- clean `2025` sentence tables before any classification

Important rule:
- do not classify raw mixed-form `2025` sentence tables

### A1.4 2025 clean classification and measures

Tasks:
- classify the cleaned `2025` annual sentence table
- build `2025` firm-year AI metrics
- build `2025` narrative measures

Recommended posture:
- use the current accepted clean model first for the extension pass
- defer model-upgrade decisions to Track A2 rather than blocking A1 entirely

### A1.5 Input refresh for panel rebuild

Tasks:
- refresh WRDS controls through `2025`
- refresh company universe / lookup if required for annual `2025`
- refresh PatentsView extraction through `2025`

Important note:
- patent refresh is not blocked by the sentence lane conceptually
- but the merged panel should not be rebuilt until controls and patents both
  have `2025` coverage

### A1.6 Panel rebuild

Tasks:
- merge refreshed narrative measures, patents, and controls
- rebuild the merged panel
- rebuild the ever-speaker annual panel
- rebuild the regression-ready panel

Important rule:
- do not append `2025` directly to the accepted March 2026 panel by hand
- rebuild the annual panel artifacts from refreshed processed inputs

## What should not be done

Do not:
- point the old active-window materializer straight at `/Users/soheilkhodadadi/DataWork/2025`
- merge `2025` rows directly into the old clean panel without rebuilding the
  input joins
- treat the mixed-form `data/processed/sentences/year=2021..2024` lane as the
  canonical starting point
- start capital-market or identification execution before the `2025` backbone
  and refreshed input dependencies are explicit

## Dependencies that can wait until later in Track A

These are real, but they do not need to be solved inside the readiness pass.

### Patent refresh

Likely action later:
- place updated PatentsView TSV files in the same external data root
- rerun the existing patent extraction path against the refreshed company lookup

### Capital-market data

Likely action later:
- use WRDS market data, likely CRSP first, for filing-date return work

Reason this is later:
- event-study design should be built on top of a refreshed disclosure backbone,
  not before it

## Readiness conclusion

The repo is ready to begin the `2025` refresh phase, but only in a controlled
way.

The next honest move is:
1. lock the annual filing policy
2. define the staged `2025` source-root approach
3. define the refreshed annual namespace and artifact targets
4. then run the bounded `2025` annual extraction-clean-classification extension

That is the safe way to unblock the empirical lane without reintroducing the
old mixed-form confusion.
