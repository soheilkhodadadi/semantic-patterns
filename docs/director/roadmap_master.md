<!-- generated_file: true -->
<!-- source_model: /Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/model/roadmap_model.yaml -->
<!-- source_sha256: 363798831db1c0bf8fd330aca7c6ad94f3ef9f583609afa41b0fae91122db08b -->
<!-- rendered_at: 2026-03-15T19:19:57.877262+00:00 -->

# Roadmap Master

This document is generated from the canonical roadmap YAML model.

Optimization proposals may recommend resequencing tasks or phases beyond the canonical order shown here.

## Branching Policy
- integration branch template: `iteration{iteration_id}/integration`
- work branch template: `iteration{iteration_id}/{slug}`
- merge target: `main`
- preferred merge strategy: `ff_only_if_possible_else_pr_merge_commit`
- review approval required before next iteration: `true`
- review approval required before main merge: `true`
- starter prompt required: `true`

## Review Workflow
- Every iteration ends with `review-and-replan`.
- Iterations 2-5 start with `kickoff-and-preflight`.
- Approved reviews authorize the next iteration and main-merge closeout.

## Stakeholder Alignment
- source artifact: `docs/director/stakeholder_expectations.md`
- active development scope: `2021-2024 public-filing development window`
- publication target scope: `all publicly traded firms`
- desired horizon: `20-year horizon when source availability permits`

### Methodology Hard Gates
- Validate the A/S/I methodology before committing to scaled downstream analysis.
- IRR must be true human-human IRR on a blinded 100+ sentence subset.
- IRR threshold must exceed 0.7 before centroid retraining.
- held_out_sentences.csv remains frozen evaluation-only.
- API outputs remain assistive-only and must not become canonical labels.

### Data Hard Gates
- Iteration 2 sentence-pool expansion must target 500 firms.
- Iteration 2 sentence-pool expansion must target 1-2k clean AI sentences.
- Centroid retraining requires at least 500 adjudicated labels.
- Centroid retraining requires at least 80 adjudicated labels per class.
- ai_total merge integrity must be checked before panel and regression work.

### Publication Hard Gates
- Publication package must include a literature differentiation table.
- Publication package must include before/after classification examples.
- Publication package must include robustness using patent mismatch x A/S ratio, job postings, lagged regressions, and industry FE/SIC buckets.
- Release packaging must produce a paper/results package, not only pipeline artifacts.

### Stakeholder Requirements
- `validate_methodology_before_scale` priority=`non-negotiable` stakeholder=`Kuntara`
  - summary: Validate the new A/S/I classification approach before deeper investment in scaled execution.
  - target iteration: `2`
  - source refs: email thread 2025-07-26
  - mapped phases: iteration2/rubric-realignment, iteration2/irr-and-adjudication, iteration2/label-sufficiency-gate
  - mapped gates: rubric_realignment_complete, human_human_irr_gt_0_7, label_sufficiency_before_retraining
- `true_human_irr_multi_rater` priority=`non-negotiable` stakeholder=`Kuntara`
  - summary: Use multiple human raters and true IRR rather than model-vs-label agreement.
  - target iteration: `2`
  - source refs: email thread 2025-07-26, email thread 2025-08-27
  - mapped phases: iteration2/irr-and-adjudication, iteration2/label-sufficiency-gate
  - mapped gates: human_human_irr_only, human_human_irr_gt_0_7
- `scale_candidate_pool_to_500_firms` priority=`publication-critical` stakeholder=`Kuntara`
  - summary: Expand beyond the bootstrap pilot to a 500-firm candidate pool with roughly 1-2k clean AI sentences.
  - target iteration: `2`
  - source refs: email thread 2025-08-27, email thread 2025-09-08
  - mapped phases: iteration2/sentence-pool-expansion-2024, iteration2/tranche2-labeling, iteration2/tranche3-labeling
  - mapped gates: candidate_pool_500_firms, candidate_pool_clean_sentences_gte_1000
- `label_set_sufficiency_before_retraining` priority=`publication-critical` stakeholder=`Kuntara`
  - summary: Reach a publication-grade adjudicated label set before retraining, not just a small pilot.
  - target iteration: `2`
  - source refs: email thread 2025-08-27, email thread 2025-09-08
  - mapped phases: iteration2/tranche1-labeling, iteration2/tranche2-labeling, iteration2/tranche3-labeling, iteration2/merge-canonical-labels, iteration2/irr-and-adjudication, iteration2/provisional-rubric-freeze-and-split-registry, iteration2/label-sufficiency-gate
  - mapped gates: adjudicated_labels_gte_500, per_class_labels_gte_80
- `ai_total_merge_integrity` priority=`non-negotiable` stakeholder=`Kuntara`
  - summary: Fix and verify merge integrity, especially ai_total, before panel and regression work.
  - target iteration: `3`
  - source refs: email thread 2025-08-27
  - mapped phases: iteration3/classification-merge-integrity, iteration4/panel-assembly-2021-2024
  - mapped gates: ai_total_merge_integrity
- `job_postings_robustness` priority=`publication-critical` stakeholder=`Kuntara`
  - summary: Include job postings as a robustness path in the publication pipeline.
  - target iteration: `4`
  - source refs: email thread 2025-09-08, email thread 2025-10-13
  - mapped phases: iteration4/job-postings-robustness-integration, iteration5/robustness-and-sensitivity
  - mapped gates: job_postings_robustness_available
- `lagged_and_industry_robustness` priority=`publication-critical` stakeholder=`Kuntara`
  - summary: Run lagged regressions and industry FE or SIC-bucket robustness before publication packaging.
  - target iteration: `5`
  - source refs: email thread 2025-10-13
  - mapped phases: iteration5/regression-specification, iteration5/robustness-and-sensitivity
  - mapped gates: lagged_regressions_included, industry_fe_or_sic_robustness_included
- `patent_mismatch_washing_proxy` priority=`publication-critical` stakeholder=`Kuntara`
  - summary: Include the patent-mismatch times A/S ratio washing proxy in the robustness package.
  - target iteration: `5`
  - source refs: email thread 2025-09-08, email thread 2025-10-13
  - mapped phases: iteration5/robustness-and-sensitivity
  - mapped gates: patent_mismatch_as_ratio_robustness
- `literature_differentiation` priority=`publication-critical` stakeholder=`Kuntara`
  - summary: Document differentiation from nearby papers with a literature comparison table.
  - target iteration: `5`
  - source refs: email thread 2025-07-26
  - mapped phases: iteration5/literature-differentiation-and-examples, iteration5/release-packaging
  - mapped gates: literature_differentiation_table_present
- `before_after_examples` priority=`publication-critical` stakeholder=`Kuntara`
  - summary: Provide before/after classification examples to make the method legible and defensible.
  - target iteration: `5`
  - source refs: email thread 2025-07-26
  - mapped phases: iteration5/literature-differentiation-and-examples, iteration5/release-packaging
  - mapped gates: before_after_examples_present
- `publication_scope_all_public_firms` priority=`preferred` stakeholder=`Kuntara`
  - summary: Move toward all-public-firm and longer-horizon coverage as the publication target once source availability permits.
  - target iteration: `4`
  - source refs: email thread 2025-10-13
  - mapped phases: iteration4/historical-window-expansion-readiness, iteration5/results-generation
  - mapped gates: publication_scope_plan_recorded
- `results_and_paper_package` priority=`non-negotiable` stakeholder=`Kuntara`
  - summary: Deliver a paper/results package, not only pipeline completion.
  - target iteration: `5`
  - source refs: email thread 2025-11-01, email thread 2025-11-18
  - mapped phases: iteration5/release-packaging
  - mapped gates: results_package_present
- `preliminary_results_internal_fast_track` priority=`operational` stakeholder=`Kuntara`
  - summary: After truthful IRR closeout, allow stakeholder-facing preliminary results on the active 2021-2024 window without weakening publication-grade gates.
  - target iteration: `2`
  - source refs: email thread 2026-03-15
  - mapped phases: iteration2/irr-disagreement-diagnostic, iteration2/preliminary-results-authorization, iteration3/preliminary-kickoff-and-preflight, iteration4/preliminary-panel-assembly-2021-2024, iteration5/preliminary-results-package, iteration5/preliminary-results-table-planning
  - mapped gates: preliminary_results_internal_only

## Methodology Alignment
- source artifact: `docs/director/proposal_methodology.md`
- core construct: AI-washing is speculative firm AI narrative without later observable AI capability.
- active development scope: `2021-2024 public-filing development window`
- publication target scope: `all publicly traded firms`
- desired horizon: `2000-2024 when source availability permits`

### Core Constructs
- Actionable statements indicate current or realized firm AI capability.
- Speculative statements indicate firm-specific AI aspiration without operational proof.
- Irrelevant statements mention AI generically without serving as a firm capability claim.

### Label Semantics
- `Actionable`: present or past firm-specific deployment, implementation, embedded workflow, or operational execution of AI
- `Speculative`: firm-specific aspirational or forward-looking AI narrative without operational evidence
- `Irrelevant`: generic market, regulatory, cyber-risk, boilerplate, or tangential AI mention

### Borderline Rules
- Generic AI risk, regulatory, or cyber language is Irrelevant unless it discloses current firm AI deployment.
- Risk-section language becomes Actionable only when it reveals current firm AI use or implementation.
- A sentence is not Speculative merely because it is uncertain or risk-oriented; it must still be a firm-specific AI narrative claim.

### IRR Design
- Stratified sample covering at least 100 firms.
- Balanced by industry and year.
- Two independent human raters and a third adjudicator.
- Report Cohen's kappa overall and by class.

### Named Measures
- `AI_Focus`: `log(1 + AI sentences)` - Firm-year AI disclosure intensity.
- `log_1_plus_A`: `log(1 + A)` - Firm-year intensity of Actionable AI statements.
- `log_1_plus_S`: `log(1 + S)` - Firm-year intensity of Speculative AI statements.
- `SpecShare`: `S / (A + S)` - Speculative share among non-irrelevant AI statements.
- `CredAI`: `z(A) - z(S)` - Credibility index contrasting Actionable and Speculative intensity.
- `A_S`: `log(1 + A / (1 + S))` - Stabilized actionable-to-speculative ratio.

### Baseline Predictive Specs
- Use patents and AI-skills job postings as capability outcomes.
- Evaluate horizons l in {0,1,2}.
- Use firm and year fixed effects in the baseline specification.
- Use industry x year fixed effects as robustness.

### AI-Washing Specification
- Use A_S as the main narrative-credibility measure.
- Use A_S x PatentMismatch in the AI-washing specification.

