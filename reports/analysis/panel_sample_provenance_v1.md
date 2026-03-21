# Panel Sample Provenance V1

This note records the panel files currently serving as the clean preliminary
delivery inputs.

## Canonical clean panel files

- Merged clean panel:
  - `data/processed/panel/panel_ai_patents_controls_2016_2024_applied_v2_legalnorm_unique.csv`
- Regression-ready estimation sample:
  - `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv`
- Patent counts used in the merged panel:
  - `data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv`
- Controls used in the merged panel:
  - `data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv`

## Row counts

- Merged clean panel: `10,004` firm-years
- Regression-ready estimation sample: `6,152` firm-years

## Why the `AI patents` mean in Table 1 looks high

Table 1 currently uses the regression-ready estimation sample rather than the
broader merged clean panel.

- In the merged clean panel:
  - `649 / 10,004` rows have positive `patents_ai` (`6.49%`)
  - mean `patents_ai = 1.061`
- In the regression-ready sample:
  - `640 / 6,152` rows have positive `patents_ai` (`10.40%`)
  - mean `patents_ai = 1.723`

So the mean is higher for two reasons:

1. the regression-ready sample is more selected than the full merged panel
2. the patent count distribution has a very heavy upper tail

The upper tail is dominated by a few very large patenting firm-years, especially
IBM:

- `IBM 2021: 768`
- `IBM 2022: 698`
- `IBM 2023: 644`
- `IBM 2020: 544`
- `IBM 2024: 433`

This means the right statistic to use when describing sparsity is not the mean
alone. The median remains zero, and the share of positive firm-years is much
smaller than the mean count suggests.

## Delivery implication

We should decide explicitly whether:

- Table 1 is an estimation-sample summary table, or
- Table 1 should be rebuilt on the broader merged clean panel

Both are defensible, but they serve different purposes and should not be mixed.
