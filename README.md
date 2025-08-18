# Semantic Patterns: Detecting AI-Washing in Corporate Disclosures

## Introduction

This project addresses the growing concern of **AI-washing**—the practice where companies use ambiguous or exaggerated language about artificial intelligence (AI) in their corporate disclosures, particularly in SEC 10-K filings. By leveraging natural language processing (NLP) techniques, this project aims to identify and classify AI-related sentences into meaningful categories that reflect the nature and intent of AI mentions. Understanding these patterns can help investors, regulators, and researchers assess the authenticity and impact of AI claims in financial documents.

## Research Context and Goals

- **Problem:** Companies often mention AI in vague or speculative ways to appear innovative or attract investment, without concrete evidence or initiatives.
- **Objective:** Develop a semantic classification pipeline that distinguishes between **Actionable**, **Speculative**, and **Irrelevant** AI claims in 10-K filings.
- **Outcomes:** Enable large-scale analysis of AI narratives, linking them to financial performance, patenting activity, and litigation risk.

## End-to-End Usage Instructions

### 1. Setup Environment

Create and activate a Python virtual environment, then install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Data Preparation

- Place raw 10-K filings and financial data in `data/raw/`.
- Use provided keyword filters and extraction scripts to generate AI-related sentence datasets.

### 3. Labeling

- Manually label a subset of sentences in `data/validation/hand_labeled_ai_sentences_labeled_cleaned_revised.csv`.
- Labels include:
  - **Actionable:** Concrete AI initiatives (e.g., “We deployed AI to detect fraud.”)
  - **Speculative:** Vague or forward-looking AI mentions (e.g., “We may explore AI in the future.”)
  - **Irrelevant:** General or boilerplate AI references (e.g., “AI is transforming the economy.”)

### 4. Embedding and Centroid Computation

Generate sentence embeddings and compute class centroids:

```bash
python src/classification/embed_labeled_sentences.py
python src/classification/compute_centroids.py
```

### 5. Classification and Evaluation

Classify sentences using centroid similarity and evaluate on held-out data:

```bash
python src/classification/classify_with_centroids.py
python src/tests/evaluate_classifier_on_held_out.py
```

### 6. Analysis and Visualization

Use `src/plots.py` to visualize label distributions, embedding clusters (via PCA/UMAP), and other insights.

---

## Detailed Explanation of Scripts and Their Purposes

| Script                                     | Description                                                                 |
|--------------------------------------------|-----------------------------------------------------------------------------|
| `src/classification/embed_labeled_sentences.py` | Generate SentenceBERT embeddings for labeled AI sentences.                  |
| `src/classification/compute_centroids.py`          | Compute centroid vectors representing each class label from embeddings.    |
| `src/classification/classify_with_centroids.py`    | Classify new AI sentences by comparing embeddings to class centroids.       |
| `src/classification/utils.py`                       | Utility functions for preprocessing, embedding, and classification tasks.  |
| `src/data/`                                         | Scripts for extracting AI-related sentences from raw 10-K filings.         |
| `src/plots.py`                                      | Visualization tools for sentence embeddings, label distributions, and clusters. |
| `src/run_pipeline.py`                               | Top-level script to execute the full pipeline end-to-end.                   |
| `tests/evaluate_classifier_on_held_out.py`         | Evaluate classification accuracy on a held-out validation dataset.          |

---

## Data Flow Diagram (Conceptual)

```
Raw 10-K Filings + Financial Data (data/raw/)
          |
          v
Sentence Extraction & Filtering (src/data/)
          |
          v
Labeled Dataset (data/validation/hand_labeled_ai_sentences_labeled_cleaned_revised.csv)
          |
          v
Embedding Generation (src/classification/embed_labeled_sentences.py)
          |
          v
Centroid Computation (src/classification/compute_centroids.py)
          |
          v
Classification of Unlabeled Sentences (src/classification/classify_with_centroids.py)
          |
          v
Evaluation & Analysis (tests/evaluate_classifier_on_held_out.py, src/plots.py)
```

---

## Configuration Files and Parameters

- **`requirements.txt`**: Lists Python package dependencies required to run the project.
- **Keyword Filters**: Located within `src/data/` scripts; these define AI-related keywords used to extract candidate sentences.
- **Label Definitions**: Found in the labeled CSV file under `data/validation/`; labels can be updated or expanded as needed.
- **Embedding Model**: Uses SentenceBERT by default; can be configured or replaced in `src/classification/utils.py`.
- **Pipeline Parameters**: Thresholds and parameters for classification and evaluation can be adjusted in the respective scripts.

---

## Extending the Project

- Add new sources of AI-related sentences or update keyword filters.
- Replace centroid-based classification with fine-tuned transformer models.
- Incorporate additional metadata (e.g., company sector, time periods) into analyses.
- Use dimensionality reduction techniques (PCA, UMAP) for more advanced visualization.

---

## Contact

**Developer & Maintainer:** Soheil Khodadadi  
**Project Supervisors:** Thomas Walker, Kuntara Pukthuanthong  

For questions, suggestions, or collaboration inquiries, please reach out via email or GitHub.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

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
  _Outputs:_ `data/validation/hand_labeled_ai_sentences_with_embeddings_mpnet.csv`
- [ ] Compute centroids:
  ```bash
  python src/classification/compute_centroids_mpnet.py
  ```
  _Outputs:_ `data/validation/centroids_mpnet.json`

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

  _Inputs:_ `data/validation/held_out_sentences.csv`  
  _Outputs:_ `data/validation/evaluation_results.csv`

### 3) 2024 Classification Run

- [ ] Confirm AI sentence files exist under `data/processed/sec/2024/`  
- [ ] Run batch classification:

  ```bash
  python src/classification/classify_all_ai_sentences.py --years 2024
  ```

  _Outputs:_ `*_classified.txt` files alongside input

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
