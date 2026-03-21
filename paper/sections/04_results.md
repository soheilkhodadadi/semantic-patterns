# Results

This section is intended to be the main landing place for generated outputs and
the surrounding narrative.

Suggested subsections:

## Classifier Benchmark

Summarize held-out performance and the selected preliminary model.

{{ include: paper/generated/snippets/classifier_benchmark_prelim_v1.md }}

{{ include: paper/generated/tables/classifier_benchmark_prelim_v1.md }}

## Extraction and Coverage

Summarize sentence counts, year coverage, and any sample restrictions.

{{ include: paper/generated/snippets/results_status_prelim_v1.md }}

## Descriptive Statistics

Insert generated tables and discuss the distribution of the narrative measures.

{{ include: paper/generated/tables/full_panel_coverage_prelim_v1.md }}

## Regression Results

Insert generated tables, describe the main coefficients, and note any caveats
about sample scope or preliminary status.

The headline discussion in the main text should stay anchored on the binary
future-patent LPM and its closest sample trims. For the main text, prefer
separate actionable-only and speculative-only regressions over crowded omnibus
tables. Count-intensity models and more flexible functional forms are useful
diagnostics, but they should be framed as exploratory unless they materially
sharpen the same story.

{{ include: paper/generated/snippets/regression_results_prelim_v1.md }}

The headline table below reports one focal disclosure variable at a time, with
controls included in the underlying regressions but constants omitted from the
display.

{{ include: paper/generated/tables/regression_headline_prelim_v1.md }}

## Regression Portfolio

Track the broader estimator/sample-split portfolio that benchmarks whether the
headline relationships are stable outside the single baseline specification.

Treat this portfolio as a disciplined appendix ladder. The main text can point
to it for robustness, but the narrative should separate:

1. headline specs: full-sample and trimmed LPM future-patent models
2. robustness specs: logit and share-based variants
3. exploratory appendix specs: raw-count/log-mix OLS models, gap metrics, and
   industry-split subsamples

{{ include: paper/generated/snippets/regression_portfolio_prelim_v1.md }}

{{ include: paper/generated/tables/regression_portfolio_prelim_v1.md }}
