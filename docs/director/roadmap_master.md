<!-- generated_file: true -->
<!-- source_model: /Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/model/roadmap_model.yaml -->
<!-- source_sha256: 8732eb4e1df2c551897bd5583b936c699575c14c2ee8f624732a43a35d62e58f -->
<!-- rendered_at: 2026-03-06T05:05:27.061902+00:00 -->

# Roadmap Master

This document is generated from the canonical roadmap YAML model.

Optimization proposals may recommend resequencing tasks or phases beyond the canonical order shown here.

## Policies
- `heldout_frozen` `dataset_freeze` enforcement=`hard` value=`True`
- `human_human_irr_only` `methodology` enforcement=`hard` value=`True`
- `no_downstream_outcome_peeking` `methodology` enforcement=`hard` value=`True`
- `openai_assistive_only` `model_governance` enforcement=`hard` value=`assistive_only`
- `no_significance_optimization` `analysis_governance` enforcement=`hard` value=`True`
- `split_registry_required_before_retraining` `data_governance` enforcement=`hard` value=`True`
- `sentence_quality_gate_before_labeling` `data_governance` enforcement=`hard` value=`True`
- `sentence_quality_gate_before_irr` `data_governance` enforcement=`hard` value=`True`

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
  - outputs: data/manifests/filings/pilot_2024_10k_v1.csv
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
- phase-level only in this roadmap version

### iteration1/label-ops-bootstrap
- Title: Label Ops Bootstrap
- Goal: Generate the first clean labeling batch from the bounded pilot after sentence-quality gating.
- Lifecycle: `planned`
- Depends on: iteration1/rubric-and-api-bootstrap
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/labeling_batch_v1.parquet, data/labels/v1/labeling_batch_v1.csv
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


## Iteration 2 - Label Expansion, Human IRR, and Frozen Training Set
Goal: Build the first canonical human-labeled dataset, validate the rubric with true IRR, and freeze the split registry.

### iteration2/dataset-expansion-2024
- Title: Dataset Expansion 2024
- Goal: Expand labeled coverage on clean pilot-derived sentences while keeping API use assistive only.
- Lifecycle: `planned`
- Depends on: iteration1/label-ops-bootstrap
- Source window: `active_2021_2024`
- Required artifacts: data/labels/v1/labels_master.parquet, reports/labels/label_expansion_summary.json
- Tags: label_expansion, assistive_api

#### Tasks
- `iteration2.labels.expand_dataset` Expand canonical labels
  - kind: `manual` gate_class: `manual` automation: `manual`
  - depends_on: none
  - inputs: data/labels/v1/labeling_batch_v1.csv
  - outputs: data/labels/v1/labels_master.parquet, reports/labels/label_expansion_summary.json
  - tags: human_labeling
  - risks: R1, R2, R3

### iteration2/irr-and-adjudication
- Title: IRR and Adjudication
- Goal: Run true human-human IRR on a blinded subset and adjudicate disagreements.
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
- Goal: Freeze train and validation sentence assignments after adjudication while keeping held-out separate.
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

### iteration2/modeling-readiness-gate
- Title: Modeling Readiness Gate
- Goal: Gate retraining on class balance, sentence quality, adjudication completion, and split integrity.
- Lifecycle: `planned`
- Depends on: iteration2/split-registry-freeze
- Source window: `active_2021_2024`
- Required artifacts: reports/models/modeling_readiness_gate.json
- Tags: modeling_gate

#### Tasks
- phase-level only in this roadmap version


## Iteration 3 - Retraining, Calibration, and Classification of 2021–2024
Goal: Retrain the local model on adjudicated labels, calibrate on validation only, and classify the current active window.

### iteration3/centroid-retraining
- Title: Centroid Retraining
- Goal: Embed the adjudicated training set, compute centroids, and fingerprint metadata.
- Lifecycle: `planned`
- Depends on: iteration2/modeling-readiness-gate
- Source window: `active_2021_2024`
- Required artifacts: artifacts/models/mpnet_v1/embeddings.parquet, artifacts/models/mpnet_v1/centroids.json, artifacts/models/mpnet_v1/metadata.json
- Tags: retraining

#### Tasks
- phase-level only in this roadmap version

### iteration3/classifier-calibration
- Title: Classifier Calibration
- Goal: Calibrate thresholds on validation only and evaluate on the frozen held-out set.
- Lifecycle: `planned`
- Depends on: iteration3/centroid-retraining
- Source window: `active_2021_2024`
- Required artifacts: reports/evaluation/calibration_v1.json, reports/evaluation/heldout_eval_v1.json
- Tags: calibration, evaluation

#### Tasks
- phase-level only in this roadmap version

