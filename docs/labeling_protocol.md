# Labeling Protocol (Iteration 1 Phase 1)

This protocol defines how to label AI-related filing sentences for the Iteration 1 training dataset.

## Scope and Unit of Labeling

- Labeling unit: sentence-level with context metadata.
- Required contextual fields: `source_file`, `source_year`, `source_form`, `source_cik`, `sentence_index`.
- Stable IDs:
  - `sentence_norm`: lowercase + strip punctuation + collapse whitespace.
  - `sentence_id`: `sha1(sentence_norm)[:16]`.
  - `sample_id`: `sha1(source_file|sentence_index|sentence_norm)[:16]`.

## Allowed Labels

- `Actionable`: sentence describes concrete implementation, deployment, operation, measurable execution, or in-production use of AI.
- `Speculative`: sentence describes plans, intentions, forward-looking expectations, potential benefits/risks, or exploratory statements without concrete deployment.
- `Irrelevant`: sentence mentions AI/technology only in generic, list-like, boilerplate, or non-substantive ways not tied to meaningful firm action.

Rows with labels outside this set fail QA.

## Decision Rules

- Prefer `Actionable` when there is explicit evidence of current/realized implementation.
- Prefer `Speculative` when language is future-oriented (`may`, `might`, `plan`, `intend`, `expect`) or uncertainty/risk-oriented without concrete deployment.
- Prefer `Irrelevant` for laundry-list mentions where AI appears as one of many trends/topics without actionability.

## Borderline A vs S Disambiguation

- If both action and future intent appear, prioritize:
  - `Actionable` when execution is explicit (for example, “deployed”, “currently use”, “in production”, quantifiable outcomes).
  - `Speculative` when execution evidence is absent and intent dominates.
- If still ambiguous, mark uncertain (`is_uncertain=1`) and provide a short `uncertainty_note`.

## Uncertainty Policy

- Use `is_uncertain=1` when label confidence is insufficient.
- Always provide `uncertainty_note` for uncertain rows.
- Uncertain rows are excluded from final training in Phase 1 and written to `uncertain_rows.csv` pending adjudication.

## Data Hygiene Rules

- No empty sentences.
- No missing labels for non-uncertain rows.
- Minimum token count: `>= 6`.
- No overlap (by `sentence_norm`) with frozen held-out set:
  - `data/validation/held_out_sentences.csv`
- Deduplication policy:
  - exact dedupe by `sentence_norm`
  - near-dedupe by `difflib.SequenceMatcher` at threshold `0.95`
  - near-duplicate conflicting labels routed to `label_conflicts.csv`

## QA and Reproducibility

- QA command:
  - `python -m semantic_ai_washing.labeling.qa_labeled_dataset --input data/labels/iteration1/expanded_labeled_sentences_preqa.csv --held-out data/validation/held_out_sentences.csv --min-tokens 6 --min-class-count 60 --target-size 400 --output data/labels/iteration1/expanded_labeled_sentences.csv --report reports/iteration1/phase1/qa_report.json --leakage-report reports/iteration1/phase1/leakage_overlap_report.csv`
- Dataset metadata:
  - `data/labels/iteration1/dataset_metadata.json`
  - includes commit hash, source fingerprints, sampling/dedupe settings, leakage policy, and rubric reference.
