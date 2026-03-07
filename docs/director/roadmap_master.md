<!-- generated_file: true -->
<!-- source_model: /Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/model/roadmap_model.yaml -->
<!-- source_sha256: 4aadd088017126c5d37221f0ecc2049a136497cd463d9f75e6b002dece872e75 -->
<!-- rendered_at: 2026-03-07T21:09:40.588858+00:00 -->

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
  - mapped phases: iteration1/rubric-and-api-bootstrap, iteration2/irr-and-adjudication, iteration2/label-sufficiency-gate
  - mapped gates: assistive_api_bootstrap_passed, human_human_irr_gt_0_7, label_sufficiency_before_retraining
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
  - mapped phases: iteration2/sentence-pool-expansion-2024, iteration2/dataset-expansion-2024
  - mapped gates: candidate_pool_500_firms, candidate_pool_clean_sentences_gte_1000
- `label_set_sufficiency_before_retraining` priority=`publication-critical` stakeholder=`Kuntara`
  - summary: Reach a publication-grade adjudicated label set before retraining, not just a small pilot.
  - target iteration: `2`
  - source refs: email thread 2025-08-27, email thread 2025-09-08
  - mapped phases: iteration2/dataset-expansion-2024, iteration2/irr-and-adjudication, iteration2/label-sufficiency-gate
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

## Policies
- `heldout_frozen` `dataset_freeze` enforcement=`hard` value=`True`
- `human_human_irr_only` `methodology` enforcement=`hard` value=`True`
- `no_downstream_outcome_peeking` `methodology` enforcement=`hard` value=`True`
- `openai_assistive_only` `model_governance` enforcement=`hard` value=`assistive_only`
- `no_significance_optimization` `analysis_governance` enforcement=`hard` value=`True`
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
  - depends_on: none
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


## Iteration 2 - Scaled Label Expansion, Human IRR, and Modeling Readiness
Goal: Expand the 2024 development window to stakeholder scale, build a publication-grade adjudicated label set, validate the rubric with true human-human IRR, and gate retraining on explicit sufficiency criteria.
Entry criteria: Iteration 1 review approved., Iteration 2 kickoff completed on iteration2/integration., Iteration 2 expansion uses the external DataWork filing corpus, not legacy in-repo sentence exports.
Exit criteria: Sentence-pool expansion reaches 500 firms and at least 1,000 clean AI sentences in the 2024 candidate pool., At least 500 adjudicated labels with at least 80 labels per class are available before retraining., Human-human IRR exceeds 0.7 on a blinded 100+ sentence subset., Split registry is frozen with zero held-out leakage and the modeling readiness report is published., Iteration 2 review approved.

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

### iteration2/sentence-pool-expansion-2024
- Title: Sentence Pool Expansion 2024
- Goal: Expand beyond the 240-row bootstrap batch to a 500-firm, 1-2k clean AI sentence candidate pool using the external 2024 filing window.
- Lifecycle: `planned`
- Depends on: iteration2/kickoff-and-preflight
- Source window: `active_2021_2024`
- Required artifacts: data/manifests/filings/expansion_2024_500_firms_v1.csv, data/processed/sentences/year=2024/expanded_ai_sentences.parquet, reports/labels/sentence_pool_expansion_2024_summary.json
- Tags: sentence_pool, scale, stakeholder_alignment

#### Tasks
- `iteration2.pool.expand_candidate_pool` Expand candidate pool to stakeholder scale
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: none
  - inputs: data/metadata/available_filings_index.csv, data/processed/sentences/year=2024/ai_sentences.parquet
  - outputs: data/manifests/filings/expansion_2024_500_firms_v1.csv, data/processed/sentences/year=2024/expanded_ai_sentences.parquet, reports/labels/sentence_pool_expansion_2024_summary.json
  - tags: sentence_pool, scale
  - risks: R2, R5
- `iteration2.pool.verify_candidate_pool_targets` Verify sentence-pool targets
  - kind: `validation` gate_class: `data` automation: `partial`
  - depends_on: iteration2.pool.expand_candidate_pool
  - inputs: reports/labels/sentence_pool_expansion_2024_summary.json
  - outputs: none
  - tags: sentence_pool_gate
  - risks: R2

### iteration2/dataset-expansion-2024
- Title: Dataset Expansion 2024
- Goal: Produce the expanded human-labeled dataset from the scaled 2024 sentence pool while keeping API use assistive only.
- Lifecycle: `planned`
- Depends on: iteration2/sentence-pool-expansion-2024
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/labels_master.parquet, data/labels/v1/labels_master_review.csv, reports/labels/label_expansion_summary.json
- Tags: label_expansion, assistive_api