### iteration3/active-window-batch-classification
- Title: Active Window Batch Classification
- Goal: Classify the active 2021–2024 source window with coverage and skip auditing.
- Lifecycle: `planned`
- Depends on: iteration3/classifier-calibration
- Source window: `active_2021_2024`
- Required artifacts: data/processed/classifications/year=2021/model=mpnet_v1/classified_sentences.parquet, data/processed/classifications/year=2022/model=mpnet_v1/classified_sentences.parquet, data/processed/classifications/year=2023/model=mpnet_v1/classified_sentences.parquet, data/processed/classifications/year=2024/model=mpnet_v1/classified_sentences.parquet, reports/classification/active_window_coverage_v1.json
- Tags: batch_classification

#### Tasks
- phase-level only in this roadmap version

### iteration3/aggregation-sanity
- Title: Aggregation Sanity
- Goal: Aggregate sentence-level classifications to firm-year outputs and QA the active window snapshot.
- Lifecycle: `planned`
- Depends on: iteration3/active-window-batch-classification
- Source window: `active_2021_2024`
- Required artifacts: data/processed/aggregates/firm_year_ai_metrics_v1.parquet, reports/classification/aggregation_qa_v1.json
- Tags: aggregation

#### Tasks
- phase-level only in this roadmap version


## Iteration 4 - Panel Construction and Conditional Historical Backfill
Goal: Build the active-window panel and cleanly separate that from any deferred historical source expansion.

### iteration4/patents-and-controls-ingestion
- Title: Patents and Controls Ingestion
- Goal: Refresh patents, controls, and crosswalk inputs required for the active-window panel.
- Lifecycle: `planned`
- Depends on: iteration3/aggregation-sanity
- Source window: `active_2021_2024`
- Required artifacts: data/interim/patents/patent_metrics_v1.parquet, data/interim/controls/controls_v1.parquet
- Tags: panel_inputs

#### Tasks
- phase-level only in this roadmap version

### iteration4/panel-assembly-2021-2024
- Title: Panel Assembly 2021-2024
- Goal: Merge active-window AI metrics with patents and controls into the canonical panel.
- Lifecycle: `planned`
- Depends on: iteration4/patents-and-controls-ingestion
- Source window: `active_2021_2024`
- Required artifacts: data/panels/panel_v1.parquet, data/panels/panel_v1.csv, reports/panels/panel_merge_coverage_v1.json
- Tags: panel

#### Tasks
- phase-level only in this roadmap version

### iteration4/panel-qa-and-freeze
- Title: Panel QA and Freeze
- Goal: Validate panel schema, missingness, and transformation rules before freezing panel v1.
- Lifecycle: `planned`
- Depends on: iteration4/panel-assembly-2021-2024
- Source window: `active_2021_2024`
- Required artifacts: reports/panels/panel_v1_qa.json
- Tags: panel_qa

#### Tasks
- phase-level only in this roadmap version

### iteration4/historical-window-expansion-readiness
- Title: Historical Window Expansion Readiness
- Goal: Determine whether pre-2021 source availability permits historical backfill work.
- Lifecycle: `deferred`
- Depends on: iteration4/panel-qa-and-freeze
- Source window: `historical_2000_2020`
- Required artifacts: reports/data/historical_backfill_readiness.json
- Tags: historical_backfill

#### Tasks
- phase-level only in this roadmap version


## Iteration 5 - Analysis Outputs and Research Release Packaging
Goal: Produce analysis outputs and a release package without making statistical significance an optimization target.

### iteration5/regression-specification
- Title: Regression Specification
- Goal: Freeze regression inputs and define baseline and robustness specifications.
- Lifecycle: `planned`
- Depends on: iteration4/panel-qa-and-freeze
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/regression_specification_v1.json
- Tags: analysis

#### Tasks
- phase-level only in this roadmap version

### iteration5/results-generation
- Title: Results Generation
- Goal: Run baseline models and generate tables and figures with provenance.
- Lifecycle: `planned`
- Depends on: iteration5/regression-specification
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/results_manifest_v1.json
- Tags: analysis

#### Tasks
- phase-level only in this roadmap version

### iteration5/robustness-and-sensitivity
- Title: Robustness and Sensitivity
- Goal: Run alternative specifications and summarize directional stability.
- Lifecycle: `planned`
- Depends on: iteration5/results-generation
- Source window: `active_2021_2024`
- Required artifacts: reports/analysis/robustness_summary_v1.json
- Tags: analysis

#### Tasks
- phase-level only in this roadmap version

### iteration5/release-packaging
- Title: Release Packaging
- Goal: Package artifacts, docs, and reproducibility notes for research release.
- Lifecycle: `planned`
- Depends on: iteration5/robustness-and-sensitivity
- Source window: `active_2021_2024`
- Required artifacts: reports/release/release_manifest_v1.json
- Tags: release

#### Tasks
- phase-level only in this roadmap version
