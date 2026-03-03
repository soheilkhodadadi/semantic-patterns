# Data Architecture Target (Hybrid Canonical)

## Objectives
- Avoid bulk-copying the entire raw SEC corpus into project-managed folders.
- Maintain canonical structured sentence/classification tables with stable IDs.
- Preserve backward compatibility for transitional txt/csv outputs.

## Layers

### 1) Source Index Layer
- Stores references to external filing corpus paths (not full body copies).
- Canonical source root provided via `SEC_SOURCE_DIR`.
- Index output includes: `cik`, `year`, `form`, `filename`, `path`, `source_hash` (when feasible).

### 2) Curated Sampling Layer
- Stores reproducible sampling manifests for labeling/evaluation cohorts.
- Tracks sampling seed, inclusion criteria, and exclusion reasons.

### 3) Sentence Table Layer
- Canonical sentence table partitioned by year.
- Suggested partition: `sentences/year=YYYY/`.
- Minimum columns: `sentence_id`, `sample_id`, `sentence`, `sentence_norm`, `source_file`, `source_year`, `source_cik`, `sentence_index`.

### 4) Classification Layer
- Canonical prediction table partitioned by year and model version.
- Includes probabilities/similarities, classifier config, and centroid metadata hash.

### 5) Split Registry Layer
- Frozen train/validation/test sentence-id registries.
- Must include split generation seed + hash + timestamp.

## Transitional Compatibility
- Keep `*_ai_sentences.txt` and `*_classified.csv` outputs operational during migration.
- Emit warnings when mixed root-level and year-partitioned layouts could cause duplicate counting.
- Target removal of legacy-only flow by Iteration 3 (subject to gate outcomes).
