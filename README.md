# Semantic Patterns: Detecting AI-Washing in Corporate Disclosures

## Introduction

This project addresses the growing concern of **AI-washing**—the practice where companies use ambiguous or exaggerated language about artificial intelligence (AI) in their corporate disclosures, particularly in SEC 10-K filings. By leveraging natural language processing (NLP) techniques, this project aims to identify and classify AI-related sentences into meaningful categories that reflect the nature and intent of AI mentions. Understanding these patterns can help investors, regulators, and researchers assess the authenticity and impact of AI claims in financial documents.

## Research Context and Goals

- **Problem:** Companies often mention AI in vague or speculative ways to appear innovative or attract investment, without concrete evidence or initiatives.
- **Objective:** Develop a semantic classification pipeline that distinguishes between **Actionable**, **Speculative**, and **Irrelevant** AI claims in 10-K filings.
- **Outcomes:** Enable large-scale analysis of AI narratives, linking them to financial performance, patenting activity, and litigation risk.

## End-to-End Usage Instructions (Quickstart)

> **Stack**: Python 3.10+, sentence-transformers (MPNet), PyTorch, pandas.
>
> **Data roots** (relative to repo):
>
> - Raw filings: `data/raw/edgar/10k/<year>/...`
> - Extracted AI sentences: `data/processed/sec/<year>/*_ai_sentences.txt`
> - Validation labels: `data/validation/hand_labeled_ai_sentences_labeled_cleaned.csv`
> - MPNet outputs: `data/validation/hand_labeled_ai_sentences_with_embeddings_mpnet.csv`, `data/validation/centroids_mpnet.json`

### 1) Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Generate MPNet embeddings & centroids (labels → vectors → class means)

```bash
python src/classification/embed_labeled_sentences_mpnet.py
python src/classification/compute_centroids_mpnet.py
```

This writes `centroids_mpnet.json` that the classifier will load.

### 3) Classify AI sentences across filings

```bash
# classify only 2024
python src/classification/classify_all_ai_sentences.py --years 2024

# classify multiple years (example)
python src/classification/classify_all_ai_sentences.py --years 2021 2022 2023 2024
```

Each `*_ai_sentences.txt` gets a sibling `*_classified.txt` with predicted labels and scores.

### 4) Evaluate on held‑out validation set

```bash
python src/tests/evaluate_classifier_on_held_out.py
```

Reads `data/validation/held_out_sentences.csv`, prints accuracy, and writes `data/validation/evaluation_results.csv`.

### 5) (Optional) Aggregate to firm‑year afterward

Use the aggregation utilities in `src/aggregation/` once 2024 (and additional years) are classified to produce firm‑year counts and shares (Actionable/Speculative/Irrelevant). See the *Workflow & Stages* section below.

## Key Scripts & What They Do

- `src/classification/embed_labeled_sentences_mpnet.py` — Encode labeled sentences with `all-mpnet-base-v2`; saves a CSV with embeddings.
- `src/classification/compute_centroids_mpnet.py` — Compute per‑label mean vectors (centroids) from MPNet embeddings; saves `centroids_mpnet.json`.
- `src/core/classify.py` — Loads MPNet + centroids and exposes `classify_sentence()` used everywhere.
- `src/classification/classify_all_ai_sentences.py` — Batch classifies every `*_ai_sentences.txt` under `data/processed/sec/<year>/` and writes `*_classified.txt`.
- `src/tests/evaluate_classifier_on_held_out.py` — Evaluates the MPNet classifier on `held_out_sentences.csv` and writes a CSV of predictions.
- `src/aggregation/aggregate_classification_counts.py` — Rolls sentence‑level classifications into firm‑year counts/shares for A/S/I.
- `src/analysis/summarize_classification_counts.py` — Quick summaries/plots (e.g., distribution by year/industry).
- `src/classification/utils.py` — Helpers for loading centroids and shared logic.

## Workflow & Stages (Conceptual)

### Stage 1 — NLP & Classification

1) Raw filings → AI sentence extraction (regex + spaCy) → `data/processed/sec/<year>/*_ai_sentences.txt`  
2) Labeled validation set → MPNet embeddings → centroids (A/S/I)  
3) Apply MPNet+centroids to classify all extracted sentences → `*_classified.txt`  
4) Held‑out evaluation (target ≥ 80% accuracy)

