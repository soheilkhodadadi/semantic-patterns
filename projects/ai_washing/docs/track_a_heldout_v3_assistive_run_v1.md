# Track A Held-Out v3 Assistive Prelabel Run v1

## Summary

- Benchmark lane: `held_out_v3`
- Review sheet: `data/validation/held_out_v3/held_out_sentences_v3_review_sheet.csv`
- Rows: `177`
- Assistive model selected for scale-up: `gpt-5-mini`
- Status: full assistive prelabel pass completed

## Model selection outcome

Two bounded smoke runs were executed before the full pass.

- `gpt-5` failed the strict JSON contract on the 10-row smoke sample.
- `gpt-5-mini` completed the 10-row smoke sample successfully.

This made `gpt-5-mini` the defensible assistive model for the full review sheet.

## Runtime issues found and fixed

Two real runtime failure modes appeared during the live scale-up:

1. intermittent malformed or empty structured outputs after otherwise successful API calls
2. transient OpenAI Responses API `500` errors

Both were patched with low-blast-radius resilience changes:

- row-level retry for parse and validation failures in the assistive prelabel batch
- retry of retryable HTTP failures in the shared Responses transport

After those changes, the full `177`-row pass completed successfully.

## Final artifacts

- full review sheet with assistive labels:
  - `data/validation/held_out_v3/held_out_sentences_v3_review_sheet.csv`
- final live run report:
  - `reports/final/ai_washing_heldout_v3_assistive_prelabel_live_gpt5mini_report_v1.json`
- final live progress:
  - `reports/final/ai_washing_heldout_v3_assistive_prelabel_live_gpt5mini_progress_v1.json`
- smoke reports:
  - `reports/final/ai_washing_heldout_v3_smoke10_gpt5_report_v1.json`
  - `reports/final/ai_washing_heldout_v3_smoke10_gpt5_progress_v1.json`
  - `reports/final/ai_washing_heldout_v3_smoke10_gpt5mini_report_v1.json`
  - `reports/final/ai_washing_heldout_v3_smoke10_gpt5mini_progress_v1.json`

## Assistive label distribution

- `Irrelevant`: `87`
- `Actionable`: `66`
- `Speculative`: `24`

All assistive confidence values are currently `high`.

## Comparison to legacy labels

- agreement with `legacy_candidate_label`: `82 / 177`
- agreement with `legacy_assistive_label`: `158 / 177`

This is directionally what we expected:

- strong continuity with the more recent assistive lane
- meaningful cleanup relative to older rubric-era candidate labels

## Next step

Use the assistive labels only as review support.

The next operational step is:

1. manually review and correct the `177` rows
2. freeze `held_out_v3`
3. rerun the local classifier candidates on the frozen benchmark