### Rubric Calibration Policy
- Rubric refinement is allowed during development calibration when tranche evidence shows the construct is being captured poorly.
- Calibration changes must be tied to proposal-faithful label semantics and predeclared predictive outcomes.

### Rubric Freeze Policy
- Rubric must freeze before publication-scale deployment.
- If later evidence requires label-definition changes, director must route back to rubric realignment through review.

### Predictive Validity Policy
- Predictive-validity is a directional development gate, not an unconstrained significance target.
- Failure of the development predictive-validity gate triggers review-driven return to rubric realignment rather than arbitrary metric fishing.

### Methodology Hard Gates
- human_human_irr_only
- irr_stratified_100_firms_min
- by_class_kappa_report_required
- rubric_freeze_before_final_scale
- directional_predictive_validity_before_publication_scale

## Policies
- `heldout_frozen` `dataset_freeze` enforcement=`hard` value=`True`
- `human_human_irr_only` `methodology` enforcement=`hard` value=`True`
- `no_downstream_outcome_peeking` `methodology` enforcement=`hard` value=`True`
- `openai_assistive_only` `model_governance` enforcement=`hard` value=`assistive_only`
- `no_significance_optimization` `analysis_governance` enforcement=`hard` value=`True`
- `preliminary_results_internal_only` `analysis_governance` enforcement=`hard` value=`{'preliminary_only': True, 'source_window_id': 'active_2021_2024', 'publication_grade_authorized': False}`
- `split_registry_required_before_retraining` `data_governance` enforcement=`hard` value=`True`
- `sentence_quality_gate_before_labeling` `data_governance` enforcement=`hard` value=`True`
- `sentence_quality_gate_before_irr` `data_governance` enforcement=`hard` value=`True`
- `human_human_irr_gt_0_7` `methodology` enforcement=`hard` value=`{'kappa_min': 0.7, 'irr_subset_min': 100}`
- `label_sufficiency_before_retraining` `data_governance` enforcement=`hard` value=`{'adjudicated_labels_min': 500, 'per_class_min': 80}`
- `merge_integrity_before_panel` `data_governance` enforcement=`hard` value=`ai_total_required`
- `publication_package_required` `analysis_governance` enforcement=`hard` value=`True`

## Data Layers
- `source_index` path=`data/metadata/available_filings_index.csv` format=`csv`
- `manifest_registry` path=`data/manifests/manifests_metadata.json` format=`json`
- `sentence_table` path=`data/processed/sentences/year=YYYY/ai_sentences.parquet` format=`parquet` review=`data/processed/sentences/year=YYYY/ai_sentences_sample.csv`
- `split_registry` path=`data/metadata/splits/split_registry_v1.csv` format=`csv`
- `label_table` path=`data/labels/v1/labels_master.parquet` format=`parquet`
- `model_artifacts` path=`artifacts/models/<model_version>/` format=`mixed`
- `classification_table` path=`data/processed/classifications/year=YYYY/model=<model_version>/classified_sentences.parquet` format=`parquet` review=`data/processed/classifications/year=YYYY/model=<model_version>/classified_sentences_sample.csv`
- `panel` path=`data/panels/panel_v1.parquet` format=`parquet` review=`data/panels/panel_v1.csv`

## Source Windows
- `active_2021_2024` status=`active` years=2021, 2022, 2023, 2024 root=`env:SEC_SOURCE_DIR`
- `historical_2000_2020` status=`deferred` years=2000-2020 root=`env:SEC_SOURCE_DIR`

## Tooling Policies
- `atlas_isolated_env` tool=`atlas` mode=`isolated_skill_env` wrapper=`scripts/atlas_isolated.sh`

## Iteration 1 - Foundation, Canonical Contracts, and Bounded 2024 Pilot
Goal: Establish canonical contracts, clean the execution surface, and build a bounded sentence-table pilot from 2024 10-K filings.
Entry criteria: Canonical roadmap model v2 is active and rendered., Active source window 2021-2024 is available through SEC_SOURCE_DIR or local source-root config.
Exit criteria: Foundation phases passed through label-ops-bootstrap., Iteration 1 review approved and closeout branch plan generated.

### iteration1/kickoff-and-preflight
- Title: Historical Kickoff and Preflight
- Goal: Traceability-only placeholder for the retroactively introduced iteration kickoff boundary.
- Lifecycle: `historical`
- Depends on: none
- Source window: `none`
- Required artifacts: director/reviews/iteration_1_kickoff.json
- Tags: historical, kickoff

#### Tasks
- phase-level only in this roadmap version

### iteration1/baseline-asset-freeze
- Title: Baseline Asset Freeze
- Goal: Freeze current evaluation assets and classify duplicates or deprecations before new data work starts.
- Lifecycle: `planned`
- Depends on: none
- Source window: `active_2021_2024`
- Required artifacts: reports/validation/validation_asset_registry.json
- Tags: data_contracts, validation_assets

#### Tasks
- `iteration1.assets.inventory_validation_assets` Inventory validation assets
  - kind: `diagnostic` gate_class: `data` automation: `partial`
  - depends_on: none
  - inputs: data/validation/held_out_sentences.csv, data/validation/CollectedAiSentencesClassifiedCleaned.csv, data/validation/hand_labeled_ai_sentences_with_embeddings_revised.csv
  - outputs: reports/validation/validation_asset_registry.json
  - tags: asset_inventory, evaluation_fixture
  - risks: R3, R6

### iteration1/repo-hygiene-and-script-canon
- Title: Repo Hygiene and Script Canon
- Goal: Define canonical, transitional, and legacy scripts so the pipeline is understandable and maintainable.
- Lifecycle: `planned`
- Depends on: iteration1/baseline-asset-freeze
- Source window: `none`
- Required artifacts: docs/director/script_registry.md, director/snapshots/script_inventory.json
- Tags: repo_hygiene, script_registry

#### Tasks
- `iteration1.repo.inventory_scripts` Inventory scripts
  - kind: `diagnostic` gate_class: `ops` automation: `partial`
  - depends_on: none
  - inputs: none
  - outputs: director/snapshots/script_inventory.json
  - tags: inventory
  - risks: R7
- `iteration1.repo.publish_script_registry` Publish script registry
  - kind: `reporting` gate_class: `ops` automation: `partial`
  - depends_on: iteration1.repo.inventory_scripts
  - inputs: director/snapshots/script_inventory.json
  - outputs: docs/director/script_registry.md
  - tags: documentation
  - risks: R7

### iteration1/tooling-isolation
- Title: Tooling Isolation
- Goal: Prevent Atlas and similar external tooling from mutating the repo runtime environment.
- Lifecycle: `planned`
- Depends on: iteration1/repo-hygiene-and-script-canon
- Source window: `none`
- Required artifacts: docs/director/tooling_isolation.md, director/config/tooling_policy.yaml
- Tags: tooling, env_safety

#### Tasks
- `iteration1.tooling.publish_isolation_policy` Publish tooling isolation policy
  - kind: `reporting` gate_class: `ops` automation: `partial`
  - depends_on: none
  - inputs: none
  - outputs: docs/director/tooling_isolation.md, director/config/tooling_policy.yaml
  - tags: atlas, env_safety
  - risks: R4, R7

### iteration1/source-index-contract
- Title: Source Index Contract
- Goal: Make the external SEC root the canonical raw-source interface and record active source windows.
- Lifecycle: `planned`
- Depends on: iteration1/tooling-isolation
- Source window: `active_2021_2024`
- Required artifacts: data/metadata/available_filings_index.csv, data/metadata/source_windows.json, reports/data/source_index_summary.json
- Tags: source_index, external_sec

#### Tasks
- `iteration1.source.index_external_sec_root` Index external SEC root
  - kind: `build` gate_class: `data` automation: `partial`
  - depends_on: none
  - inputs: none
  - outputs: data/metadata/available_filings_index.csv, data/metadata/source_windows.json, reports/data/source_index_summary.json
  - tags: source_index, source_window
  - risks: R5

### iteration1/sentence-table-pilot-2024
- Title: Sentence Table Pilot 2024
- Goal: Build a bounded 2024 10-K pilot manifest and canonical sentence table.
- Lifecycle: `planned`
- Depends on: iteration1/source-index-contract
- Source window: `active_2021_2024`
- Required artifacts: data/manifests/filings/pilot_2024_10k_v1.csv, data/processed/sentences/year=2024/ai_sentences.parquet, reports/data/pilot_2024_sentence_quality.json, data/processed/sentences/year=2024/ai_sentences_sample.csv
- Tags: pilot, sentence_table

#### Tasks
- `iteration1.pilot.generate_2024_manifest` Generate bounded 2024 manifest
  - kind: `build` gate_class: `data` automation: `partial`
  - depends_on: none
  - inputs: data/metadata/available_filings_index.csv
  - outputs: data/manifests/filings/pilot_2024_10k_v1.csv, reports/data/pilot_2024_manifest_summary.json
  - tags: pilot_manifest
  - risks: R5
- `iteration1.pilot.extract_sentence_table` Extract canonical sentence table
  - kind: `build` gate_class: `data` automation: `partial`
  - depends_on: iteration1.pilot.generate_2024_manifest
  - inputs: data/manifests/filings/pilot_2024_10k_v1.csv
  - outputs: data/processed/sentences/year=2024/ai_sentences.parquet, data/processed/sentences/year=2024/ai_sentences_sample.csv, reports/data/pilot_2024_sentence_quality.json
  - tags: sentence_table, fragment_audit
  - risks: R5, R6

### iteration1/rubric-and-api-bootstrap
- Title: Rubric and API Bootstrap
- Goal: Prepare rubric v1 and bounded assistive API usage without promoting API output to canonical labels.
- Lifecycle: `planned`
- Depends on: iteration1/sentence-table-pilot-2024
- Source window: `active_2021_2024`
- Required artifacts: docs/labeling_protocol.md, director/config/api_assistive_policy.yaml, reports/api/api_bootstrap_smoke_test.json
- Tags: rubric, api_assistive

#### Tasks
- `iteration1.rubric.publish_rubric_v1` Publish rubric v1
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: none
  - inputs: reports/data/pilot_2024_sentence_quality.json
  - outputs: docs/labeling_protocol.md
  - tags: rubric_v1, api_assistive
  - risks: R1
- `iteration1.api.publish_assistive_policy` Publish assistive API policy
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: none
  - inputs: none
  - outputs: director/config/api_assistive_policy.yaml
  - tags: api_assistive_policy
  - risks: R4, R7
