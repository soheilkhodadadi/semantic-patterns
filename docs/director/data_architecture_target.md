# Data Architecture Target

## Principles
- Raw filings are referenced via `SEC_SOURCE_DIR`; they are not bulk-copied into canonical project storage.
- Canonical tables are stored as Parquet where scale matters.
- CSV remains a review/export format, not the canonical analytical store.
- Splits, labels, model artifacts, and panels are versioned independently.

## Canonical Layers

### 1. Source Index
- `data/metadata/available_filings_index.csv`
- `data/metadata/source_windows.json`
- Purpose: reference the external filing corpus and active source windows.

### 2. Manifest Registry
- `data/manifests/filings/<manifest_id>.csv`
- `data/manifests/sentences/<manifest_id>.csv`
- `data/manifests/manifests_metadata.json`
- Purpose: reproducible bounded subsets for extraction, labeling, and evaluation.

### 3. Sentence Table
- `data/processed/sentences/year=YYYY/ai_sentences.parquet`
- Review export: `data/processed/sentences/year=YYYY/ai_sentences_sample.csv`
- Purpose: canonical extracted AI-sentence dataset with stable IDs and integrity fields.

### 4. Split Registry
- `data/metadata/splits/split_registry_v1.csv`
- `data/metadata/splits/split_registry_v1.json`
- Purpose: freeze train and validation assignments independently of sentence storage.

### 5. Label Table
- `data/labels/v1/labels_master.parquet`
- `data/labels/v1/irr_subset.parquet`
- `data/labels/v1/adjudication.parquet`
- Optional review exports: `data/labels/v1/*.csv`
- Purpose: canonical human and assistive labeling records without contaminating held-out evaluation data.

### 6. Model Artifacts
- `artifacts/models/<model_version>/embeddings.parquet`
- `artifacts/models/<model_version>/centroids.json`
- `artifacts/models/<model_version>/metadata.json`
- `reports/evaluation/<eval_version>/*`
- Purpose: reproducible model state and evaluation evidence.

### 7. Classification Table
- `data/processed/classifications/year=YYYY/model=<model_version>/classified_sentences.parquet`
- Review export: `.../classified_sentences_sample.csv`
- Purpose: sentence-level predictions for active source windows.

### 8. Panel Layer
- `data/panels/panel_v1.parquet`
- `data/panels/panel_v1.csv`
- `reports/panels/panel_v1_qa.json`
- Purpose: analysis-ready firm-year panel.

## Transitional Compatibility
- Legacy `*_ai_sentences.txt` and `*_classified.csv` outputs remain transitional only.
- Legacy `src/data/*.py` shims remain compatibility-only and should be retired after migration is complete.
