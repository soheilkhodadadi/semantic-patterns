# Semantic Patterns: Detecting AI-Washing in Corporate Disclosures

<a target="_blank" href="https://cookiecutter-data-science.drivendata.org/">
    <img src="https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter" />
</a>

This project aims to identify and classify AI-related language in SEC 10-K filings to detect patterns of **"AI-washing"**—where companies mention artificial intelligence in vague or misleading ways. Using natural language processing (NLP), the project builds tools to detect **Actionable**, **Speculative**, and **Irrelevant** AI claims and study their relationship with financial behavior and investor response.

---

## 🧠 Research Goals

- Extract AI mentions from corporate filings using keyword-based filters
- Manually label a gold standard dataset of AI-related sentences
- Train a semantic classifier using SentenceBERT embeddings and class centroids
- Classify all AI sentences across thousands of 10-Ks
- Link AI narrative patterns to stock returns, patenting behavior, and litigation

---

## 📁 Project Structure

This project follows the [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/) structure.

```
semantic-patterns/
├── data/
│   ├── raw/                   # Original 10-K filings and CRSP/Compustat data
│   ├── processed/             # Final structured AI sentence datasets
│   ├── validation/            # Hand-labeled sentence files, embeddings, centroids
│
├── models/                    # (Optional) Serialized model objects
│
├── notebooks/                 # EDA and analysis notebooks
│
├── src/
│   ├── classification/        # Sentence classification pipeline
│   │   ├── embed_labeled_sentences.py
│   │   ├── compute_centroids.py
│   │   ├── classify_with_centroids.py
│   │   └── utils.py
│   │
│   ├── data/                  # Sentence extraction, filtering
│   ├── plots.py               # Visualizations of sentence or label distribution
│   └── run_pipeline.py        # Top-level script to run all stages
│
├── tests/                     # Evaluation and accuracy testing scripts
│   └── evaluate_classifier_on_held_out.py
│
├── reports/                   # Exportable output for paper figures or audit
│
├── requirements.txt           # Python environment requirements
└── README.md                  # This file
```

---

## 🔍 Sentence Classification Task

AI-related sentences are classified into three categories:

| Label        | Description |
|--------------|-------------|
| **Actionable** | Concrete initiatives using AI (e.g., “We deployed AI to detect fraud.”) |
| **Speculative** | Forward-looking or vague references (e.g., “We may explore AI in the future.”) |
| **Irrelevant** | General industry trends or boilerplate (e.g., “AI is transforming the economy.”) |

---

## 🛠️ How to Run the Pipeline

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Embedding + Centroid Pipeline

```bash
# Step 1: Generate embeddings from labeled sentences
python src/classification/embed_labeled_sentences.py

# Step 2: Compute centroids for each class
python src/classification/compute_centroids.py

# Step 3: Evaluate on held-out validation examples
python src/tests/evaluate_classifier_on_held_out.py
```

---

## 🧩 Extending the Project

You can plug in new sentence sources or update the label definitions using:

- `data/validation/hand_labeled_ai_sentences_labeled_cleaned_revised.csv`
- Or replace the classifier with a fine-tuned transformer model
- You can also run PCA/UMAP visualizations using `plots.py` to see cluster separation

---

## 📬 Contact

Developer & Maintainer: Soheil Khodadadi
Project Supervisors: Thomas Walker, Kuntara Pukthuanthong

---

## 📄 License

MIT License (if applicable)