- `iteration1.api.run_smoke_test` Run assistive API smoke test
  - kind: `validation` gate_class: `ops` automation: `partial`
  - depends_on: iteration1.rubric.publish_rubric_v1, iteration1.api.publish_assistive_policy
  - inputs: docs/labeling_protocol.md, director/config/api_assistive_policy.yaml, data/processed/sentences/year=2024/ai_sentences_sample.csv
  - outputs: reports/api/api_bootstrap_smoke_test.json
  - tags: api_assistive, smoke_test
  - risks: R4, R7

### iteration1/label-ops-bootstrap
- Title: Label Ops Bootstrap
- Goal: Generate the first clean labeling batch from the bounded pilot after sentence-quality gating.
- Lifecycle: `planned`
- Depends on: iteration1/rubric-and-api-bootstrap
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/labeling_batch_v1.parquet, data/labels/v1/labeling_batch_v1.csv, reports/labels/labeling_batch_v1_summary.json
- Tags: label_ops, sentence_quality_gate

#### Tasks
- `iteration1.shared.audit_sentence_integrity` Audit sentence integrity
  - kind: `diagnostic` gate_class: `data` automation: `partial`
  - depends_on: none
  - inputs: data/processed/sentences/year=2024/ai_sentences_sample.csv
  - outputs: reports/data/pilot_2024_sentence_quality.json
  - tags: sentence_quality_gate
  - risks: R1, R5
- `iteration1.labels.prepare_labeling_batch` Prepare first labeling batch
  - kind: `build` gate_class: `data` automation: `partial`
  - depends_on: iteration1.shared.audit_sentence_integrity
  - inputs: data/processed/sentences/year=2024/ai_sentences.parquet
  - outputs: data/labels/v1/labeling_batch_v1.parquet, data/labels/v1/labeling_batch_v1.csv
  - tags: label_batch
  - risks: R1, R2, R5

### iteration1/review-and-replan
- Title: Review and Replan
- Goal: Synthesize iteration evidence, approve closeout, and prepare the next iteration handoff.
- Lifecycle: `planned`
- Depends on: iteration1/label-ops-bootstrap
- Source window: `none`
- Required artifacts: director/reviews/iteration_1_review.json, director/reviews/iteration_1_review.md, director/reviews/iteration_1_patch_proposal.yaml, director/reviews/iteration_1_branch_plan.md, director/reviews/iteration_1_starter_prompt.md, director/reviews/iteration_1_approval.json
- Tags: review, closeout

#### Tasks
- `iteration1.review.generate_review` Generate iteration review
  - kind: `analysis` gate_class: `ops` automation: `partial`
  - depends_on: iteration1.labels.prepare_labeling_batch
  - inputs: docs/iteration_log.md
  - outputs: director/reviews/iteration_1_review.json, director/reviews/iteration_1_review.md, director/reviews/iteration_1_patch_proposal.yaml, director/reviews/iteration_1_branch_plan.md, director/reviews/iteration_1_starter_prompt.md
  - tags: review_generation
  - risks: R4, R7
- `iteration1.review.approve_closeout` Approve iteration closeout
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration1.review.generate_review
  - inputs: director/reviews/iteration_1_review.json
  - outputs: director/reviews/iteration_1_approval.json
  - tags: review_approval
  - risks: R4

### iteration1/diagnostics-nlp
- Title: Historical Diagnostics Baseline
- Goal: Preserved historical diagnostics work completed before roadmap-model v2.
- Lifecycle: `historical`
- Depends on: none
- Source window: `none`
- Required artifacts: reports/iteration1/phase0/baseline_report.md
- Tags: historical

#### Tasks
- phase-level only in this roadmap version

### iteration1/label-expansion-recovery
- Title: Superseded Recovery Label Expansion
- Goal: Preserved recovery branch work completed before roadmap-model v2.
- Lifecycle: `superseded`
- Depends on: none
- Source window: `none`
- Required artifacts: reports/iteration1/phase1_recovery/qa_report.json
- Tags: superseded

#### Tasks
- phase-level only in this roadmap version

### iteration1/irr-validation
- Title: Superseded Recovery IRR Workflow
- Goal: Preserved recovery IRR workflow completed before roadmap-model v2.
- Lifecycle: `superseded`
- Depends on: none
- Source window: `none`
- Required artifacts: reports/iteration1/phase2_irr/irr_status.json
- Tags: superseded

#### Tasks
- phase-level only in this roadmap version


## Iteration 2 - Rubric Realignment, Label Expansion, and Provisional Freeze
Goal: Realign the rubric to the proposal construct, rebuild tranche-based canonical labels under rubric v2.4, and provisionally freeze the rubric only after sufficiency and IRR gates pass.
Entry criteria: Iteration 1 review approved., Iteration 2 kickoff completed on iteration2/integration., Proposal methodology source and stakeholder expectations are both current.
Exit criteria: Rubric realignment report and revised protocol v2.4 are published., Tranche 1 is re-reviewed under rubric v2.4 before further canonical labeling proceeds., Sentence-pool expansion reaches 500 firms and at least 1,000 clean AI sentences in the 2024 candidate pool., At least 500 adjudicated labels with at least 80 labels per class are available before retraining., Human-human IRR exceeds 0.7 on a stratified, blinded 100+ item subset with by-class diagnostics., Provisional rubric freeze and split registry are published with zero held-out leakage., Preliminary stakeholder-facing results may be authorized separately for the active 2021-2024 window without authorizing publication-grade retraining., Iteration 2 review approved.

### iteration2/kickoff-and-preflight
- Title: Kickoff and Preflight
- Goal: Validate branch context and prior review approval before starting Iteration 2 work.
- Lifecycle: `planned`
- Depends on: iteration1/review-and-replan
- Source window: `none`
- Required artifacts: director/reviews/iteration_2_kickoff.json
- Tags: kickoff, branch_policy

#### Tasks
- `iteration2.kickoff.verify_context` Verify kickoff context
  - kind: `validation` gate_class: `ops` automation: `partial`
  - depends_on: none
  - inputs: director/reviews/iteration_1_approval.json
  - outputs: director/reviews/iteration_2_kickoff.json
  - tags: kickoff
  - risks: R4, R7

### iteration2/rubric-realignment
- Title: Rubric Realignment
- Goal: Confirm the cleaned tranche-1 slice under the accepted v2.4a prompt, then rebuild the full tranche through the cleaned extraction path before canonical tranche review resumes.
- Lifecycle: `planned`
- Depends on: iteration2/kickoff-and-preflight
- Source window: `active_2021_2024`
- Required artifacts: docs/labeling_protocol.md, reports/labels/tranche1_rubric_calibration_v2_4.md, data/labels/v1/labeling_batch_v1_prelabeled_v2_4_clean_slice40.csv, reports/labels/assistive_prelabel_tranche1_v2_4_clean_slice40_summary.json, data/labels/v1/labeling_batch_v1_filled_v2_4_clean_slice40.csv, reports/labels/tranche1_clean_slice_v2_4_check.json, reports/labels/tranche1_clean_slice_v2_4_check.md, data/labels/v1/labeling_batch_v1_reextracted_v2_4.csv, reports/labels/tranche1_reextraction_v2_4_summary.json, data/labels/v1/labeling_batch_v1_prelabeled_v2_4.csv, reports/labels/assistive_prelabel_tranche1_v2_4_summary.json, data/labels/v1/labeling_batch_v1_filled_v2_4.csv
- Tags: rubric_calibration, methodology_alignment

#### Tasks
- `iteration2.rubric.review_tranche1_error_patterns_v2_4` Review tranche 1 error patterns for rubric v2.4
  - kind: `analysis` gate_class: `science` automation: `manual`
  - depends_on: none
  - inputs: data/labels/v1/labeling_batch_v1_filled_v2_1_slice40.csv, docs/director/proposal_methodology.md
  - outputs: reports/labels/tranche1_rubric_calibration_v2_4.md
  - tags: rubric_calibration, proposal_alignment
  - risks: R1, R3
- `iteration2.rubric.publish_protocol_v2_4` Publish rubric v2.4 protocol
  - kind: `manual` gate_class: `science` automation: `manual`
  - depends_on: iteration2.rubric.review_tranche1_error_patterns_v2_4
  - inputs: reports/labels/tranche1_rubric_calibration_v2_4.md
  - outputs: docs/labeling_protocol.md
  - tags: rubric_calibration, protocol
  - risks: R1, R3
- `iteration2.rubric.generate_tranche1_clean_slice_prelables_v2_4` Generate tranche 1 clean-slice assistive prelabels under rubric v2.4
  - kind: `build` gate_class: `ops` automation: `partial`
  - depends_on: iteration2.rubric.publish_protocol_v2_4
  - inputs: data/labels/v1/labeling_batch_v1_reextracted_v2_2_slice40.csv, director/config/api_assistive_policy.yaml
  - outputs: data/labels/v1/labeling_batch_v1_prelabeled_v2_4_clean_slice40.csv, reports/labels/assistive_prelabel_tranche1_v2_4_clean_slice40_summary.json
  - tags: assistive_api, tranche1, calibration
  - risks: R1, R4
- `iteration2.rubric.initialize_tranche1_clean_slice_review_v2_4` Initialize tranche 1 clean-slice review sheet under rubric v2.4
  - kind: `build` gate_class: `ops` automation: `full`
  - depends_on: iteration2.rubric.generate_tranche1_clean_slice_prelables_v2_4
  - inputs: data/labels/v1/labeling_batch_v1_prelabeled_v2_4_clean_slice40.csv
  - outputs: data/labels/v1/labeling_batch_v1_filled_v2_4_clean_slice40.csv
  - tags: tranche1, calibration, review_sheet
  - risks: R1
- `iteration2.rubric.confirm_tranche1_clean_slice_v2_4` Confirm cleaned tranche 1 slice under rubric v2.4
  - kind: `validation` gate_class: `science` automation: `full`
  - depends_on: iteration2.rubric.initialize_tranche1_clean_slice_review_v2_4
  - inputs: data/labels/v1/labeling_batch_v1_filled_v2_1_slice40.csv, data/labels/v1/labeling_batch_v1_prelabeled_v2_4_clean_slice40.csv
  - outputs: reports/labels/tranche1_clean_slice_v2_4_check.json, reports/labels/tranche1_clean_slice_v2_4_check.md
  - tags: tranche1, calibration, validation
  - risks: R1, R3
- `iteration2.rubric.rebuild_tranche1_text_v2_4` Rebuild full tranche 1 text under cleaned extraction path
  - kind: `build` gate_class: `data` automation: `partial`
  - depends_on: iteration2.rubric.confirm_tranche1_clean_slice_v2_4
  - inputs: data/labels/v1/labeling_batch_v1.csv
  - outputs: data/labels/v1/labeling_batch_v1_reextracted_v2_4.csv, reports/labels/tranche1_reextraction_v2_4_summary.json
  - tags: tranche1, extraction, rebuild
  - risks: R1, R3
