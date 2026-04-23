# AI-Washing Track A Master Run Execution Posture V1

Date:
- `2026-04-11`

Status:
- preparation-phase execution note
- intended to operationalize `paper/guides/AI_Washing_Codex_Master_Run_Sheet_v1.md`
- focused on storage posture, run naming, output discipline, and rerun safety

## Purpose

This note answers four practical questions before the next empirical wave starts:

1. where should heavy mutable runtime artifacts live?
2. where should light paper-facing outputs live?
3. how should each test be named and saved so reruns stay readable?
4. how should future scripts be organized so a changed specification does not
   require archaeology?

## The core problem we just observed

The repo-local `.venv` is currently unreliable for heavy batch work because the
project lives inside an iCloud-managed tree.

Observed symptom:
- tiny package files inside `.venv` intermittently block on read
- this affects imports, long runs, and even trivial file reads
- the failure mode is not limited to one package or one script

Operational implication:
- the repo should remain the source of truth for code, specs, and light outputs
- heavy mutable runtime artifacts should move to a non-iCloud path
- runtime virtual environments for heavy empirical runs should also live outside
  the repo tree

## Execution split to use going forward

### 1. Repo remains the control tower

Keep these in the repo:
- code
- guides
- plans
- run manifests
- light reports
- paper-ready exports
- writer packets
- small CSV summaries that are useful for versioned review

Canonical repo surfaces:
- `src/semantic_ai_washing/`
- `projects/ai_washing/docs/`
- `projects/ai_washing/configs/`
- `paper/generated/`
- `reports/analysis/`

### 2. DataWork becomes the heavy runtime root

Use:
- `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing`

for:
- runtime venvs
- large intermediate panels
- large event-study windows
- long-horizon return panels
- repeatable test-run outputs
- logs and temporary products

This is the right split because:
- heavy files are the ones iCloud fights most aggressively
- heavy reruns are the part most likely to be repeated with new specs
- code and specs are relatively small and should remain versioned in the repo

## Canonical DataWork layout

The runtime root should be:

```text
/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/
  runtime_venvs/
  logs/
  tmp/
  raw/
    sec/
    wrds/
    patents/
    external/
  derived/
    panels/
    event_study/
    returns/
    tables/
    figures/
    test_runs/
      test_01_mismatch_surge/
      test_02_filing_date_car/
      test_03_post_filing_drift/
      test_04_portfolio_sorts/
      test_05_size_heterogeneity/
      test_06_real_effects/
      test_07_chatgpt_did/
      test_08_financing_valuation/
      validation_refresh/
```

## Canonical repo export layout

Paper-facing light outputs should stay in the repo under:

```text
paper/generated/
  tables/
  figures/
  latex/
  writer_packets/
```

Interpretation:
- DataWork holds heavy run-state and large intermediate artifacts
- repo `paper/generated/` holds the lighter outputs that are read, diffed,
  cited, and eventually moved into Word or LaTeX

## Naming convention

### Test id

Each empirical family gets one stable test id:
- `test_01_mismatch_surge`
- `test_02_filing_date_car`
- `test_03_post_filing_drift`
- `test_04_portfolio_sorts`
- `test_05_size_heterogeneity`
- `test_06_real_effects`
- `test_07_chatgpt_did`
- `test_08_financing_valuation`
- `validation_refresh`

### Run id

Each execution gets one run id:

```text
YYYYMMDD_<sample>_<variant>_vN
```

Examples:
- `20260411_hybrid_api_a_conf49_main_v1`
- `20260412_hybrid_api_a_conf49_market_model_v1`
- `20260412_hybrid_api_a_conf49_smallcap_split_v1`

### File naming rule

Within each run directory, prefer stable semantic names over ad hoc names:
- `dataset_summary.json`
- `result_notes.md`
- `writer_packet.md`
- `writer_packet.json`
- `table_main.csv`
- `table_main.md`
- `table_main.tex`
- `figure_main.png`
- `figure_main.pdf`
- `run_manifest.json`

## Script organization rule

From this point forward, new paper-grade empirical runs should not be built as
one giant omnibus script.

Use:
- one driver module per test family
- one run should map to one script family and one output contract

Preferred future package home:
- `src/semantic_ai_washing/analysis/publication_runs/`

Why:
- Kuntara-style reruns become easy
- changed specs stay local to the test family
- table and writer-packet generation can be kept adjacent to the test itself

## Minimum output contract for every run

This mirrors the master run sheet and is non-optional:

1. `dataset_summary.json`
2. main output object:
   - `table_main.*` and/or `figure_main.*`
3. `result_notes.md`
4. `writer_packet.md`
5. `run_manifest.json`

The writer packet should always include:
- sample definition
- unit of observation
- dependent variable
- key regressors
- control set
- fixed effects
- clustering
- weighting
- benchmark model if returns are used
- exact N
- key coefficient or spread
- one economic magnitude sentence
- main-text / appendix / discard recommendation

## Export posture: Word now, LaTeX-ready always

Current paper surface:
- Word remains acceptable as the final editing surface

But all new runs should also emit a LaTeX-ready object when feasible:
- `table_main.tex` for regression and summary tables
- plain CSV next to it for auditability
- Markdown writer packet for human review

This gives us:
- Word compatibility now
- Overleaf-friendly migration later
- lower rewrite cost once the paper settles

## Immediate implementation order

### Phase 1. Preparation
1. bootstrap the DataWork runtime layout
2. create a runtime venv outside the repo tree
3. freeze the test registry and naming convention
4. add writer-packet template and export directories

### Phase 2. Wave 1 runs
1. `test_01_mismatch_surge`
2. `test_02_filing_date_car`
3. `test_03_post_filing_drift`
4. `test_05_size_heterogeneity`
5. `test_07_chatgpt_did`

### Phase 3. Wave 2 and validation
1. `test_06_real_effects`
2. `test_08_financing_valuation`
3. `test_04_portfolio_sorts`
4. `validation_refresh`

## What the user can do on their side

Helpful user actions:
- keep `/Users/soheilkhodadadi/DataWork` as the canonical non-iCloud heavy-data
  root
- if possible, avoid relying on repo-local `.venv` for empirical batch work
- if desired later, remove and rebuild `.venv` outside the iCloud tree rather
  than repeatedly fighting partial hydration

## Bottom line

The paper no longer needs more brainstorming.

It needs a durable run system:
- repo for code/specs/light outputs
- DataWork for heavy runtime artifacts
- one script family per test
- one run manifest per execution
- one writer packet per result

That is the preparation posture that will let us scale the master run sheet
without making the repo unreadable.
