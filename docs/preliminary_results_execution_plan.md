# Preliminary Results Execution Plan

Updated: 2026-03-18

## Goal

Deliver a strong preliminary draft with:

- cleaned classified sentence universe for `2016-2024`
- expanded patent and controls coverage
- a regression portfolio, not just a single table
- paper-ready generated narrative, tables, and technical-report detail

## Current Status

### Completed

- `held_out_v2` frozen and benchmarked
- preliminary winner selected: `binary_relevance_then_as_v1`
- cleaned sentence universe built for `2016-2024`
- cleaned classification completed for `2016-2024`
- narrative measures built from the classified universe
- first active-window panel (`2021-2024`) built and baseline regressions run
- paper pipeline now includes benchmark, cleanup, and first regression results
- local methodology and comparison-paper copies are now readable inside `paper/source` and `paper/literature`
- execution and paper-playbook guidance now reflect the local methodology and finance-paper comparison

### Active Constraints

- patents are still likely undercounted because the keyword list is too narrow
- patent calibration now also has a precision constraint: avoid raw `AI` / `ML` substring false positives
- controls currently cover `2018-2024` with the baseline set, but not yet the full `2016-2024` panel
- methodology is now locally available, but several specified controls are still missing from the pipeline
- worktree has many generated artifacts mixed with source changes and needs cleanup discipline

## Execution Lanes

### Lane A: Patent Expansion

Objective:
- broaden AI patent detection with a defensible keyword taxonomy
- make patent extraction resumable and monitorable

Current status:
- `extract_filtered_patents.py` is the preferred extractor
- low-blast instrumentation target identified and implemented:
  - `--keywords-path`
  - `--progress-report`
- expanded candidate keyword file created:
  - `data/metadata/patent_keywords_expanded_v1.txt`
- benchmark tool created:
  - `src/semantic_ai_washing/patents/benchmark_keyword_sets.py`
- current diagnosis:
  - the old patent series was too permissive because raw `AI` / `ML` substring matching generated obvious false positives
  - the newer boundary-aware series is likely too strict
  - `transformer` as a standalone token is too ambiguous and already produced an electrical-transformer false positive
- current calibration files:
  - `data/metadata/patent_keywords_precise_v2.txt`
  - `data/metadata/patent_keywords_applied_v2.txt`
  - `data/metadata/patent_keywords_automation_v2.txt`
  - `data/metadata/patent_keywords_watchlist_v2.txt`

Immediate next steps:
1. benchmark the three keyword tiers on `2024` and inspect matched keywords/examples
2. pick:
   - one main patent series
   - one broader robustness series
3. rerun patents for `2021-2024` with the selected series
4. only then extend patents to `2016-2020`

Working decision rules:
- do not use raw `AI` or `ML` as standalone patent keywords
- prefer phrase-level terms that match patent abstract language
- treat broad/ambiguous automation language as robustness-only unless combined with clearer AI cues

Checkpoint artifacts:
- `reports/data/patent_extraction_progress_*.json`
- `reports/data/patent_keyword_benchmark_*.json`
- `data/processed/patents/ai_patent_counts_filtered_*.csv`
- `data/processed/patents/ai_patent_examples_*.csv`
- `data/processed/patents/patents_diagnostics_*.csv`

### Lane B: Controls Expansion

Objective:
- extend controls from the active window to the full `2016-2024` panel

Current status:
- baseline controls exist for `2018-2024` and support the first panel
- methodology-specified controls still missing:
  - `market_to_book`
  - `firm_age`
  - `sa_index`
  - `hhi`
- explicit methodology extensions to defer for the preliminary draft:
  - `CEO Vega`
  - job-posting AI-skills measures

Immediate next steps:
1. rerun the baseline WRDS controls pull for `2016-2024`
2. add `market_to_book`
3. add `firm_age` and derive `sa_index`
4. defer `hhi` until the sample-wide controls lane is stable
5. update downstream panel/regression allowlists for any new control columns

Checkpoint artifacts:
- `data/interim/controls/controls_by_firm_year_*.csv`
- `reports/panels/preliminary_inputs_manifest_*.json`
- `reports/controls_qc*.md`

### Lane C: Panel Portfolio

Objective:
- build a larger panel and regression portfolio once patents and controls are extended

Current status:
- first `2021-2024` panel and baseline regressions succeeded
- initial result is informative but underpowered

Immediate next steps:
1. rebuild merged panel on the expanded `2016-2024` inputs
2. rerun baseline models
3. run the fuller regression catalog:
   - count models
   - share models
   - dummy models
   - leads `k=0,1,2`
4. add descriptive and trend outputs

Target output families:
- summary statistics
- annual trend figures
- benchmark/model-validation appendix tables
- main regression tables
- robustness tables

### Lane D: Paper and Reporting

Objective:
- keep the manuscript and technical-report layer synchronized with the pipeline

Current status:
- generated manuscript assets and Word export are working
- first regression results are now included

Immediate next steps:
1. refresh generated assets after each major panel rerun
2. add descriptive-statistics and validation-history snippets
3. expand the appendix-style technical detail section

Target content to include:
- heldout construction and review details
- IRR and adjudication details
- benchmark matrix and winner selection logic
- extraction/cleanup coverage
- regression portfolio and robustness notes

### Lane E: Worktree Hygiene

Objective:
- keep source control readable while preserving important generated outputs

Immediate next steps:
1. separate source changes from generated artifacts
2. keep high-value source edits commit-ready
3. keep generated outputs untracked or explicitly ignored where appropriate

## Resumability Protocol

For long-running jobs:

1. every lane should write a progress JSON
2. outputs should use stable filenames with versioned suffixes where needed
3. reruns should accept explicit input/output paths and not assume a single global default
4. partial outputs should be safe to inspect without corrupting the next rerun

## Highest-Leverage Order

1. patent keyword calibration on `2024`
2. baseline controls extension to `2016-2024`
3. patent rerun on `2021-2024` with selected keyword series
4. full panel rebuild
5. regression portfolio expansion
6. paper/report refresh

## User Help That Would Speed Things Up

- flag any must-have tables/figures for the next supervisor update so we can prioritize them
- if possible later, provide a few clearly true-AI patent examples from firms you know well; those would help calibrate keyword recall faster
