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

## IRR Workflow (Phase 2)

- Rater 2 sheet is text-only by default (`irr_item_id`, `sentence`, `rater2_label`, `rater2_note`) to reduce contextual anchoring.
- Rater instructions:
  - label each sentence as one of `Actionable|Speculative|Irrelevant`
  - avoid using downstream outcomes (patents/returns/performance) during labeling
  - use `rater2_note` only for uncertainty rationale, not external evidence
- Disagreement taxonomy:
  - transitions tracked as `A->S`, `A->I`, `S->A`, `S->I`, `I->A`, `I->S`
  - pairwise classes tracked as `A_vs_S`, `A_vs_I`, `S_vs_I`
- Adjudication rules:
  - when both raters agree, keep agreed label
  - when raters disagree, set `final_label` in adjudication sheet with brief `adjudication_note`
  - unresolved/blank `final_label` rows are considered pending adjudication
- IRR gate policy:
  - infrastructure-mode Phase 2 can complete with `pending_rater2` or `pending_adjudication`
  - strict κ gate (`kappa >= 0.6`) must pass before centroid retraining

## Assistive API Bootstrap (Iteration 1)

- OpenAI API output is assistive-only and is never canonical by default.
- API output is not IRR and must not replace the second-rater workflow.
- `data/validation/held_out_sentences.csv` remains frozen evaluation-only and must not be reused for assistive prompt training or canonical label generation.
- Human raters remain the source of truth for labels, adjudication, and rubric refinement.
- The assistive prompt must return exactly one of `Actionable|Speculative|Irrelevant`.
- Returned rationale is short and review-oriented.
- Returned confidence is informational only and must not override the rubric.
- The smoke test uses one deterministic clean sentence from `data/processed/sentences/year=2024/ai_sentences_sample.csv`.
- The API key must be injected through `OPENAI_API_KEY`. Do not store it in tracked files or paste it back into chat.
- No downstream outcomes, patents, returns, or later panel variables may appear in the prompt or adjudication reasoning.

### Assistive Prompt Rubric Summary

- `Actionable`: explicit current deployment, operational use, implementation details, or realized AI execution.
- `Speculative`: future-looking plans, intentions, risks, expected benefits, or exploratory AI statements without concrete execution evidence.
- `Irrelevant`: generic, boilerplate, list-like, or non-substantive AI mentions that do not indicate meaningful firm action.

### Disallowed API Uses

- Generating canonical labels for the training set.
- Replacing the blinded human second-rater workflow.
- Reusing held-out sentences as training or assistive prompt examples.

## Label Ops Bootstrap (Iteration 1)

- `labeling_batch_v1` is leakage-safe against the frozen held-out dataset.
- Exact duplicate sentence texts are removed before the batch is created.
- The first bootstrap batch is human-labeling-ready and leaves review fields blank:
  - `label`
  - `is_uncertain`
  - `uncertainty_note`
- API suggestions are intentionally excluded from `labeling_batch_v1`.
- The bootstrap batch contract is:
  - `240` rows total
  - availability-aware quarter redistribution after clean-filter, held-out exclusion, and exact-text dedupe
  - exact quarter counts are recorded in `reports/labels/labeling_batch_v1_summary.json`
- Batch creation consumes only the canonical 2024 sentence table and the bounded pilot manifest:
  - `data/processed/sentences/year=2024/ai_sentences.parquet`
  - `data/manifests/filings/pilot_2024_10k_v1.csv`