- `iteration2.rubric.regenerate_tranche1_assistive_prelabels_v2_4` Regenerate full tranche 1 assistive prelabels under rubric v2.4
  - kind: `build` gate_class: `ops` automation: `partial`
  - depends_on: iteration2.rubric.rebuild_tranche1_text_v2_4
  - inputs: data/labels/v1/labeling_batch_v1_reextracted_v2_4.csv, director/config/api_assistive_policy.yaml
  - outputs: data/labels/v1/labeling_batch_v1_prelabeled_v2_4.csv, reports/labels/assistive_prelabel_tranche1_v2_4_summary.json
  - tags: assistive_api, tranche1, calibration
  - risks: R1, R4
- `iteration2.rubric.initialize_tranche1_review_v2_4` Initialize full tranche 1 rubric-v2.4 review sheet
  - kind: `build` gate_class: `ops` automation: `full`
  - depends_on: iteration2.rubric.regenerate_tranche1_assistive_prelabels_v2_4
  - inputs: data/labels/v1/labeling_batch_v1_prelabeled_v2_4.csv
  - outputs: data/labels/v1/labeling_batch_v1_filled_v2_4.csv
  - tags: tranche1, review_sheet
  - risks: R1

### iteration2/tranche1-labeling
- Title: Tranche 1 Labeling
- Goal: Verify tranche 1 under rubric v2.4 after slice sign-off and regenerated assistive prelabels.
- Lifecycle: `planned`
- Depends on: iteration2/rubric-realignment
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/labeling_batch_v1_filled_v2_4.csv
- Tags: tranche1, human_labeling

#### Tasks
- `iteration2.labels.verify_tranche1_labels` Verify tranche 1 labels
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration2.rubric.initialize_tranche1_review_v2_4
  - inputs: data/labels/v1/labeling_batch_v1_prelabeled_v2_4.csv
  - outputs: data/labels/v1/labeling_batch_v1_filled_v2_4.csv
  - tags: human_labeling, tranche1
  - risks: R1, R3

### iteration2/sentence-pool-expansion-2024
- Title: Sentence Pool Expansion 2024
- Goal: Expand beyond tranche 1 into 4 resumable 125-firm batches, then combine them into a cumulative 500-firm, 1-2k clean AI sentence pool.
- Lifecycle: `planned`
- Depends on: iteration2/tranche1-labeling
- Source window: `active_2021_2024`
- Required artifacts: data/manifests/filings/expansion_2024_500_firms_v1.csv, data/processed/sentences/year=2024/expanded_ai_sentences.parquet, reports/labels/sentence_pool_expansion_2024_summary.json
- Tags: sentence_pool, scale, stakeholder_alignment

#### Tasks
- `iteration2.pool.expand_candidate_pool_batch_01` Expand candidate pool batch 01
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: none
  - inputs: data/metadata/available_filings_index.csv
  - outputs: data/manifests/filings/expansion_2024_batch_01.csv, data/processed/sentences/year=2024/expanded_ai_sentences_batch_01.parquet, reports/labels/sentence_pool_expansion_2024_batch_01_summary.json
  - tags: sentence_pool, scale, batch_01
  - risks: R2, R5
- `iteration2.pool.expand_candidate_pool_batch_02` Expand candidate pool batch 02
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: iteration2.pool.expand_candidate_pool_batch_01
  - inputs: data/metadata/available_filings_index.csv
  - outputs: data/manifests/filings/expansion_2024_batch_02.csv, data/processed/sentences/year=2024/expanded_ai_sentences_batch_02.parquet, reports/labels/sentence_pool_expansion_2024_batch_02_summary.json
  - tags: sentence_pool, scale, batch_02
  - risks: R2, R5
- `iteration2.pool.expand_candidate_pool_batch_03` Expand candidate pool batch 03
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: iteration2.pool.expand_candidate_pool_batch_02
  - inputs: data/metadata/available_filings_index.csv
  - outputs: data/manifests/filings/expansion_2024_batch_03.csv, data/processed/sentences/year=2024/expanded_ai_sentences_batch_03.parquet, reports/labels/sentence_pool_expansion_2024_batch_03_summary.json
  - tags: sentence_pool, scale, batch_03
  - risks: R2, R5
- `iteration2.pool.expand_candidate_pool_batch_04` Expand candidate pool batch 04
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: iteration2.pool.expand_candidate_pool_batch_03
  - inputs: data/metadata/available_filings_index.csv
  - outputs: data/manifests/filings/expansion_2024_batch_04.csv, data/processed/sentences/year=2024/expanded_ai_sentences_batch_04.parquet, reports/labels/sentence_pool_expansion_2024_batch_04_summary.json
  - tags: sentence_pool, scale, batch_04
  - risks: R2, R5
- `iteration2.pool.combine_candidate_pool_batches` Combine candidate pool batches
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: iteration2.pool.expand_candidate_pool_batch_04
  - inputs: none
  - outputs: data/manifests/filings/expansion_2024_500_firms_v1.csv, data/processed/sentences/year=2024/expanded_ai_sentences.parquet, reports/labels/sentence_pool_expansion_2024_summary.json
  - tags: sentence_pool, scale, combine
  - risks: R2, R5
- `iteration2.pool.verify_candidate_pool_targets` Verify sentence-pool targets
  - kind: `validation` gate_class: `data` automation: `partial`
  - depends_on: iteration2.pool.combine_candidate_pool_batches
  - inputs: reports/labels/sentence_pool_expansion_2024_summary.json
  - outputs: none
  - tags: sentence_pool_gate
  - risks: R2

### iteration2/tranche2-labeling
- Title: Tranche 2 Labeling
- Goal: Build, prelabel, and verify the first 160-row expanded tranche from the cumulative expanded sentence pool.
- Lifecycle: `planned`
- Depends on: iteration2/sentence-pool-expansion-2024
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/labeling_batch_v2.parquet, data/labels/v1/labeling_batch_v2.csv, reports/labels/labeling_batch_v2_summary.json, data/labels/v1/labeling_batch_v2_prelabeled.csv, reports/labels/assistive_prelabel_tranche2_summary.json, data/labels/v1/labeling_batch_v2_filled.csv
- Tags: tranche2, human_labeling

#### Tasks
- `iteration2.labels.prepare_tranche2_labeling_batch` Prepare tranche 2 labeling batch
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: iteration2.pool.verify_candidate_pool_targets
  - inputs: data/processed/sentences/year=2024/expanded_ai_sentences.parquet, data/manifests/filings/expansion_2024_500_firms_v1.csv, data/labels/v1/labeling_batch_v1.csv
  - outputs: data/labels/v1/labeling_batch_v2.parquet, data/labels/v1/labeling_batch_v2.csv, reports/labels/labeling_batch_v2_summary.json
  - tags: expanded_batch, tranche2
  - risks: R1, R2
- `iteration2.labels.generate_tranche2_assistive_prelabels` Generate tranche 2 assistive prelabels
  - kind: `build` gate_class: `ops` automation: `partial`
  - depends_on: iteration2.labels.prepare_tranche2_labeling_batch
  - inputs: data/labels/v1/labeling_batch_v2.csv, director/config/api_assistive_policy.yaml
  - outputs: data/labels/v1/labeling_batch_v2_prelabeled.csv, reports/labels/assistive_prelabel_tranche2_summary.json
  - tags: assistive_api, tranche2, prelabels
  - risks: R1, R4
- `iteration2.labels.verify_tranche2_labels` Verify tranche 2 labels
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration2.labels.generate_tranche2_assistive_prelabels
  - inputs: data/labels/v1/labeling_batch_v2_prelabeled.csv
  - outputs: data/labels/v1/labeling_batch_v2_filled.csv
  - tags: human_labeling, tranche2
  - risks: R1, R3

### iteration2/tranche3-labeling
- Title: Tranche 3 Labeling
- Goal: Build, prelabel, and verify the second 160-row expanded tranche from the cumulative expanded sentence pool.
- Lifecycle: `planned`
- Depends on: iteration2/tranche2-labeling
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/labeling_batch_v3.parquet, data/labels/v1/labeling_batch_v3.csv, reports/labels/labeling_batch_v3_summary.json, data/labels/v1/labeling_batch_v3_prelabeled.csv, reports/labels/assistive_prelabel_tranche3_summary.json, data/labels/v1/labeling_batch_v3_filled.csv
- Tags: tranche3, human_labeling

#### Tasks
- `iteration2.labels.prepare_tranche3_labeling_batch` Prepare tranche 3 labeling batch
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: iteration2.labels.verify_tranche2_labels
  - inputs: data/processed/sentences/year=2024/expanded_ai_sentences.parquet, data/manifests/filings/expansion_2024_500_firms_v1.csv, data/labels/v1/labeling_batch_v1.csv
  - outputs: data/labels/v1/labeling_batch_v3.parquet, data/labels/v1/labeling_batch_v3.csv, reports/labels/labeling_batch_v3_summary.json
  - tags: expanded_batch, tranche3
  - risks: R1, R2
- `iteration2.labels.generate_tranche3_assistive_prelabels` Generate tranche 3 assistive prelabels
  - kind: `build` gate_class: `ops` automation: `partial`
  - depends_on: iteration2.labels.prepare_tranche3_labeling_batch
  - inputs: data/labels/v1/labeling_batch_v3.csv, director/config/api_assistive_policy.yaml
  - outputs: data/labels/v1/labeling_batch_v3_prelabeled.csv, reports/labels/assistive_prelabel_tranche3_summary.json
  - tags: assistive_api, tranche3, prelabels
  - risks: R1, R4
- `iteration2.labels.verify_tranche3_labels` Verify tranche 3 labels
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration2.labels.generate_tranche3_assistive_prelabels
  - inputs: data/labels/v1/labeling_batch_v3_prelabeled.csv
  - outputs: data/labels/v1/labeling_batch_v3_filled.csv
  - tags: human_labeling, tranche3
  - risks: R1, R3

### iteration2/merge-canonical-labels
- Title: Merge Canonical Labels
- Goal: Merge the three verified tranches into the canonical label master after proposal-faithful tranche 1 review.
- Lifecycle: `planned`
- Depends on: iteration2/tranche3-labeling
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/labels_master.parquet, data/labels/v1/labels_master_review.csv, reports/labels/label_expansion_summary.json
- Tags: merge_labels, stakeholder_alignment

