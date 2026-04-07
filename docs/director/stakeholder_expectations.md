# Stakeholder Expectations

This document is the canonical paraphrased record of Kuntara's project
expectations for the AI-washing planning lane. It is intended to replace ad hoc
recall from chat or email history.

## Source

- Primary source: exported email thread `Re_ AI washing.eml`
- Additional source: stakeholder email provided on `2026-04-06`
- Coverage window: `2025-06-29` through `2026-04-06`
- Stakeholder: `Kuntara`

## Expectations

### Preliminary and restructure era expectations

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

### Publication-upgrade addendum

These expectations belong to the next project-scoped AI-washing phase rather
than the earlier preliminary-results roadmap.

Primary planning mapping:
- `projects/ai_washing/docs/publication_upgrade_stakeholder_expectations_v1.md`
- `projects/ai_washing/docs/publication_upgrade_roadmap_v1.md`

| Requirement ID | Priority | Date(s) | Expectation | Planning mapping |
| --- | --- | --- | --- | --- |
| `surprising_lead_result_required` | `publication-critical` | `2026-04-06` | Reframe the paper around a result with stronger surprise and front-load that result in the paper package. | Publication-upgrade Workstream E |
| `capital_market_consequence_required` | `non-negotiable` | `2026-04-06` | Add at least one capital-market consequence test so the paper quantifies why AI-washing matters economically. | Publication-upgrade Workstream C |
| `market_reaction_event_study_candidate` | `publication-critical` | `2026-04-06` | Treat filing-date market reaction or a closely related event-study design as a primary candidate for the capital-market consequence lane. | Publication-upgrade Workstream C |
| `identification_design_required` | `non-negotiable` | `2026-04-06` | Add a more credible identification strategy rather than leaving the paper entirely predictive. | Publication-upgrade Workstream D |
| `chatgpt_shock_candidate` | `publication-critical` | `2026-04-06` | Treat the late-2022 ChatGPT release as the leading candidate shock unless a cleaner design is found. | Publication-upgrade Workstream D |
| `refresh_2025_filings` | `non-negotiable` | `2026-04-06` | Refresh the filing backbone to include 2025 10-Ks and rerun the relevant extraction/classification pipeline. | Publication-upgrade Workstream A |
| `classifier_robustness_upgrade` | `publication-critical` | `2026-04-06` | Improve model credibility through stronger accuracy and robustness evidence, including high-confidence or human-labeled subset checks. | Publication-upgrade Workstream B |
| `specification_defensibility` | `publication-critical` | `2026-04-06` | Explain or replace vulnerable empirical presentation choices such as negative adjusted `R^2` where needed. | Publication-upgrade Workstream E |
| `paper_voice_and_package_hardening` | `preferred` | `2026-04-06` | Harden the final paper package so the prose, literature positioning, and contribution framing do not undermine the economics. | Publication-upgrade Workstream E |

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

### Publication-upgrade addendum

- Add at least one serious capital-market consequence test before treating the
  next paper package as publication-ready.
- Choose and document at least one identification design candidate rather than
  leaving the next phase purely predictive.
- Make the 2025 filing refresh explicit in the next execution lane.
- Pair any model-improvement work with robustness that reduces dependence on the
  full classified sample.
- Do not let a writing/package weakness hide the strongest empirical result.

## Notes

- The active development window remains `2021–2024`.
- The publication target scope is broader than the active development window and should remain visible in the roadmap even when source availability defers full execution.
- The earlier machine-readable roadmap remains the archive of the preliminary
  and restructure era.
- The current publication-upgrade lane is project-scoped under
  `projects/ai_washing/docs/`.
- This document is authoritative for shared stakeholder alignment. New
  stakeholder evidence should patch this document first, then the active
  project-scoped roadmap.