#### Tasks
- `iteration2.labels.expand_dataset` Expand canonical labels
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: none
  - inputs: reports/labels/sentence_pool_expansion_2024_summary.json, data/processed/sentences/year=2024/expanded_ai_sentences.parquet, data/manifests/filings/expansion_2024_500_firms_v1.csv
  - outputs: data/labels/v1/labels_master.parquet, data/labels/v1/labels_master_review.csv, reports/labels/label_expansion_summary.json
  - tags: human_labeling
  - risks: R1, R2, R3

### iteration2/irr-and-adjudication
- Title: IRR and Adjudication
- Goal: Run true human-human IRR on a blinded 100+ sentence subset, adjudicate disagreements, and record rubric refinements.
- Lifecycle: `planned`
- Depends on: iteration2/dataset-expansion-2024
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
- `iteration2.irr.prepare_and_collect` Prepare and collect blinded IRR labels
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: iteration2.shared.audit_sentence_integrity
  - inputs: data/labels/v1/labels_master.parquet
  - outputs: data/labels/v1/irr_subset.parquet, reports/labels/irr_report.json, data/labels/v1/adjudication.parquet
  - tags: human_irr
  - risks: R1, R3

### iteration2/split-registry-freeze
- Title: Split Registry Freeze
- Goal: Freeze train and validation sentence assignments after adjudication while keeping held-out separate and leakage-safe.
- Lifecycle: `planned`
- Depends on: iteration2/irr-and-adjudication
- Source window: `active_2021_2024`
- Required artifacts: data/metadata/splits/split_registry_v1.csv, data/metadata/splits/split_registry_v1.json
- Tags: split_registry, leakage_control

#### Tasks
- `iteration2.splits.freeze_registry` Freeze split registry
  - kind: `build` gate_class: `data` automation: `partial`
  - depends_on: none
  - inputs: data/labels/v1/adjudication.parquet
  - outputs: data/metadata/splits/split_registry_v1.csv, data/metadata/splits/split_registry_v1.json
  - tags: split_registry
  - risks: R3, R6

### iteration2/label-sufficiency-gate
- Title: Label Sufficiency Gate
- Goal: Publish and verify the modeling readiness report before centroid retraining begins.
- Lifecycle: `planned`
- Depends on: iteration2/split-registry-freeze
- Source window: `active_2021_2024`
- Required artifacts: reports/models/modeling_readiness_gate.json
- Tags: modeling_gate, stakeholder_alignment

#### Tasks
- `iteration2.labels.publish_modeling_readiness_report` Publish modeling readiness report
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: none
  - inputs: data/labels/v1/labels_master.parquet, reports/labels/irr_report.json, data/metadata/splits/split_registry_v1.csv
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
  - depends_on: none
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


## Iteration 3 - Retraining, Evaluation, and Active-Window Classification
Goal: Retrain on the expanded adjudicated label set, benchmark whether fine-tuning is warranted, evaluate on held-out, and classify the active development window with explicit merge-integrity QA.
Entry criteria: Iteration 2 review approved., Iteration 3 kickoff completed on iteration3/integration., Label sufficiency gate passed with at least 500 adjudicated labels, at least 80 labels per class, and human-human IRR > 0.7.
Exit criteria: Retraining, held-out evaluation, active-window classification, and ai_total merge-integrity QA are complete., Held-out evaluation remains at or above the 0.80 project baseline before publication-scale rollout., Iteration 3 review approved.

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
- phase-level only in this roadmap version

### iteration3/review-and-replan
- Title: Review and Replan
- Goal: Synthesize iteration evidence, approve closeout, and prepare the next iteration handoff.
- Lifecycle: `planned`
- Depends on: iteration3/classification-merge-integrity
- Source window: `none`
- Required artifacts: director/reviews/iteration_3_review.json, director/reviews/iteration_3_review.md, director/reviews/iteration_3_patch_proposal.yaml, director/reviews/iteration_3_branch_plan.md, director/reviews/iteration_3_starter_prompt.md, director/reviews/iteration_3_approval.json
- Tags: review, closeout

#### Tasks
- `iteration3.review.generate_review` Generate iteration review
  - kind: `analysis` gate_class: `ops` automation: `partial`
  - depends_on: none
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
- phase-level only in this roadmap version

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
  - depends_on: none
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
- phase-level only in this roadmap version

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
  - depends_on: none
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


