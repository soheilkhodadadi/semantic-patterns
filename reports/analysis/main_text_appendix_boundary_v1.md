# Main-Text vs Appendix Boundary

Date:
- `2026-03-20`

Status:
- preliminary delivery-design boundary

## Principle

Main text should answer the paper’s core preliminary question with the smallest
set of clean, interpretable, persuasive artifacts.

Appendix should defend the main text:

- alternative estimators
- extra fixed-effect ladders
- extra sample trims
- technical validation details
- alternative variable definitions

Main text should not become a holding area for every interesting regression.

## Main Text

### Table 1

- `Summary Statistics and Coverage`

Why main text:
- defines the sample
- establishes the scale of the measures
- orients the reader before any regression table
- should be anchored on the ever-speaker annual panel rather than the narrower speaking-only sample

### Table 2

- `AI Patent Timing and Alignment on the Ever-Speaker Panel`

Why main text:
- first indispensable main-text regression table on the broader panel
- directly links narrative composition to AI patent outcomes at multiple calendar-time horizons
- should use AI patent outcomes rather than generic patent incidence

### Table 3

- `Disclosure Composition and AI Patent Timing`

Why main text:
- shows whether decomposition into actionable and speculative-only disclosure adds signal beyond broad AI-focus intensity
- keeps the core composition result separate and readable

### Table 4

- `Patent-Timing Matrix by Disclosure Type`

Why main text:
- mirrors the literature-style timing layout more closely
- shows the full `t-2` through `t+2` pattern with FE/sample variants in columns
- helps the reader see whether disclosure types are backward-looking, contemporaneous, or forward-looking

### Table 5

- `Credibility Metrics`

Why appendix:
- it helps benchmark auxiliary credibility-style constructs
- but it is exploratory relative to the methodology-aligned `A_S x PatentMismatch` design
- it should no longer compete with the main-text ladder

### Table 6

- `A/S Ratio, Patent Mismatch, and Future AI Patenting`

Why main text:
- this is the first table that directly matches the methodology's core AI-washing specification
- it tests whether credible AI disclosure loses predictive power in mismatch years
- it is more central to the paper's stated construct than the exploratory credibility bundle

### Table 7

- `Firm-Level Determinants of PatentMismatch`

Why candidate main text:
- it answers the next natural question after the mismatch tables and figures: who exhibits mismatch
- it mirrors the literature's determinants step
- it should remain compact and descriptive rather than becoming a mechanism section

Why keep reduced variants nearby:
- `Table 7C / 7D` recover most of the baseline firm sample
- they are useful for deciding whether the full multivariate column is substantively informative or just overly sparse

### Main Figures

- time series of AI disclosure composition
- industry heterogeneity
- patent-alignment / mismatch visualization

## Appendix

### Technical Validation

- held-out benchmark details
- model benchmark matrix
- IRR / adjudication details
- sentence cleanup diagnostics
- keyword construction details

### Estimator Robustness

- extensive-margin `any AI patent` timing models
- logit variants
- Poisson / count models
- alternative functional forms

### Additional Design Sensitivity

- extra FE variants beyond the compact ladder
- extra SIC / industry splits
- high-tech only or special-sample splits if not needed in main text

### Alternative Construct Definitions

- `SpecMinusAct`
- alternative walk / talk analogues if later added
- mismatch variants once implemented

## Current Boundary Decision

As of this preliminary delivery stage:

- `Table 1` is main text
- `Table 2` is main text
- `Table 3` is main text as the composition-timing companion
- `Table 4 / Table 4B` are candidate main-text timing-matrix tables if they remain readable
- `Table 6 / Table 6B` are promoted main-text methodology-aligned AI-washing tables
- `Table 7 / Table 7B` are candidate main-text determinants tables if they remain readable and do not over-crowd the results section
- `Table 5 / Table 5B` are appendix-only exploratory credibility tables
- the current conditional validation table from the speaking-only panel moves to the appendix
- FE ladders beyond the compact timing-matrix comparison should not enter the paper until we decide whether they clarify or distract
- count models, Poisson models, and richer appendix-style robustness remain out of the main text for now
