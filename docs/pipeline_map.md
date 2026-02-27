# Pipeline Map

This document captures the canonical Iteration 1 pipeline entry points on `main`.

## Canonical Module Entry Points

1. Extraction: `python -m semantic_ai_washing.data.extract_ai_sentences`
2. Classification: `python -m semantic_ai_washing.classification.classify_all_ai_sentences`
3. Aggregation: `python -m semantic_ai_washing.aggregation.aggregate_classification_counts`
4. Evaluation: `python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out`

## Default Data Flow

1. Input filings root: `data/processed/sec/<year>/...`
2. Extraction outputs: `*_ai_sentences.txt`
3. Classification outputs: `*_classified.csv`
4. Aggregation output: `data/final/ai_frequencies_by_firm_year.csv`
5. Held-out evaluation input: `data/validation/held_out_sentences.csv`
6. Evaluation details output (legacy default): `data/validation/evaluation_results.csv`

