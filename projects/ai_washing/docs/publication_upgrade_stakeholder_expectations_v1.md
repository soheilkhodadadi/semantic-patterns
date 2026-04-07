# AI-Washing Publication Upgrade Stakeholder Expectations V1

## Purpose

This note records the next-phase stakeholder expectations for the AI-washing
project after the preliminary results and restructure phase.

It is project-scoped on purpose.
The goal is to keep the publication-upgrade lane separate from the earlier
preliminary-results roadmap while preserving continuity with the earlier
evidence base.

## Source

- primary source: Kuntara email provided on `2026-04-06`
- supporting sources:
  - `docs/director/stakeholder_expectations.md`
  - `docs/director/proposal_methodology.md`
  - `paper/source/AI Washing - SK - 2026.03.25.pdf`

## Main expectations

### 1. Lead with the surprising result

The current paper does not yet lead with a finding that creates enough surprise
for a stronger journal target.

Current likely candidate:
- the acceleration of disclosure-patent mismatch in the later sample years

Implication:
- the next paper version should be framed around the strongest unexpected result,
  not only around the classifier and validation design

### 2. Quantify economic stakes

The project now needs evidence that AI-washing matters for real decisions and
capital allocation.

Required direction:
- test whether low-credibility AI disclosure is rewarded, mispriced, or
  otherwise connected to capital-market outcomes

Candidate outcomes:
- abnormal returns around filing dates
- valuation or multiple differences
- analyst coverage or response
- equity-financing or market-access consequences if feasible

### 3. Add identification

The current design is mainly predictive.
The next phase should introduce a more credible identification strategy.

Most obvious candidate:
- the release of ChatGPT in late 2022 as a disclosure-cost shock or salience
  shock

Alternative candidates:
- relevant disclosure or regulatory events if they offer a cleaner design

### 4. Refresh the data window

The project should no longer stop at 2024 just because that was the previous
data cut.

Expected next data move:
- ingest 2025 10-K filings
- rerun extraction and classification on the refreshed window
- decide whether 2025 is in the main specification set or a near-term extension

### 5. Strengthen classifier credibility

The current classifier performance is usable for preliminary results but not
ideal for a stronger journal submission.

Required direction:
- improve accuracy if feasible
- and, regardless, run robustness designs that reduce dependence on the full
  model output

Candidate robustness directions:
- human-labeled-only subset
- high-confidence subset
- threshold-based robustness
- sensitivity of results to classification uncertainty

### 6. Fix presentational vulnerabilities

These are not pure repo-engineering tasks, but they do affect what outputs the
project should generate.

Expected improvements:
- explain or neutralize negative adjusted `R^2` flags
- make the literature positioning sharper and more selective
- provide before/after examples and stronger differentiation

## Project-level hard gates for the next phase

### Scientific gates

- do not let the project remain only a measurement/prediction paper
- add at least one serious economic-stakes test
- add at least one serious identification design candidate

### Data gates

- 2025 filing integration plan must be explicit
- refreshed extraction/classification run must be reproducible
- any new market-data dependency must be documented before analysis begins

### Model-credibility gates

- rerun held-out and/or high-confidence robustness before treating new findings
  as stable
- do not rely only on the aggregate classified panel without uncertainty-aware
  checks

### Paper-package gates

- lead result must be explicit
- market relevance must be quantified
- identification language must be defensible, not aspirational

## What this means for execution

The next AI-washing phase is not:
- another restructure pass
- another pure pipeline pass
- another classifier-only pass

It is:
- a publication-upgrade phase with new economics-facing requirements

## Bottom line

The earlier roadmap validated the methodology enough to produce preliminary
results.

The new stakeholder expectation is different:
- turn the project into a stronger paper by adding economic stakes,
  identification, refreshed data, and stronger robustness around the model.