#### Tasks
- `iteration2.labels.merge_canonical_labels` Merge canonical labels
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: iteration2.labels.verify_tranche1_labels, iteration2.labels.verify_tranche2_labels, iteration2.labels.verify_tranche3_labels
  - inputs: data/labels/v1/labeling_batch_v1_filled_v2_4.csv, data/labels/v1/labeling_batch_v2_filled.csv, data/labels/v1/labeling_batch_v3_filled.csv
  - outputs: data/labels/v1/labels_master.parquet, data/labels/v1/labels_master_review.csv, reports/labels/label_expansion_summary.json
  - tags: human_labeling, merge_labels
  - risks: R1, R2, R3

### iteration2/irr-and-adjudication
- Title: IRR and Adjudication
- Goal: Run proposal-style human-human IRR on a stratified 100+ firm subset, publish by-class diagnostics, and adjudicate disagreements.
- Lifecycle: `planned`
- Depends on: iteration2/merge-canonical-labels
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/irr_subset.parquet, reports/labels/irr_report.json, data/labels/v1/adjudication.parquet
- Tags: irr, adjudication, sentence_quality_gate

#### Tasks
- `iteration2.shared.audit_sentence_integrity` Audit IRR sentence integrity
  - kind: `diagnostic` gate_class: `data` automation: `partial`
  - depends_on: none
  - inputs: data/labels/v1/labels_master_review.csv
  - outputs: reports/labels/irr_sentence_quality.json
  - tags: sentence_quality_gate
  - risks: R1, R5
- `iteration2.irr.prepare_subset_handoff` Prepare blinded IRR subset handoff
  - kind: `build` gate_class: `data` automation: `full`
  - depends_on: iteration2.shared.audit_sentence_integrity
  - inputs: data/labels/v1/labels_master_review.csv
  - outputs: data/labels/v1/irr_subset.parquet, data/labels/v1/irr_subset_master.csv, data/labels/v1/irr_subset_rater2_blinded.csv, data/labels/v1/irr_subset_rater2_blinded.xlsx, reports/labels/irr_subset_sampling_report.json, reports/labels/irr_attestation.json
  - tags: human_irr, sampling
  - risks: R1, R3
- `iteration2.irr.collect_rater2_labels` Collect blinded second-rater labels
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration2.irr.prepare_subset_handoff
  - inputs: data/labels/v1/irr_subset_rater2_blinded.xlsx
  - outputs: data/labels/v1/irr_subset_rater2_completed.xlsx
  - tags: human_irr, rater2
  - risks: R1, R3
- `iteration2.irr.compute_and_seed_adjudication` Compute IRR status and seed adjudication
  - kind: `analysis` gate_class: `data` automation: `full`
  - depends_on: iteration2.irr.prepare_subset_handoff
  - inputs: data/labels/v1/irr_subset_master.csv, reports/labels/irr_attestation.json, reports/labels/irr_subset_sampling_report.json
  - outputs: reports/labels/irr_report.json, data/labels/v1/irr_adjudication_sheet.csv, data/labels/v1/irr_adjudication_sheet.xlsx, data/labels/v1/adjudication.parquet
  - tags: human_irr, adjudication
  - risks: R1, R3
- `iteration2.irr.finalize_adjudication_and_report` Finalize adjudication and publish final IRR report
  - kind: `validation` gate_class: `manual` automation: `partial`
  - depends_on: iteration2.irr.collect_rater2_labels, iteration2.irr.compute_and_seed_adjudication
  - inputs: data/labels/v1/irr_subset_rater2_completed.xlsx, data/labels/v1/irr_adjudication_completed.xlsx
  - outputs: reports/labels/irr_report.json, data/labels/v1/adjudication.parquet
  - tags: human_irr, finalization
  - risks: R1, R3

### iteration2/irr-disagreement-diagnostic
- Title: IRR Disagreement Diagnostic
- Goal: Publish a secondary disagreement diagnostic package that explains where the failed canonical IRR is concentrated without rewriting the headline IRR result.
- Lifecycle: `planned`
- Depends on: iteration2/merge-canonical-labels
- Source window: `active_2021_2024`
- Required artifacts: reports/labels/irr_disagreement_diagnostic_v1.json, reports/labels/irr_disagreement_rows_v1.csv
- Tags: irr, disagreement_diagnostic, preliminary_results

#### Tasks
- `iteration2.irr.publish_disagreement_diagnostic` Publish IRR disagreement diagnostic
  - kind: `analysis` gate_class: `science` automation: `full`
  - depends_on: none
  - inputs: data/labels/v1/irr_subset_master.csv, data/labels/v1/irr_subset_rater2_completed.xlsx, data/labels/v1/adjudication.parquet, reports/labels/irr_report.json
  - outputs: reports/labels/irr_disagreement_diagnostic_v1.json, reports/labels/irr_disagreement_rows_v1.csv
  - tags: irr, disagreement_diagnostic
  - risks: R1, R3

### iteration2/provisional-rubric-freeze-and-split-registry
- Title: Provisional Rubric Freeze and Split Registry
- Goal: Freeze the rubric provisionally for scale-up, generate the split registry, and preserve zero held-out leakage before retraining.
- Lifecycle: `planned`
- Depends on: iteration2/irr-and-adjudication
- Source window: `active_2021_2024`
- Required artifacts: data/metadata/splits/split_registry_v1.csv, data/metadata/splits/split_registry_v1.json, reports/labels/rubric_freeze_v2.json
- Tags: split_registry, rubric_freeze, methodology_alignment

#### Tasks
- `iteration2.splits.freeze_registry` Freeze split registry
  - kind: `build` gate_class: `data` automation: `partial`
  - depends_on: none
  - inputs: data/labels/v1/adjudication.parquet
  - outputs: data/metadata/splits/split_registry_v1.csv, data/metadata/splits/split_registry_v1.json
  - tags: split_registry
  - risks: R3, R6
- `iteration2.rubric.publish_provisional_freeze` Publish provisional rubric freeze
  - kind: `manual` gate_class: `science` automation: `manual`
  - depends_on: iteration2.splits.freeze_registry
  - inputs: reports/labels/irr_report.json
  - outputs: reports/labels/rubric_freeze_v2.json
  - tags: rubric_freeze, methodology_alignment
  - risks: R1, R3

### iteration2/label-sufficiency-gate
- Title: Label Sufficiency Gate
- Goal: Publish and verify the modeling readiness report only after proposal-style IRR, split freeze, and provisional rubric freeze are complete.
- Lifecycle: `planned`
- Depends on: iteration2/provisional-rubric-freeze-and-split-registry
- Source window: `active_2021_2024`
- Required artifacts: reports/models/modeling_readiness_gate.json
- Tags: modeling_gate, stakeholder_alignment

#### Tasks
- `iteration2.labels.publish_modeling_readiness_report` Publish modeling readiness report
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: none
  - inputs: data/labels/v1/labels_master.parquet, reports/labels/irr_report.json, data/metadata/splits/split_registry_v1.csv, reports/labels/rubric_freeze_v2.json
  - outputs: reports/models/modeling_readiness_gate.json
  - tags: modeling_gate
  - risks: R1, R3
- `iteration2.labels.verify_label_sufficiency` Verify label sufficiency
  - kind: `validation` gate_class: `science` automation: `partial`
  - depends_on: iteration2.labels.publish_modeling_readiness_report
  - inputs: reports/models/modeling_readiness_gate.json
  - outputs: none
  - tags: modeling_gate
  - risks: R1, R3

### iteration2/preliminary-results-authorization
- Title: Preliminary Results Authorization
- Goal: Publish a separate active-window readiness report that authorizes stakeholder-facing preliminary results without weakening the blocked publication-grade gate.
- Lifecycle: `planned`
- Depends on: iteration2/irr-disagreement-diagnostic
- Source window: `active_2021_2024`
- Required artifacts: reports/models/preliminary_results_readiness_v1.json
- Tags: preliminary_results, stakeholder_alignment, readiness

#### Tasks
- `iteration2.prelim.publish_preliminary_results_readiness` Publish preliminary results readiness
  - kind: `analysis` gate_class: `science` automation: `full`
  - depends_on: none
  - inputs: data/labels/v1/labels_master.parquet, reports/labels/irr_report.json, reports/labels/irr_disagreement_diagnostic_v1.json, data/metadata/splits/split_registry_v1.csv, data/metadata/splits/split_registry_v1.json, reports/labels/rubric_freeze_v2.json
  - outputs: reports/models/preliminary_results_readiness_v1.json
  - tags: preliminary_results, stakeholder_alignment
  - risks: R1, R3

### iteration2/review-and-replan
- Title: Review and Replan
- Goal: Synthesize iteration evidence, approve closeout, and prepare the next iteration handoff.
- Lifecycle: `planned`
- Depends on: iteration2/label-sufficiency-gate
- Source window: `none`
- Required artifacts: director/reviews/iteration_2_review.json, director/reviews/iteration_2_review.md, director/reviews/iteration_2_patch_proposal.yaml, director/reviews/iteration_2_branch_plan.md, director/reviews/iteration_2_starter_prompt.md, director/reviews/iteration_2_approval.json
- Tags: review, closeout

#### Tasks
- `iteration2.review.generate_review` Generate iteration review
  - kind: `analysis` gate_class: `ops` automation: `partial`
  - depends_on: iteration2.labels.verify_label_sufficiency
  - inputs: docs/iteration_log.md
  - outputs: director/reviews/iteration_2_review.json, director/reviews/iteration_2_review.md, director/reviews/iteration_2_patch_proposal.yaml, director/reviews/iteration_2_branch_plan.md, director/reviews/iteration_2_starter_prompt.md
  - tags: review_generation
  - risks: R4, R7
- `iteration2.review.approve_closeout` Approve iteration closeout
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration2.review.generate_review
  - inputs: director/reviews/iteration_2_review.json
  - outputs: director/reviews/iteration_2_approval.json
  - tags: review_approval
  - risks: R4


## Iteration 3 - Retraining, Measure Construction, and Development Predictive Validity
Goal: Retrain on the proposal-aligned adjudicated labels, build named firm-year measures, and test whether the rubric directionally predicts later AI capability before publication-scale deployment.
Entry criteria: Iteration 2 review approved., Iteration 3 kickoff completed on iteration3/integration., Label sufficiency gate passed with at least 500 adjudicated labels, at least 80 labels per class, human-human IRR > 0.7, and provisional rubric freeze recorded.
Exit criteria: Retraining, held-out evaluation, active-window classification, and ai_total merge-integrity QA are complete., Named firm-year narrative measures are published explicitly., Development predictive-validity gate is documented before publication-scale rollout., Iteration 3 review approved.