**Stage 2 — Integration (IDs, patents, controls)**
5) Build CIK↔ticker↔GVKEY crosswalk, derive industries  
6) Aggregate sentences to firm‑year A/S/I counts & shares  
7) Retrieve/aggregate patent counts (AI vs total)  
8) Pull Compustat controls via WRDS and merge into panel

**Stage 3 — Analysis & Delivery**
9) Feature engineering (AI_intensity, shares, SpecMinusAct, Δyear)  
10) Baseline & FE regressions; clustered SEs  
11) Export tables/figures + delivery memo

### One‑line diagram

```text
Raw Filings → AI Sentence Extraction → MPNet Centroids → Sentence Classification →
Firm‑Year Aggregation → Crosswalk/Patents/Controls Merge → Analysis → Tables/Delivery
```

## Configuration Files and Parameters

- **`requirements.txt`**: Lists Python package dependencies required to run the project.
- **Keyword Filters**: Located within `src/data/` scripts; these define AI-related keywords used to extract candidate sentences.
- **Label Definitions**: Found in the labeled CSV file under `data/validation/`; labels can be updated or expanded as needed.
- **Embedding Model**: Uses `sentence-transformers/all-mpnet-base-v2` by default; configured in `src/core/classify.py`.
- **Pipeline Parameters**: Thresholds and parameters for classification and evaluation can be adjusted in the respective scripts.

---

## Stage 1 — NLP Upgrade Checklist (branch: `stage1-nlp-upgrade`)

Use this checklist to track progress on upgrading to MPNet embeddings and running the end-to-end classification.

### Branch setup

- [ ] Create and switch to branch:

  ```bash
  git checkout main && git pull origin main
  git checkout -b stage1-nlp-upgrade
  ```

- [ ] Commit and push milestones:

  ```bash
  git add -A && git commit -m "Describe milestone"
  git push -u origin stage1-nlp-upgrade
  ```

### 1) Embeddings & Centroids

- [ ] Run MPNet embedding script:

  ```bash
  python src/classification/embed_labeled_sentences_mpnet.py
  ```

  *Outputs:* `data/validation/hand_labeled_ai_sentences_with_embeddings_mpnet.csv`
- [ ] Compute centroids:

  ```bash
  python src/classification/compute_centroids_mpnet.py
  ```

  *Outputs:* `data/validation/centroids_mpnet.json`

- [ ] Verify `src/core/classify.py` uses:
  - `MODEL_NAME="sentence-transformers/all-mpnet-base-v2"`
  - `CENTROIDS_PATH="data/validation/centroids_mpnet.json"`

### 2) Held‑out Evaluation (target ≥ 80% accuracy)

- [ ] Ensure `src/tests/evaluate_classifier_on_held_out.py` imports:

  ```python
  from core.classify import classify_sentence
  ```

- [ ] Evaluate:

  ```bash
  python src/tests/evaluate_classifier_on_held_out.py
  ```

  *Inputs:* `data/validation/held_out_sentences.csv`  
  *Outputs:* `data/validation/evaluation_results.csv`

### 3) 2024 Classification Run

- [ ] Confirm AI sentence files exist under `data/processed/sec/2024/`  
- [ ] Run batch classification:

  ```bash
  python src/classification/classify_all_ai_sentences.py --years 2024
  ```

  *Outputs:* `*_classified.txt` files alongside input

### 4) QA Gate

- [ ] Held‑out accuracy ≥ 80%, confusion matrix looks reasonable  
- [ ] 2024 fully classified with minimal errors  
- [ ] Record metrics (accuracy, F1, thresholds) in commit message

### 5) Merge & Tag

- [ ] Create PR `stage1-nlp-upgrade → main`  
- [ ] Merge after review and tag release:

  ```bash
  git checkout main && git pull origin main
  git merge --no-ff stage1-nlp-upgrade
  git push origin main
  git tag -a v1-nlp -m "Stage 1 NLP upgrade (MPNet centroids, 2024 run)"
  git push origin v1-nlp
  ```
