# Publication Runs

This package is the intended home for one-driver-per-test paper-grade empirical
runs.

Naming rule:
- `test_01_mismatch_surge`
- `test_02_filing_date_car`
- `test_03_post_filing_drift`
- `test_04_portfolio_sorts`
- `test_05_size_heterogeneity`
- `test_06_real_effects`
- `test_07_chatgpt_did`
- `test_08_financing_valuation`
- `validation_refresh`

Operational rule:
- each test family should own its own driver module
- each run should emit a dataset summary, main output object, writer packet,
  and run manifest
- heavy mutable artifacts should go to the DataWork runtime root, not the
  iCloud-backed repo tree
