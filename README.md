# Semantic Patterns: AI-Washing Detection Pipeline

## Overview

This repository contains a research pipeline for identifying and classifying AI-related language in SEC 10-K filings.  
The workflow extracts AI-related sentences, classifies each sentence as **Actionable**, **Speculative**, or **Irrelevant**, and aggregates sentence-level predictions to firm-year features for downstream analysis.

## Python and Environment

- Python baseline: **3.9+**
- Recommended setup:

```bash
python3.9 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e .
# optional developer tools (pytest + ruff)
pip install -e .[dev]
```

Verify installation:

```bash
python -c "import semantic_ai_washing; print(semantic_ai_washing.__file__)"
```

## Data Layout

Expected locations (relative to repository root):

- Raw/processed filing text root: `data/processed/sec/<year>/...`
- AI keywords: `data/metadata/ai_keywords.txt`
- Validation and centroids: `data/validation/...`

The extraction and classification scripts discover files from these default paths unless overridden by CLI flags.

## Quickstart Pipeline

### 1) Extract AI-related sentences

```bash
python -m semantic_ai_washing.data.extract_ai_sentences \
  --input-dir data/processed/sec \
  --keywords data/metadata/ai_keywords.txt \
  --include-forms 10-K \
  --years 2024
```

Useful options:

- `--limit 1` for a quick smoke run
- `--force` to overwrite existing `*_ai_sentences.txt`
- `--file <path>` to process one filing directly
- `--log-level DEBUG` for verbose extraction diagnostics

### 2) Classify extracted sentences

```bash
python -m semantic_ai_washing.classification.classify_all_ai_sentences \
  --years 2024 \
  --two-stage \
  --rule-boosts \
  --tau 0.07 \
  --eps-irr 0.03 \
  --min-tokens 6
```

### 3) Aggregate to firm-year counts/features

```bash
python -m semantic_ai_washing.aggregation.aggregate_classification_counts
```

## Outputs

- `*_ai_sentences.txt`: extracted AI-related sentences (one sentence per line)
- `*_classified.csv`: per-sentence predicted label and score columns
- `data/final/ai_frequencies_by_firm_year.csv`: firm-year aggregated counts and `log1p` features

## Evaluation and Testing

Held-out classifier evaluation:

```bash
python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out \
  --two-stage \
  --rule-boosts \
  --tau 0.07 \
  --eps-irr 0.03 \
  --min-tokens 6
```

Project QA commands:

```bash
make format
make lint
pytest -q
```

CI runs Ruff + pytest on each push and pull request.

## Project Structure

- `src/semantic_ai_washing/data/`: extraction and data-prep scripts
- `src/semantic_ai_washing/core/`: reusable sentence filtering and classification logic
- `src/semantic_ai_washing/classification/`: batch classification and centroid tooling
- `src/semantic_ai_washing/aggregation/`: firm-year aggregation and merges
- `src/semantic_ai_washing/analysis/`: analysis and reporting scripts
- `tests/`: pytest-based regression tests

## Development Workflow

Use canonical module execution (`python -m semantic_ai_washing...`) for all new work.  
Legacy `src/...` entrypoint scripts are compatibility shims and should not be the default for new documentation or automation.

Branching, PR, and merge conventions are documented in [CONTRIBUTING.md](CONTRIBUTING.md).
