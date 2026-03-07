# Stakeholder Expectations

This document is the canonical paraphrased record of Kuntara's project expectations for the current roadmap. It is derived from the exported email thread `Re_ AI washing.eml` and is intended to replace ad hoc recall from chat or email history.

## Source

- Primary source: exported email thread `Re_ AI washing.eml`
- Coverage window: `2025-06-29` through `2025-11-18`
- Stakeholder: `Kuntara`

## Expectations

| Requirement ID | Priority | Date(s) | Expectation | Roadmap mapping |
| --- | --- | --- | --- | --- |
| `validate_methodology_before_scale` | `non-negotiable` | `2025-07-26` | Validate the A/S/I methodology before deeper investment in scaled execution. | Iteration 1 API/rubric bootstrap; Iteration 2 IRR and sufficiency gate |
| `true_human_irr_multi_rater` | `non-negotiable` | `2025-07-26`, `2025-08-27` | Use multiple human raters and true human-human IRR rather than model-vs-label agreement. | Iteration 2 IRR and sufficiency gate |
| `scale_candidate_pool_to_500_firms` | `publication-critical` | `2025-08-27`, `2025-09-08` | Scale beyond the pilot to roughly 500 firms and 1–2k clean AI sentences. | Iteration 2 sentence-pool expansion and dataset expansion |
| `label_set_sufficiency_before_retraining` | `publication-critical` | `2025-08-27`, `2025-09-08` | Reach a materially larger adjudicated label set before retraining; small pilots are not enough for a publishable finance-paper classifier. | Iteration 2 dataset expansion, IRR/adjudication, sufficiency gate |
| `ai_total_merge_integrity` | `non-negotiable` | `2025-08-27` | Fix and verify merge integrity, especially `ai_total`, before panel and regression work. | Iteration 3 merge-integrity QA; Iteration 4 panel assembly |
| `job_postings_robustness` | `publication-critical` | `2025-09-08`, `2025-10-13` | Include job postings as a robustness path. | Iteration 4 robustness input integration; Iteration 5 robustness |
| `lagged_and_industry_robustness` | `publication-critical` | `2025-10-13` | Include lagged regressions (`t+1`, `t+2`) and industry FE or SIC-bucket robustness. | Iteration 5 regression specification and robustness |
| `patent_mismatch_washing_proxy` | `publication-critical` | `2025-09-08`, `2025-10-13` | Include patent-mismatch × A/S ratio robustness for the washing interpretation. | Iteration 5 robustness |
| `literature_differentiation` | `publication-critical` | `2025-07-26` | Produce a literature differentiation table versus nearby papers. | Iteration 5 differentiation/package |
| `before_after_examples` | `publication-critical` | `2025-07-26` | Provide before/after classification examples to make the method legible and defensible. | Iteration 5 differentiation/package |
| `publication_scope_all_public_firms` | `preferred` | `2025-10-13` | Move toward all publicly traded firms and a longer-horizon sample as the publication target when source availability allows. | Iteration 4 historical/publication scope expansion; Iteration 5 results |
| `results_and_paper_package` | `non-negotiable` | `2025-11-01`, `2025-11-18` | Deliver a results/paper package, not only pipeline completion. | Iteration 5 release packaging |

## Hard Gates Derived From Expectations

### Methodology

- IRR must be true human-human IRR.
- IRR threshold is `kappa > 0.7`.
- IRR subset size is `>= 100`.
- `held_out_sentences.csv` remains frozen evaluation-only.
- API outputs remain assistive-only and never become canonical labels by default.

### Data sufficiency

- Iteration 2 sentence-pool expansion targets `500 firms`.
- Iteration 2 sentence-pool expansion targets `1–2k` clean AI sentences.
- Retraining requires `>= 500` adjudicated labels.
- Retraining requires `>= 80` adjudicated labels per class.
- Merge integrity, especially `ai_total`, must be checked before panel/regression phases.

### Publication package

- Publication package must include:
  - literature differentiation
  - before/after classification examples
  - patent mismatch × A/S ratio robustness
  - job postings robustness
  - lagged regressions
  - industry FE or SIC-bucket robustness
- Publication significance remains an output expectation, not an optimization target for earlier science phases.

## Notes

- The active development window remains `2021–2024`.
- The publication target scope is broader than the active development window and should remain visible in the roadmap even when source availability defers full execution.
- This document is authoritative for stakeholder alignment. New stakeholder evidence should patch this document first, then the roadmap model.