### iteration3/preliminary-kickoff-and-preflight
- Title: Preliminary Kickoff and Preflight
- Goal: Confirm that the active-window preliminary lane is authorized and remains explicitly separate from the blocked publication-grade path.
- Lifecycle: `planned`
- Depends on: iteration2/preliminary-results-authorization
- Source window: `active_2021_2024`
- Required artifacts: reports/models/preliminary_results_readiness_v1.json
- Tags: preliminary_results, kickoff

#### Tasks
- phase-level only in this roadmap version

### iteration3/preliminary-centroid-retraining
- Title: Preliminary Centroid Retraining
- Goal: Train a preliminary-only model namespace for the active 2021-2024 window without overwriting publication-grade artifacts.
- Lifecycle: `planned`
- Depends on: iteration3/preliminary-kickoff-and-preflight
- Source window: `active_2021_2024`
- Required artifacts: artifacts/models/mpnet_prelim_v1/embeddings.parquet, artifacts/models/mpnet_prelim_v1/centroids.json, artifacts/models/mpnet_prelim_v1/metadata.json
- Tags: preliminary_results, retraining

#### Tasks
- phase-level only in this roadmap version

### iteration3/preliminary-heldout-evaluation
- Title: Preliminary Held-Out Evaluation
- Goal: Evaluate the preliminary model truthfully on the frozen held-out split without relaxing leakage checks or implying publication-grade authorization.
- Lifecycle: `planned`
- Depends on: iteration3/preliminary-centroid-retraining
- Source window: `active_2021_2024`
- Required artifacts: reports/evaluation/heldout_eval_prelim_v1.json
- Tags: preliminary_results, evaluation

#### Tasks
- phase-level only in this roadmap version

### iteration3/preliminary-active-window-classification
- Title: Preliminary Active Window Classification
- Goal: Classify the active 2021-2024 source window into a separate preliminary artifact namespace for internal results work.
- Lifecycle: `planned`
- Depends on: iteration3/preliminary-heldout-evaluation
- Source window: `active_2021_2024`
- Required artifacts: data/processed/classifications/year=2021/model=mpnet_prelim_v1/classified_sentences.parquet, data/processed/classifications/year=2022/model=mpnet_prelim_v1/classified_sentences.parquet, data/processed/classifications/year=2023/model=mpnet_prelim_v1/classified_sentences.parquet, data/processed/classifications/year=2024/model=mpnet_prelim_v1/classified_sentences.parquet, reports/classification/active_window_coverage_prelim_v1.json
- Tags: preliminary_results, batch_classification

#### Tasks
- phase-level only in this roadmap version

### iteration3/preliminary-firm-year-measure-construction
- Title: Preliminary Firm-Year Measure Construction
- Goal: Build preliminary-only firm-year AI metrics and narrative measures for internal 2021-2024 stakeholder results.
- Lifecycle: `planned`
- Depends on: iteration3/preliminary-active-window-classification
- Source window: `active_2021_2024`
- Required artifacts: data/processed/aggregates/firm_year_ai_metrics_prelim_v1.parquet, data/processed/aggregates/firm_year_narrative_measures_prelim_v1.parquet, reports/classification/firm_year_narrative_measures_prelim_v1.json
- Tags: preliminary_results, measures

#### Tasks
- phase-level only in this roadmap version

### iteration3/kickoff-and-preflight
- Title: Kickoff and Preflight
- Goal: Validate branch context and prior review approval before starting Iteration 3 work.
- Lifecycle: `planned`
- Depends on: iteration2/review-and-replan
- Source window: `none`
- Required artifacts: director/reviews/iteration_3_kickoff.json
- Tags: kickoff, branch_policy

#### Tasks
- `iteration3.kickoff.verify_context` Verify kickoff context
  - kind: `validation` gate_class: `ops` automation: `partial`
  - depends_on: none
  - inputs: director/reviews/iteration_2_approval.json
  - outputs: director/reviews/iteration_3_kickoff.json
  - tags: kickoff
  - risks: R4, R7

### iteration3/centroid-retraining
- Title: Centroid Retraining
- Goal: Embed the adjudicated training set, compute centroids, and fingerprint the baseline publication candidate model.
- Lifecycle: `planned`
- Depends on: iteration3/kickoff-and-preflight
- Source window: `active_2021_2024`
- Required artifacts: artifacts/models/mpnet_v1/embeddings.parquet, artifacts/models/mpnet_v1/centroids.json, artifacts/models/mpnet_v1/metadata.json
- Tags: retraining

#### Tasks
- phase-level only in this roadmap version

### iteration3/mpnet-finetuning-benchmark
- Title: MPNet Fine-Tuning Benchmark
- Goal: Benchmark whether fine-tuning MPNet on the expanded adjudicated dataset materially improves publication-grade classifier performance.
- Lifecycle: `planned`
- Depends on: iteration3/centroid-retraining
- Source window: `active_2021_2024`
- Required artifacts: reports/evaluation/mpnet_finetuning_benchmark_v1.json
- Tags: model_benchmark, fine_tuning

#### Tasks
- phase-level only in this roadmap version

### iteration3/classifier-calibration-and-heldout-eval
- Title: Classifier Calibration and Held-Out Eval
- Goal: Calibrate thresholds on validation only and evaluate the publication candidate classifier on the frozen held-out set.
- Lifecycle: `planned`
- Depends on: iteration3/mpnet-finetuning-benchmark
- Source window: `active_2021_2024`
- Required artifacts: reports/evaluation/calibration_v1.json, reports/evaluation/heldout_eval_v1.json
- Tags: calibration, evaluation

#### Tasks
- phase-level only in this roadmap version

### iteration3/active-window-batch-classification
- Title: Active Window Batch Classification
- Goal: Classify the active 2021–2024 source window with coverage and skip auditing.
- Lifecycle: `planned`
- Depends on: iteration3/classifier-calibration-and-heldout-eval
- Source window: `active_2021_2024`
- Required artifacts: data/processed/classifications/year=2021/model=mpnet_v1/classified_sentences.parquet, data/processed/classifications/year=2022/model=mpnet_v1/classified_sentences.parquet, data/processed/classifications/year=2023/model=mpnet_v1/classified_sentences.parquet, data/processed/classifications/year=2024/model=mpnet_v1/classified_sentences.parquet, reports/classification/active_window_coverage_v1.json
- Tags: batch_classification

#### Tasks
- phase-level only in this roadmap version

### iteration3/classification-merge-integrity
- Title: Classification Merge Integrity
- Goal: Aggregate sentence-level classifications, verify ai_total integrity, and QA the active-window firm-year snapshot before panel work.
- Lifecycle: `planned`
- Depends on: iteration3/active-window-batch-classification
- Source window: `active_2021_2024`
- Required artifacts: data/processed/aggregates/firm_year_ai_metrics_v1.parquet, reports/classification/aggregation_qa_v1.json, reports/classification/merge_integrity_v1.json
- Tags: aggregation, merge_integrity

#### Tasks
- `iteration3.merge.verify_outputs` Verify classification merge integrity outputs
  - kind: `validation` gate_class: `ops` automation: `partial`
  - depends_on: none
  - inputs: none
  - outputs: data/processed/aggregates/firm_year_ai_metrics_v1.parquet, reports/classification/aggregation_qa_v1.json, reports/classification/merge_integrity_v1.json
  - tags: phase_completion_gate
  - risks: R4

### iteration3/firm-year-measure-construction
- Title: Firm-Year Measure Construction
- Goal: Construct the proposal-defined firm-year narrative measures AI Focus, log(1+A), log(1+S), SpecShare, CredAI, and A_S from the classified disclosure outputs.
- Lifecycle: `planned`
- Depends on: iteration3/classification-merge-integrity
- Source window: `active_2021_2024`
- Required artifacts: data/processed/aggregates/firm_year_narrative_measures_v1.parquet, reports/classification/firm_year_narrative_measures_v1.json
- Tags: measures, methodology_alignment

#### Tasks
- `iteration3.measures.publish_firm_year_measures` Publish firm-year narrative measures
  - kind: `manual` gate_class: `science` automation: `manual`
  - depends_on: iteration3.merge.verify_outputs
  - inputs: data/processed/aggregates/firm_year_ai_metrics_v1.parquet
  - outputs: data/processed/aggregates/firm_year_narrative_measures_v1.parquet, reports/classification/firm_year_narrative_measures_v1.json
  - tags: firm_year_measures, proposal_alignment
  - risks: R2, R6

### iteration3/development-predictive-validity-gate
- Title: Development Predictive-Validity Gate
- Goal: Document whether the proposal-aligned rubric and firm-year measures directionally predict later AI capability outcomes before publication-scale deployment.
- Lifecycle: `planned`
- Depends on: iteration3/firm-year-measure-construction
- Source window: `active_2021_2024`
- Required artifacts: reports/evaluation/development_predictive_validity_v1.json
- Tags: predictive_validity, methodology_alignment

#### Tasks
- `iteration3.validity.publish_development_predictive_validity` Publish development predictive-validity report
  - kind: `manual` gate_class: `science` automation: `manual`
  - depends_on: iteration3.measures.publish_firm_year_measures
  - inputs: reports/classification/firm_year_narrative_measures_v1.json
  - outputs: reports/evaluation/development_predictive_validity_v1.json
  - tags: predictive_validity, proposal_alignment
  - risks: R2, R6

### iteration3/review-and-replan
- Title: Review and Replan
- Goal: Synthesize iteration evidence, approve closeout, and prepare the next iteration handoff.
- Lifecycle: `planned`
- Depends on: iteration3/development-predictive-validity-gate
- Source window: `none`
- Required artifacts: director/reviews/iteration_3_review.json, director/reviews/iteration_3_review.md, director/reviews/iteration_3_patch_proposal.yaml, director/reviews/iteration_3_branch_plan.md, director/reviews/iteration_3_starter_prompt.md, director/reviews/iteration_3_approval.json
- Tags: review, closeout

#### Tasks
- `iteration3.review.generate_review` Generate iteration review
  - kind: `analysis` gate_class: `ops` automation: `partial`
  - depends_on: iteration3.validity.publish_development_predictive_validity
  - inputs: docs/iteration_log.md
  - outputs: director/reviews/iteration_3_review.json, director/reviews/iteration_3_review.md, director/reviews/iteration_3_patch_proposal.yaml, director/reviews/iteration_3_branch_plan.md, director/reviews/iteration_3_starter_prompt.md
  - tags: review_generation
  - risks: R4, R7
- `iteration3.review.approve_closeout` Approve iteration closeout
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration3.review.generate_review
  - inputs: director/reviews/iteration_3_review.json
  - outputs: director/reviews/iteration_3_approval.json
  - tags: review_approval
  - risks: R4


