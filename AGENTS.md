# AGENTS (Codex Automation Guidelines)

This document provides project-specific guidance for AI coding agents (like OpenAI Codex) working on the semantic-patterns repository. It covers how to run linting and tests, describes the repository structure and key scripts, and defines what “done” means for tasks in this project.

## Linting and Formatting

- Linting Tool: This project uses Ruff exclusively for Python linting and formatting. No other linters or formatters (like Flake8 or Black) are used.
- Configuration: The pyproject.toml contains Ruff configurations (e.g. line length, file include/exclude patterns under [tool.ruff]).
- Local Environment Baseline: Use the repo-local `.venv` interpreter for development and automation. Run `make bootstrap` once, then `make doctor` to verify interpreter, pip/module availability, and tooling.
- How to Lint: Run `make lint` to check code style (this runs `ruff format --check` and `ruff check`). All code should pass Ruff with no warnings or errors.
- How to Format: Run `make format` to apply auto-fixes (`ruff check --fix` and `ruff format`). Ensure code is clean afterward with `make lint`.

## Testing and Validation

- Canonical Namespace: Use `semantic_ai_washing.*` imports for all new code. Legacy `src/*` module paths are transitional compatibility shims only.
- Canonical Script Invocation: Prefer `python -m semantic_ai_washing.<domain>.<module>` after installing the package (`pip install -e .`) over direct `python src/...` execution.
- Pytest Baseline: The repository now includes a root `tests/` pytest suite for regression coverage (currently focused on extraction/aggregation-critical paths). Use `pytest -q` as part of the default validation flow.
- Recommended Preflight: Run `make doctor` before lint/tests to catch interpreter drift (for example conda base active while `.venv` is intended).
- Classifier Evaluation: Use `python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out` to evaluate the AI classifier on a held-out dataset. This script will output the model’s accuracy and other metrics, and it typically saves results (like a confusion matrix). It should complete without errors.
- Manual Spot-Check: Use `python -m semantic_ai_washing.tests.spot_check_classifications` to perform a manual spot check of classifications. This script prints a random sample of sentences with their predicted labels for review, helping to qualitatively assess the model’s outputs.
- Interpretation: Consider the evaluation successful if the accuracy meets the project’s quality threshold (see Definition of Done below) and the confusion matrix or sample outputs look reasonable (e.g. the model isn’t consistently mislabeling one category).

## Repository Structure & Key Scripts

The project is organized under the src/ directory with sub-packages for different components (e.g. classification, scripts, tests, aggregation, patents). There is no single CLI entry point; instead, a series of scripts handle data processing, model training, and evaluation. Below are the main scripts and their purposes (with typical usage):

- Sentence Extraction: `src/semantic_ai_washing/data/extract_ai_sentences.py` – Extracts AI-related sentences from raw text filings. Run this script to generate files (e.g., *_ai_sentences.txt) containing sentences about AI for each source document.
- Sentence Classification: `src/semantic_ai_washing/classification/classify_all_ai_sentences.py` – Classifies all extracted sentences using the AI-washing classifier. Running this script produces CSV files (e.g., *_classified.csv) with each sentence and its predicted label/probability.
- Embed Labeled Sentences: `src/semantic_ai_washing/classification/embed_labeled_sentences_mpnet.py` – (For model updates) Generates vector embeddings for labeled sentences using a MPNet model. This is typically run when updating the classifier, to compute embeddings for the training data.
- Compute Centroids: `src/semantic_ai_washing/classification/compute_centroids_mpnet.py` – Computes class centroids from the embedded sentences. The classifier uses these centroids as references for labeling new sentences.
- Evaluate Classifier: `src/semantic_ai_washing/tests/evaluate_classifier_on_held_out.py` – Evaluates the classifier’s performance on a held-out test set. (As noted above, run this to get accuracy metrics and ensure the model meets quality targets.)
- Spot-Check Classifications: `src/semantic_ai_washing/tests/spot_check_classifications.py` – Prints random classified sentences and their labels for manual verification of classification quality.
- Aggregate Results: `src/semantic_ai_washing/aggregation/aggregate_classification_counts.py` – Aggregates per-sentence classification results into higher-level counts (for example, counting how many sentences of each class per document or per firm-year). It supports both legacy `*_classified.txt` and current `*_classified.csv` files.
- Patent Data Integration: (If applicable) Scripts in `src/semantic_ai_washing/patents/` (e.g., merge_ai_with_patents.py) handle merging the AI classification results with external patent data to enrich the analysis.

Usage: Most of these scripts are standalone and assume default file paths or configurations (often specified in the code or README). To run a script, use module execution (for example: `python -m semantic_ai_washing.classification.classify_all_ai_sentences`). Make sure any prerequisites (such as input data files or prior steps like embedding generation) are satisfied before running each script.

## Definition of Done (Completion Criteria)

For any code contribution or task in this repository, the following criteria define when the task is “done” and ready for review/merge:

- Lint & Format Clean: All Python code must pass Ruff linting with no errors, and be properly formatted according to Ruff’s rules. (Use `make format` then `make lint` to verify.)
- Environment Health: Run `make bootstrap` then `make doctor` to ensure `.venv`, `python -m pip`, and `semantic_ai_washing` imports are healthy before QA checks.
- Accuracy ≥ 80%: The classifier must achieve at least 80% accuracy on the held-out evaluation set (this is the minimum quality gate per project guidelines). Run `python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out` and confirm the accuracy meets or exceeds 0.80. Additionally, check that the confusion matrix from this evaluation looks reasonable (no unexpected pattern of misclassifications).
- Data Processed: If the task involved adding or updating data (e.g., new documents or a new year of filings):
  - Ensure `python -m semantic_ai_washing.data.extract_ai_sentences` has been run to extract AI-related sentences from new/updated data.
  - Run `python -m semantic_ai_washing.classification.classify_all_ai_sentences` so all new sentences are classified with the current model.
  - If applicable, run `python -m semantic_ai_washing.aggregation.aggregate_classification_counts` to update aggregated metrics (for example firm-year classification counts).
  - Verify that any new data (for example, all 2024 filings) are fully processed and included in the outputs.
- Documentation & Logging: Document the outcome of the changes:
  - Update or create relevant documentation (README, etc.) if any processes or results have changed.
  - In the commit message or PR description, note key metrics and results (e.g., “Held-out accuracy = 82%, F1 improved by 5%, adjusted threshold to 0.7”).
  - If the task was performed via an interactive Codex session, ensure that all code diffs were shown for review and that logs/output from test scripts (like accuracy results) are captured for the record.
- Scope and Review: Confirm that code changes are confined to the intended scope of the task:
  - Typically, modifications should be made within the src/ directory (in the relevant module/package) unless explicitly directed otherwise.
  - Do not modify files outside of src/ or unrelated components without explicit instruction.
  - After implementing changes, review the diff to ensure only the expected files and lines were changed. (Automated agents should always present diffs for verification before finalizing any commit.)

By fulfilling the above criteria, the project maintains both code quality and functional integrity. Codex (and other AI agents) should use these guidelines to autonomously run checks (linting, evaluation) and to decide when a code-editing task is complete.