## Approved Review Appendix
### 4aadd088-313a3a32
- Scope: `iteration 1`
- Accepted changes: none
- Deferred changes: optimizer-proposed_roadmap_patch_8732eb4e-3a3a3230-1, optimizer-proposed_roadmap_patch_8732eb4e-3a3a3230-2, optimizer-proposed_roadmap_patch_9d516339-3a3a3230-1, optimizer-proposed_roadmap_patch_9d516339-3a3a3230-2, optimizer-proposed_roadmap_patch_b2f116c5-3a3a3230-1, optimizer-proposed_roadmap_patch_b2f116c5-3a3a3230-2, optimizer-proposed_roadmap_patch_d3700831-313a6972-1, optimizer-proposed_roadmap_patch_d3700831-313a6972-2, optimizer-proposed_roadmap_patch_e08e31e6-3a3a3230-1, optimizer-proposed_roadmap_patch_e08e31e6-3a3a3230-2, optimizer-proposed_roadmap_patch_fb55837d-3a3a3230-1, optimizer-proposed_roadmap_patch_fb55837d-3a3a3230-2, review-availability-aware-quartering
- Next iteration: `2`
- Entry criteria: Iteration 1 review approved., Iteration 2 kickoff completed on iteration2/integration., Iteration 2 expansion uses the external DataWork filing corpus, not legacy in-repo sentence exports.
- Stakeholder summary: active_development_scope=2021-2024 public-filing development window; counts_by_priority{non-negotiable=4, preferred=1, publication-critical=7}; counts_by_status{in_progress=1, open=11}; desired_horizon=20-year horizon when source availability permits; due_unsatisfied_count=0; publication_target_scope=all publicly traded firms; requirement_statuses=[{'requirement_id': 'validate_methodology_before_scale', 'priority': 'non-negotiable', 'target_iteration': '2', 'status': 'in_progress', 'mapped_phases': ['iteration1/rubric-and-api-bootstrap', 'iteration2/irr-and-adjudication', 'iteration2/label-sufficiency-gate'], 'mapped_statuses': ['satisfied', 'waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'true_human_irr_multi_rater', 'priority': 'non-negotiable', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/irr-and-adjudication', 'iteration2/label-sufficiency-gate'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'scale_candidate_pool_to_500_firms', 'priority': 'publication-critical', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/sentence-pool-expansion-2024', 'iteration2/dataset-expansion-2024'], 'mapped_statuses': ['blocked_manual', 'waiting_on_deps']}, {'requirement_id': 'label_set_sufficiency_before_retraining', 'priority': 'publication-critical', 'target_iteration': '2', 'status': 'open', 'mapped_phases': ['iteration2/dataset-expansion-2024', 'iteration2/irr-and-adjudication', 'iteration2/label-sufficiency-gate'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'ai_total_merge_integrity', 'priority': 'non-negotiable', 'target_iteration': '3', 'status': 'open', 'mapped_phases': ['iteration3/classification-merge-integrity', 'iteration4/panel-assembly-2021-2024'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'job_postings_robustness', 'priority': 'publication-critical', 'target_iteration': '4', 'status': 'open', 'mapped_phases': ['iteration4/job-postings-robustness-integration', 'iteration5/robustness-and-sensitivity'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'lagged_and_industry_robustness', 'priority': 'publication-critical', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/regression-specification', 'iteration5/robustness-and-sensitivity'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'patent_mismatch_washing_proxy', 'priority': 'publication-critical', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/robustness-and-sensitivity'], 'mapped_statuses': ['waiting_on_deps']}, {'requirement_id': 'literature_differentiation', 'priority': 'publication-critical', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/literature-differentiation-and-examples', 'iteration5/release-packaging'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'before_after_examples', 'priority': 'publication-critical', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/literature-differentiation-and-examples', 'iteration5/release-packaging'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'publication_scope_all_public_firms', 'priority': 'preferred', 'target_iteration': '4', 'status': 'open', 'mapped_phases': ['iteration4/historical-window-expansion-readiness', 'iteration5/results-generation'], 'mapped_statuses': ['waiting_on_deps', 'waiting_on_deps']}, {'requirement_id': 'results_and_paper_package', 'priority': 'non-negotiable', 'target_iteration': '5', 'status': 'open', 'mapped_phases': ['iteration5/release-packaging'], 'mapped_statuses': ['waiting_on_deps']}]; source_artifact=docs/director/stakeholder_expectations.md
- Unmet stakeholder requirements: none
- Publication blockers: none
