# AI-Washing v3.1 Project Map

Date: 2026-04-22  
Purpose: compact orientation guide for the current paper-upgrade lane.

## 1. What Lives Where

### A. Manuscript source

Current Overleaf-style manuscript source:

- `paper/full paper/ai_washing_v3.0/`

Use this for:

- current LaTeX draft sections
- figure placement checks
- current paper wording and ordering

Do not use it as the source of truth for empirical outputs. It is the writing surface.

### B. Paper-facing generated outputs in the repo

- `paper/generated/`
- new `v3.1` lane: `paper/generated/v3_1/`
- prior paper package: `paper/generated/final_package/20260411_paper_revision_packet_v1/`

Use this for:

- `.docx`, `.tex`, and `.csv` exports that are light enough to keep in the repo
- writer notes and snippets used during drafting
- final packaged assets for paper revision

Treat these as mirrored paper assets, not as the heavy runtime source of truth.

### C. Heavy runtime and non-iCloud assets

Runtime root:

- `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/`

Use this for:

- heavy intermediate datasets
- WRDS pulls
- event-study windows
- monthly return panels
- large test-run folders
- factor downloads and benchmark files

New canonical `v3.1` sublane:

- `/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_1/`

Subfolders:

- `run_registry/`: manifests, sample summaries, per-run metadata
- `test_runs/`: one folder per new paper test
- `factor_inputs/`: Ken French and similar benchmark inputs
- `audit/`: cross-test diagnostics and comparison notes
- `paper_assets/`: optional mirrored heavy assets that should not sit in iCloud

### D. Analysis code

Canonical package:

- `src/semantic_ai_washing/analysis/`

Current backbone builders:

- `build_refresh_ever_speaker_panel.py`
- `build_full_sample_wrds_backbone.py`
- `build_filing_event_spine.py`
- `build_event_return_windows.py`
- `run_filing_event_regressions.py`

Paper-test drivers:

- `src/semantic_ai_washing/analysis/publication_runs/`

This is the intended home for one-driver-per-test paper runs.

### E. Historical planning and paper notes

- `paper/guides/AI_Washing_Codex_Master_Run_Sheet_v1.md`
- `paper/guides/AI_Washing_Legacy_Rerun_Queue_20260411.md`
- `paper/guides/finance_paper_playbook.md`

These remain useful context, but the active market-identification plan now lives in:

- `paper/guides/AI_Washing_v3_1_Publication_Roadmap_20260422.md`

## 2. Current Canonical Datasets

### Annual panel

- `data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet`

### Filing-event estimation sample

- `data/processed/panel/filing_event_estimation_sample_hybrid_api_a_conf49_v1.parquet`

### Daily filing-event returns

- `data/interim/market/filing_event_returns_daily_hybrid_api_a_conf49_v1.parquet`

### Monthly CRSP returns

- `data/interim/market/wrds_crsp_msf_full_sample_v1.parquet`
- `data/interim/market/wrds_crsp_msi_full_sample_v1.parquet`

### Annual market features

- `data/interim/market/annual_market_features_ever_speaker_2016_2025_hybrid_api_a_conf49_v1.csv`

## 3. Current Pain Points and the Fix

### Pain point 1: the same result family exists in several places

Example:

- raw heavy run output in DataWork
- mirrored `.csv` / `.docx` / `.md` in `paper/generated/`
- final selected asset in the paper package

### Fix

For `v3.1`, treat the layers as follows:

1. **source of truth for heavy empirical output** = `DataWork/.../derived/v3_1/test_runs/`
2. **source of truth for paper-facing export** = `paper/generated/v3_1/`
3. **source of truth for manuscript wording** = `paper/full paper/ai_washing_v3.0/` until a later draft lane is created

### Pain point 2: historical and active tests are mixed together

### Fix

Do not delete old files. Instead:

- keep existing `test_01` to `test_08` and legacy reruns as frozen history;
- add new `v3.1` market-strengthening tests as new test families starting at `test_09`.

### Pain point 3: run IDs are understandable in isolation but hard to compare across waves

### Fix

Use a strict run-ID scheme for all new work:

- `YYYYMMDD_aiw_v3_1_<test_id>_<spec_id>_v1`

## 4. Naming and Versioning Rules

### Test family IDs for the new wave

- `test_09_factor_adjusted_alpha`
- `test_10_adjusted_post_filing_returns`
- `test_11_mismatch_component_horse_race`
- `test_12_predictive_return_controls`
- `test_13_pre_post_event_path`
- `test_14_first_mismatch_onset`
- `test_15_matched_ai_talking_sample`
- `test_16_construct_variant_screen`
- `test_17_real_outcome_dynamics`
- `test_18_financing_incentives_refresh`

### Output contract per run

Minimum per-run contents:

- `dataset_summary.json`
- `main_table.csv`
- `main_table.tex`
- `main_table.docx`
- `result_notes.md`
- `writer_packet.json`
- `run_manifest.json`

Optional when relevant:

- `main_figure.png`
- `main_figure_series.csv`
- `comparison_to_prior_run.md`

## 5. What Is Canonical Now

If there is a conflict, prefer these in order:

1. the latest `v3.1` roadmap in `paper/guides/`
2. the current canonical dataset paths listed above
3. the new `v3.1` DataWork lane for heavy outputs
4. the repo `paper/generated/v3_1/` lane for paper-facing exports
5. historical `20260411` assets only as reference or comparison

## 6. Practical Working Rules

### When running new empirical work

- do not write new heavy artifacts into the older mixed-output roots if a `v3.1` path exists;
- do not overwrite `20260411` paper assets;
- do not treat the manuscript folder as a data store;
- keep one driver per test family;
- keep writer packets close to the run.

### When reading results during drafting

Use this order:

1. latest run manifest in DataWork
2. result notes / writer packet
3. mirrored table or figure in `paper/generated/v3_1/`
4. final selected paper package asset

## 7. Recommended Near-Term Cleanup Without Disruption

These are safe and useful. They do not require destructive moves.

1. keep all current historical outputs in place;
2. route all new `v3.1` tests into the new DataWork lane;
3. route new paper-facing exports into `paper/generated/v3_1/`;
4. once the next wave of tests is complete, build a fresh final package rather than editing the old one in place.

## 8. Immediate Operational Next Step

After this map, the next concrete step is:

- stage factor data in `DataWork/.../derived/v3_1/factor_inputs/`
- implement `test_09_factor_adjusted_alpha`
- use its verdict to decide how aggressively to pursue the rest of the market-identification sequence