## Iteration 4 - Panel Construction, Robustness Inputs, and Publication Scope Expansion
Goal: Build the active-window panel, add stakeholder-requested robustness inputs, and prepare or execute broader publication-scope expansion as source availability permits.
Entry criteria: Iteration 3 review approved., Iteration 4 kickoff completed on iteration4/integration.
Exit criteria: Active-window panel is assembled and QA-frozen., Job-postings robustness inputs are integrated., Publication-scope expansion readiness is recorded for all-public-firm / longer-horizon coverage., Iteration 4 review approved.

### iteration4/preliminary-patents-and-controls-ingestion
- Title: Preliminary Patents and Controls Ingestion
- Goal: Refresh or document the reuse of patents and controls inputs for the active-window preliminary panel lane.
- Lifecycle: `planned`
- Depends on: iteration3/preliminary-firm-year-measure-construction
- Source window: `active_2021_2024`
- Required artifacts: reports/panels/preliminary_inputs_manifest_v1.json
- Tags: preliminary_results, panel_inputs

#### Tasks
- phase-level only in this roadmap version

### iteration4/preliminary-panel-assembly-2021-2024
- Title: Preliminary Panel Assembly 2021-2024
- Goal: Assemble a separate preliminary 2021-2024 panel for internal stakeholder-facing results without touching canonical panel artifacts.
- Lifecycle: `planned`
- Depends on: iteration4/preliminary-patents-and-controls-ingestion
- Source window: `active_2021_2024`
- Required artifacts: data/panels/panel_prelim_v1.parquet, data/panels/panel_prelim_v1.csv, reports/panels/panel_prelim_merge_coverage_v1.json
- Tags: preliminary_results, panel

#### Tasks
- phase-level only in this roadmap version

### iteration4/preliminary-panel-qa
- Title: Preliminary Panel QA
- Goal: Run preliminary panel QA and document that outputs remain preliminary-only and active-window scoped.
- Lifecycle: `planned`
- Depends on: iteration4/preliminary-panel-assembly-2021-2024
- Source window: `active_2021_2024`
- Required artifacts: reports/panels/panel_prelim_qa_v1.json
- Tags: preliminary_results, panel_qa

#### Tasks
- phase-level only in this roadmap version

### iteration4/kickoff-and-preflight
- Title: Kickoff and Preflight
- Goal: Validate branch context and prior review approval before starting Iteration 4 work.
- Lifecycle: `planned`
- Depends on: iteration3/review-and-replan
- Source window: `none`
- Required artifacts: director/reviews/iteration_4_kickoff.json
- Tags: kickoff, branch_policy

#### Tasks
- `iteration4.kickoff.verify_context` Verify kickoff context
  - kind: `validation` gate_class: `ops` automation: `partial`
  - depends_on: none
  - inputs: director/reviews/iteration_3_approval.json
  - outputs: director/reviews/iteration_4_kickoff.json
  - tags: kickoff
  - risks: R4, R7

### iteration4/patents-and-controls-ingestion
- Title: Patents and Controls Ingestion
- Goal: Refresh patents, controls, crosswalks, and ai_total-safe merge inputs required for panel construction and publication robustness.
- Lifecycle: `planned`
- Depends on: iteration4/kickoff-and-preflight
- Source window: `active_2021_2024`
- Required artifacts: data/interim/patents/patent_metrics_v1.parquet, data/interim/controls/controls_v1.parquet
- Tags: panel_inputs

#### Tasks
- phase-level only in this roadmap version

### iteration4/panel-assembly-2021-2024
- Title: Panel Assembly 2021-2024
- Goal: Merge active-window AI metrics with patents and controls into the canonical panel while preserving merge integrity for publication analysis.
- Lifecycle: `planned`
- Depends on: iteration4/patents-and-controls-ingestion
- Source window: `active_2021_2024`
- Required artifacts: data/panels/panel_v1.parquet, data/panels/panel_v1.csv, reports/panels/panel_merge_coverage_v1.json
- Tags: panel

#### Tasks
- phase-level only in this roadmap version

### iteration4/panel-qa-and-freeze
- Title: Panel QA and Freeze
- Goal: Validate panel schema, missingness, transformations, and publication-grade QA checks before freezing panel v1.
- Lifecycle: `planned`
- Depends on: iteration4/panel-assembly-2021-2024
- Source window: `active_2021_2024`
- Required artifacts: reports/panels/panel_v1_qa.json
- Tags: panel_qa

#### Tasks
- phase-level only in this roadmap version

### iteration4/job-postings-robustness-integration
- Title: Job Postings Robustness Integration
- Goal: Integrate job postings as a stakeholder-requested robustness input for publication analysis.
- Lifecycle: `planned`
- Depends on: iteration4/panel-qa-and-freeze
- Source window: `active_2021_2024`
- Required artifacts: data/interim/job_postings/job_postings_v1.parquet, reports/panels/job_postings_robustness_qa.json
- Tags: robustness, job_postings

#### Tasks
- `iteration4.job_postings.verify_outputs` Verify job-postings robustness outputs
  - kind: `validation` gate_class: `ops` automation: `partial`
  - depends_on: none
  - inputs: none
  - outputs: data/interim/job_postings/job_postings_v1.parquet, reports/panels/job_postings_robustness_qa.json
  - tags: phase_completion_gate
  - risks: R4

### iteration4/historical-window-expansion-readiness
- Title: Historical and All-Public-Firm Expansion Readiness
- Goal: Determine whether longer-horizon and all-public-firm source availability permits publication-scope expansion beyond the active development window.
- Lifecycle: `deferred`
- Depends on: iteration4/panel-qa-and-freeze
- Source window: `historical_2000_2020`
- Required artifacts: reports/data/publication_scope_expansion_readiness.json
- Tags: historical_backfill, publication_scope

#### Tasks
- phase-level only in this roadmap version

### iteration4/review-and-replan
- Title: Review and Replan
- Goal: Synthesize iteration evidence, approve closeout, and prepare the next iteration handoff.
- Lifecycle: `planned`
- Depends on: iteration4/job-postings-robustness-integration
- Source window: `none`
- Required artifacts: director/reviews/iteration_4_review.json, director/reviews/iteration_4_review.md, director/reviews/iteration_4_patch_proposal.yaml, director/reviews/iteration_4_branch_plan.md, director/reviews/iteration_4_starter_prompt.md, director/reviews/iteration_4_approval.json
- Tags: review, closeout

#### Tasks
- `iteration4.review.generate_review` Generate iteration review
  - kind: `analysis` gate_class: `ops` automation: `partial`
  - depends_on: iteration4.job_postings.verify_outputs
  - inputs: docs/iteration_log.md
  - outputs: director/reviews/iteration_4_review.json, director/reviews/iteration_4_review.md, director/reviews/iteration_4_patch_proposal.yaml, director/reviews/iteration_4_branch_plan.md, director/reviews/iteration_4_starter_prompt.md
  - tags: review_generation
  - risks: R4, R7
- `iteration4.review.approve_closeout` Approve iteration closeout
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration4.review.generate_review
  - inputs: director/reviews/iteration_4_review.json
  - outputs: director/reviews/iteration_4_approval.json
  - tags: review_approval
  - risks: R4


## Iteration 5 - Publication Outputs, Robustness, and Paper Package
Goal: Produce publication-oriented analysis outputs, stakeholder-requested robustness, and a paper/results package without turning significance into an optimization target.
Entry criteria: Iteration 4 review approved., Iteration 5 kickoff completed on iteration5/integration.
Exit criteria: Publication regressions, robustness outputs, differentiation artifacts, and paper/results package are complete., Iteration 5 review approved.

### iteration5/preliminary-regression-specification
- Title: Preliminary Regression Specification
- Goal: Freeze preliminary active-window regression inputs and baseline internal-result specifications without implying publication-grade release readiness.
- Lifecycle: `planned`
- Depends on: iteration4/preliminary-panel-qa
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/regression_specification_prelim_v1.json
- Tags: preliminary_results, analysis

#### Tasks
- phase-level only in this roadmap version

### iteration5/preliminary-results-generation
- Title: Preliminary Results Generation
- Goal: Produce an internal preliminary results manifest for the active 2021-2024 window while keeping publication-grade claims closed.
- Lifecycle: `planned`
- Depends on: iteration5/preliminary-regression-specification
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/results_manifest_prelim_v1.json
- Tags: preliminary_results, analysis

#### Tasks
- phase-level only in this roadmap version

### iteration5/preliminary-results-package
- Title: Preliminary Results Package
- Goal: Package preliminary stakeholder-facing outputs in a separate release manifest that clearly marks the active-window scope and non-publication status.
- Lifecycle: `planned`
- Depends on: iteration5/preliminary-results-generation
- Source window: `active_2021_2024`
- Required artifacts: reports/release/preliminary_release_manifest_v1.json
- Tags: preliminary_results, release

#### Tasks
- phase-level only in this roadmap version

### iteration5/preliminary-results-table-planning
- Title: Preliminary Results Table Planning
- Goal: Preserve a deferred planning placeholder for the first internal draft table set after we inspect the preliminary panel and results outputs.
- Lifecycle: `deferred`
- Depends on: iteration5/preliminary-results-generation
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/preliminary_results_table_plan_v1.md
- Tags: preliminary_results, planning

#### Tasks
- `iteration5.prelim.define_first_results_tables` Define first preliminary results tables
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: none
  - inputs: reports/analysis/results_manifest_prelim_v1.json
  - outputs: reports/analysis/preliminary_results_table_plan_v1.md
  - tags: preliminary_results, planning
  - risks: R2

### iteration5/kickoff-and-preflight
- Title: Kickoff and Preflight
- Goal: Validate branch context and prior review approval before starting Iteration 5 work.
- Lifecycle: `planned`
- Depends on: iteration4/review-and-replan
- Source window: `none`
- Required artifacts: director/reviews/iteration_5_kickoff.json
- Tags: kickoff, branch_policy

#### Tasks
- `iteration5.kickoff.verify_context` Verify kickoff context
  - kind: `validation` gate_class: `ops` automation: `partial`
  - depends_on: none
  - inputs: director/reviews/iteration_4_approval.json
  - outputs: director/reviews/iteration_5_kickoff.json
  - tags: kickoff
  - risks: R4, R7

### iteration5/regression-specification
- Title: Regression Specification
- Goal: Freeze regression inputs and define baseline, lagged, and industry-control robustness specifications for publication.
- Lifecycle: `planned`
- Depends on: iteration5/kickoff-and-preflight
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/regression_specification_v1.json
- Tags: analysis

#### Tasks
- phase-level only in this roadmap version

### iteration5/results-generation
- Title: Results Generation
- Goal: Run baseline models and generate the initial tables, figures, and short-intro-ready result package with provenance.
- Lifecycle: `planned`
- Depends on: iteration5/regression-specification
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/results_manifest_v1.json
- Tags: analysis

