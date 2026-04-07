# AI-Washing Track A Filing-Date and Patent-Window Audit V1

## Purpose

This note records the current state of:
- filing-date availability in the refreshed SEC sentence pipeline
- patent timing in the current annual panel
- the exact gap between the current annual patent scaffold and the intended
  `t-2` to `t+2` timing design

It is a Track A scoping artifact, not a final empirical design decision.

## Inputs reviewed

Local repo/data inputs:
- `data/metadata/available_filings_index_2025_refresh_v1.csv`
- `data/processed/sentences_refresh_2025_v1/year=2025/ai_sentences.parquet`
- `data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv`
- `data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv`
- `projects/ai_washing/src/ai_washing_member/data/index_sec_filings.py`
- `projects/ai_washing/src/ai_washing_member/data/extract_sentence_table.py`
- `src/semantic_ai_washing/aggregation/build_ever_speaker_annual_panel.py`

## Filing-date findings

### 1. Exact filing dates are recoverable now

The SEC filename pattern already encodes the filing date as the leading
`YYYYMMDD` token.

Examples from the refreshed index:
- `20250313_10-K_edgar_data_1000209_0000950170-25-038693.txt`
- `20250225_10-K_edgar_data_1000228_0001000228-25-000014.txt`

So the event date for a first filing-date event study can be recovered from:
- `available_filings_index_2025_refresh_v1.csv`
- or `source_file` inside extracted sentence tables

### 2. Filing dates are not yet promoted as a dedicated downstream field

The current extracted sentence tables carry:
- `source_file`
- `source_year`
- `source_quarter`
- `source_form`
- `source_cik`

They do **not** carry a dedicated `filing_date` column.

Implication:
- annual disclosure work is fine as-is
- event-study work should promote `filing_date` into an event-study scaffold or
  an event-ready firm-filing table instead of repeatedly reparsing it from the
  filename

### 3. We do not need CRSP or Compustat to obtain filing dates

For the 10-K event-study lane, the filing date should come from the SEC source
itself, not from the market-data side.

Recommended rule:
- treat SEC/EDGAR-derived filing dates as the canonical event dates
- use CRSP only for returns and security-market variables
- use Compustat/CCM only for controls and firm identifiers

## Patent-window findings

### 4. The current annual panel is calendar-year, not filing-date-relative

The current ever-speaker panel uses annual firm-year patent counts and then
creates:
- `patents_ai_lag1`
- `patents_ai_lag2`
- `patents_ai_lead0`
- `patents_ai_lead1`
- `patents_ai_lead2`

by shifting annual counts within firm.

That is a clean annual design, but it is **not** the same thing as measuring
patents within two years before or after an exact 10-K filing date.

### 5. The current patent series is left-censored for `t-2`

The active patent file currently spans:
- min year: `2016`
- max year: `2024`

Current active patent artifact:
- `data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv`

Because the annual panel trims the patent table to the panel years before
constructing lags, the early sample loses usable prior-year timing:
- `2016`: `lag1` and `lag2` are structurally missing
- `2017`: `lag2` is structurally missing

Observed in the current panel:
- `2016` rows have `patents_ai_lag1 = NaN` and `patents_ai_lag2 = NaN`
- `2017` rows have `patents_ai_lag2 = NaN`

### 6. If we want valid annual `t-2` timing from the start of the sample, we need pre-2016 patent years

Minimum correction for the annual panel:
- rebuild the patent series to cover at least `2014-2025`
- keep those years available during lag/lead construction
- only trim the regression sample after the lags/leads are formed

That is the cleanest way to preserve the current annual design while fixing the
front-of-sample censoring.

## Recommended decision for Track A

### Short version

Use two separate timing lanes:

1. Annual disclosure-validation lane
- keep the annual panel design
- extend patents to `2014-2025`
- rebuild lags/leads after extending the patent window

2. Filing-date market-reaction lane
- derive exact `filing_date` from SEC filenames/index rows
- build a dedicated event-ready filing table
- do not force the entire annual sentence backbone to become event-date-native

This keeps the annual paper backbone stable while making the event-study lane
precise enough.

## Immediate next tasks

1. Add a small helper or event-ready scaffold that promotes `filing_date` from
   the indexed SEC filename.
2. Refresh the patent series with a source window that includes `2014-2025`.
3. Rebuild the annual ever-speaker panel only after the widened patent window is
   available.
4. Keep the first event-study build as a separate dataset keyed on exact filing
   dates.

## Bottom line

We are not blocked on filing dates.

The real timing issue is on the patent side:
- the current annual panel uses calendar-year patent timing
- the early sample is left-censored for `t-2`

So the next correction is not to redesign the entire disclosure pipeline.
It is to:
- widen the patent source window
- preserve filing dates explicitly for the later event-study lane