#### Tasks
- phase-level only in this roadmap version

### iteration5/robustness-and-sensitivity
- Title: Robustness and Sensitivity
- Goal: Run patent mismatch x A/S ratio, job postings, lagged t+1/t+2, and industry FE/SIC-bucket robustness checks.
- Lifecycle: `planned`
- Depends on: iteration5/results-generation
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/robustness_summary_v1.json
- Tags: analysis

#### Tasks
- phase-level only in this roadmap version

### iteration5/literature-differentiation-and-examples
- Title: Literature Differentiation and Examples
- Goal: Publish the literature differentiation table and before/after classification examples required for the paper package.
- Lifecycle: `planned`
- Depends on: iteration5/robustness-and-sensitivity
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/literature_differentiation_v1.md, reports/analysis/classification_examples_v1.md
- Tags: publication_package, differentiation

#### Tasks
- phase-level only in this roadmap version

### iteration5/release-packaging
- Title: Release Packaging
- Goal: Package the paper/results set, supporting artifacts, and reproducibility notes for research release.
- Lifecycle: `planned`
- Depends on: iteration5/literature-differentiation-and-examples
- Source window: `active_2021_2024`
- Required artifacts: reports/release/release_manifest_v1.json
- Tags: release

#### Tasks
- `iteration5.release.verify_outputs` Verify release packaging outputs
  - kind: `validation` gate_class: `release` automation: `partial`
  - depends_on: none
  - inputs: none
  - outputs: reports/release/release_manifest_v1.json
  - tags: phase_completion_gate
  - risks: R4

### iteration5/review-and-replan
- Title: Review and Replan
- Goal: Synthesize iteration evidence, approve closeout, and generate the final handoff package.
- Lifecycle: `planned`
- Depends on: iteration5/release-packaging
- Source window: `none`
- Required artifacts: director/reviews/iteration_5_review.json, director/reviews/iteration_5_review.md, director/reviews/iteration_5_patch_proposal.yaml, director/reviews/iteration_5_branch_plan.md, director/reviews/iteration_5_starter_prompt.md, director/reviews/iteration_5_approval.json
- Tags: review, closeout

#### Tasks
- `iteration5.review.generate_review` Generate iteration review
  - kind: `analysis` gate_class: `ops` automation: `partial`
  - depends_on: iteration5.release.verify_outputs
  - inputs: docs/iteration_log.md
  - outputs: director/reviews/iteration_5_review.json, director/reviews/iteration_5_review.md, director/reviews/iteration_5_patch_proposal.yaml, director/reviews/iteration_5_branch_plan.md, director/reviews/iteration_5_starter_prompt.md
  - tags: review_generation
  - risks: R4, R7
- `iteration5.review.approve_closeout` Approve iteration closeout
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration5.review.generate_review
  - inputs: director/reviews/iteration_5_review.json
  - outputs: director/reviews/iteration_5_approval.json
  - tags: review_approval
  - risks: R4


## Iteration 6 - Publication-Grade Upgrade and Scope Expansion
Goal: After the preliminary-results cycle, improve model quality, revisit rubric only when diagnostics justify it, and expand toward broader publication-grade source coverage.
Entry criteria: Preliminary stakeholder-facing results have been packaged from the active 2021-2024 window., Publication-grade retraining and release gates remain governed by the canonical methodology hard gates.
Exit criteria: A publication-grade upgrade plan is published for the next wave of model, scope, and robustness improvements.

### iteration6/post-preliminary-publication-grade-upgrade
- Title: Post-Preliminary Publication-Grade Upgrade
- Goal: Diagnose disagreement and model-quality limitations, plan historical expansion, and define the next publication-grade upgrade cycle without tuning toward significance.
- Lifecycle: `deferred`
- Depends on: iteration5/review-and-replan
- Source window: `none`
- Required artifacts: reports/models/publication_upgrade_plan_v1.json
- Tags: deferred_upgrade, publication_scope, methodology_alignment

#### Tasks
- phase-level only in this roadmap version


## Approved Review Appendix
### dbab2a10-313a3a32
- Scope: `iteration 1`
- Accepted changes: none
- Deferred changes: optimizer-proposed_roadmap_patch_8732eb4e-3a3a3230-1, optimizer-proposed_roadmap_patch_8732eb4e-3a3a3230-2, optimizer-proposed_roadmap_patch_9d516339-3a3a3230-1, optimizer-proposed_roadmap_patch_9d516339-3a3a3230-2, optimizer-proposed_roadmap_patch_b2f116c5-3a3a3230-1, optimizer-proposed_roadmap_patch_b2f116c5-3a3a3230-2, optimizer-proposed_roadmap_patch_d3700831-313a6972-1, optimizer-proposed_roadmap_patch_d3700831-313a6972-2, optimizer-proposed_roadmap_patch_e08e31e6-3a3a3230-1, optimizer-proposed_roadmap_patch_e08e31e6-3a3a3230-2, optimizer-proposed_roadmap_patch_fb55837d-3a3a3230-1, optimizer-proposed_roadmap_patch_fb55837d-3a3a3230-2, review-availability-aware-quartering
- Next iteration: `2`
- Entry criteria: Iteration 1 review approved., Iteration 2 kickoff completed on iteration2/integration., Proposal methodology source and stakeholder expectations are both current.
- Stakeholder summary: active_development_scope=2021-2024 public-filing development window; counts_by_priority{non-negotiable=4, preferred=1, publication-critical=7}; counts_by_status{open=12}; desired_horizon=20-year horizon when source availability permits; due_unsatisfied_count=0; publication_target_scope=all publicly traded firms; requirement_statuses=[{'requirement_id': 'validate_methodology_before_scale', 'priority': 'non-negotiable', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/rubric-realignment', 'iteration2/irr-and-adjudication', 'iteration2/label-sufficiency-gate'], 'mapped_statuses': ['blocked_manual', 'waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'true_human_irr_multi_rater', 'priority': 'non-negotiable', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/irr-and-adjudication', 'iteration2/label-sufficiency-gate'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'scale_candidate_pool_to_500_firms', 'priority': 'publication-critical', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/sentence-pool-expansion-2024', 'iteration2/tranche2-labeling', 'iteration2/tranche3-labeling'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'label_set_sufficiency_before_retraining', 'priority': 'publication-critical', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/tranche1-labeling', 'iteration2/tranche2-labeling', 'iteration2/tranche3-labeling', 'iteration2/merge-canonical-labels', 'iteration2/irr-and-adjudication', 'iteration2/provisional-rubric-freeze-and-split-registry', 'iteration2/label-sufficiency-gate'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps', 'waiting_on_deps', 'waiting_on_deps', 'waiting_on_deps', 'waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'ai_total_merge_integrity', 'priority': 'non-negotiable', 'target_iteration': '3', 'status': 'open', 'mapped_phases': ['iteration3/classification-merge-integrity', 'iteration4/panel-assembly-2021-2024'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'job_postings_robustness', 'priority': 'publication-critical', 'target_iteration': '4', 'status': 'open', 'mapped_phases': ['iteration4/job-postings-robustness-integration', 'iteration5/robustness-and-sensitivity'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'lagged_and_industry_robustness', 'priority': 'publication-critical', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/regression-specification', 'iteration5/robustness-and-sensitivity'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'patent_mismatch_washing_proxy', 'priority': 'publication-critical', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/robustness-and-sensitivity'], 'mapped_statuses': ['waiting_on_deps']}, {'requirement_id': 'literature_differentiation', 'priority': 'publication-critical', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/literature-differentiation-and-examples', 'iteration5/release-packaging'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'before_after_examples', 'priority': 'publication-critical', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/literature-differentiation-and-examples', 'iteration5/release-packaging'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'publication_scope_all_public_firms', 'priority': 'preferred', 'target_iteration': '4', 'status': 'open', 'mapped_phases': ['iteration4/historical-window-expansion-readiness', 'iteration5/results-generation'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'results_and_paper_package', 'priority': 'non-negotiable', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/release-packaging'], 'mapped_statuses': ['waiting_on_deps']}]; source_artifact=docs/director/stakeholder_expectations.md
- Methodology summary: active_development_scope=2021-2024 public-filing development window; core_construct=AI-washing is speculative firm AI narrative without later observable AI capability.; counts_by_priority{non-negotiable=3, publication-critical=2}; counts_by_status{open=5}; desired_horizon=2000-2024 when source availability permits; hard_gates=['human_human_irr_only', 'irr_stratified_100_firms_min', 'by_class_kappa_report_required', 'rubric_freeze_before_final_scale', 'directional_predictive_validity_before_publication_scale']; named_measures=[{'measure_id': 'AI_Focus', 'formula': 'log(1 + AI sentences)'}, {'measure_id': 'log_1_plus_A', 'formula': 'log(1 + A)'}, {'measure_id': 'log_1_plus_S', 'formula': 'log(1 + S)'}, {'measure_id': 'SpecShare', 'formula': 'S / (A + S)'}, {'measure_id': 'CredAI', 'formula': 'z(A) - z(S)'}, {'measure_id': 'A_S', 'formula': 'log(1 + A / (1 + S))'}]; publication_target_scope=all publicly traded firms; requirement_statuses=[{'requirement_id': 'proposal_rubric_realignment_before_scale', 'priority': 'non-negotiable', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/rubric-realignment', 'iteration2/tranche1-labeling'], 'mapped_statuses': ['blocked_manual', 'waiting_on_deps']}, {'requirement_id': 'proposal_style_irr_design', 'priority': 'non-negotiable', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/irr-and-adjudication'], 'mapped_statuses': ['waiting_on_deps']}, {'requirement_id': 'proposal_named_measure_construction', 'priority': 'publication-critical', 'target_iteration': '3', 'status': 'open', 'mapped_phases': ['iteration3/firm-year-measure-construction'], 'mapped_statuses': ['waiting_on_deps']}, {'requirement_id': 'proposal_directional_predictive_validity', 'priority': 'publication-critical', 'target_iteration': '3', 'status': 'open', 'mapped_phases': ['iteration3/development-predictive-validity-gate'], 'mapped_statuses': ['waiting_on_deps']}, {'requirement_id': 'proposal_rubric_freeze', 'priority': 'non-negotiable', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/provisional-rubric-freeze-and-split-registry'], 'mapped_statuses': ['waiting_on_deps']}]; source_artifact=docs/director/proposal_methodology.md
- Unmet stakeholder requirements: none
- Unmet methodology requirements: none
- Rubric calibration status: `future`
- Rubric freeze status: `future`
- Predictive-validity gate status: `future`
- Publication blockers: none
