<!-- generated_file: true -->
<!-- source_model: /Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/model/roadmap_model.yaml -->
<!-- source_sha256: d3700831d2786fcb36dac789a95a75529209cf4dc8e56eee74afa538818a1765 -->
<!-- rendered_at: 2026-03-05T22:53:21.772841+00:00 -->

# Roadmap Master

This document is generated from the canonical roadmap YAML model.

Optimization proposals may recommend resequencing tasks or phases beyond the canonical order shown here.

## Iteration 1 - Expand labels and retrain centroids
Goal: Improve classifier reliability and scientific readiness while preserving truthful gate semantics.

### iteration1/diagnostics-nlp
- Title: Diagnostics Baseline and Failure Taxonomy
- Goal: Establish a factual baseline and artifact fingerprints before changing the science pipeline.
- Depends on: none
- Required artifacts: reports/iteration1/phase0/baseline_eval_metrics.json, reports/iteration1/phase0/baseline_eval_confusion_matrix.csv, reports/iteration1/phase0/run_metadata.json, reports/iteration1/phase0/baseline_report.md

#### Tasks
- `iteration1.diagnostics.pipeline_map_confirmation` Pipeline map confirmation
  - kind: `diagnostic`
  - depends_on: none
  - inputs: none
  - outputs: docs/pipeline_map.md
  - risks: R5, R6
- `iteration1.diagnostics.heldout_baseline_evaluation` Held-out baseline evaluation
  - kind: `validation`
  - depends_on: iteration1.diagnostics.pipeline_map_confirmation
  - inputs: data/validation/held_out_sentences.csv
  - outputs: reports/iteration1/phase0/baseline_eval_metrics.json, reports/iteration1/phase0/baseline_eval_confusion_matrix.csv
  - risks: R5, R6
- `iteration1.diagnostics.tiny_batch_sanity_classification` Tiny batch sanity classification
  - kind: `build`
  - depends_on: iteration1.diagnostics.heldout_baseline_evaluation
  - inputs: none
  - outputs: reports/iteration1/phase0/baseline_batch_distribution.csv, reports/iteration1/phase0/run_metadata.json
  - risks: R5, R6
- `iteration1.diagnostics.batch_coverage_check` Batch coverage check
  - kind: `validation`
  - depends_on: iteration1.diagnostics.tiny_batch_sanity_classification
  - inputs: none
  - outputs: reports/iteration1/phase0/run_metadata.json
  - risks: R5
- `iteration1.diagnostics.failure_taxonomy_generation` Failure taxonomy generation
  - kind: `analysis`
  - depends_on: iteration1.diagnostics.heldout_baseline_evaluation
  - inputs: none
  - outputs: reports/iteration1/phase0/baseline_failure_taxonomy.csv
  - risks: R6
- `iteration1.diagnostics.baseline_report_assembly` Baseline report assembly
  - kind: `reporting`
  - depends_on: iteration1.diagnostics.batch_coverage_check, iteration1.diagnostics.failure_taxonomy_generation
  - inputs: none
  - outputs: reports/iteration1/phase0/baseline_report.md
  - risks: R5, R6

### iteration1/label-expansion
- Title: Label Expansion and Dataset Hygiene
- Goal: Expand the labeled dataset with leakage-safe sampling and QA, without falsely passing the strict canonical science gate.
- Depends on: iteration1/diagnostics-nlp
- Required artifacts: reports/iteration1/phase1/sampling_summary.json, reports/iteration1/phase1/dedupe_report.json, reports/iteration1/phase1/qa_report.json, reports/iteration1/phase1/leakage_overlap_report.csv

#### Tasks
- `iteration1.label_expansion.audit_source_labeled_dataset` Audit source labeled dataset
  - kind: `diagnostic`
  - depends_on: none
  - inputs: none
  - outputs: data/validation/hand_labeled_ai_sentences_labeled_cleaned_revised.csv
  - risks: R1, R3
- `iteration1.label_expansion.audit_candidate_sentence_integrity` Audit candidate sentence integrity
  - kind: `diagnostic`
  - depends_on: iteration1.label_expansion.audit_source_labeled_dataset
  - inputs: none
  - outputs: data/labels/iteration1/recovery/expanded_labeled_sentences_preqa.csv
  - risks: R1, R5
- `iteration1.label_expansion.build_labeling_sample` Build labeling sample
  - kind: `build`
  - depends_on: iteration1.label_expansion.audit_source_labeled_dataset
  - inputs: none
  - outputs: reports/iteration1/phase1/sampling_summary.json, data/labels/iteration1/labeling_sheet_for_manual.csv
  - risks: R2, R3, R5
- `iteration1.label_expansion.manual_labeling_handoff` Manual labeling handoff
  - kind: `manual`
  - depends_on: iteration1.label_expansion.build_labeling_sample
  - inputs: none
  - outputs: data/labels/iteration1/labeling_sheet_completed.csv
  - risks: R1, R2
- `iteration1.label_expansion.dedupe_merge` Dedupe merge
  - kind: `build`
  - depends_on: iteration1.label_expansion.manual_labeling_handoff
  - inputs: none
  - outputs: reports/iteration1/phase1/dedupe_report.json, data/labels/iteration1/expanded_labeled_sentences_preqa.csv
  - risks: R1, R3, R6
- `iteration1.label_expansion.dataset_qa` Dataset QA
  - kind: `validation`
  - depends_on: iteration1.label_expansion.dedupe_merge
  - inputs: none
  - outputs: reports/iteration1/phase1/qa_report.json, reports/iteration1/phase1/leakage_overlap_report.csv
  - risks: R2, R3, R6
- `iteration1.label_expansion.metadata_report_generation` Metadata and report generation
  - kind: `reporting`
  - depends_on: iteration1.label_expansion.dataset_qa
  - inputs: none
  - outputs: reports/iteration1/phase1/qa_report.json
  - risks: R6

### iteration1/irr-validation
- Title: IRR Gate
- Goal: Establish IRR infrastructure and prevent IRR execution from proceeding when source sentence quality is inadequate.
- Depends on: iteration1/label-expansion
- Required artifacts: data/labels/iteration1/irr/irr_subset_master.csv, data/labels/iteration1/irr/irr_subset_rater2_blinded.csv, reports/iteration1/phase2_irr/irr_kappa_report.json, reports/iteration1/phase2_irr/irr_status.json, data/labels/iteration1/irr/irr_adjudication_sheet.csv, reports/iteration1/phase2_irr/adjudication_status.json

#### Tasks
- `iteration1.shared.audit_sentence_integrity` Audit IRR source sentence integrity
  - kind: `diagnostic`
  - depends_on: none
  - inputs: none
  - outputs: data/labels/iteration1/recovery/expanded_labeled_sentences_preqa.csv
  - risks: R1, R5
- `iteration1.irr.prepare_subset` Prepare IRR subset
  - kind: `build`
  - depends_on: iteration1.shared.audit_sentence_integrity
  - inputs: none
  - outputs: data/labels/iteration1/irr/irr_subset_master.csv, data/labels/iteration1/irr/irr_subset_rater2_blinded.csv
  - risks: R1, R2
- `iteration1.irr.manual_rater2_handoff` Manual second-rater handoff
  - kind: `manual`
  - depends_on: iteration1.irr.prepare_subset
  - inputs: none
  - outputs: data/labels/iteration1/irr/irr_subset_rater2_completed.csv
  - risks: R1
- `iteration1.irr.compute_infrastructure_metrics` Compute infrastructure IRR metrics
  - kind: `validation`
  - depends_on: iteration1.irr.prepare_subset
  - inputs: none
  - outputs: reports/iteration1/phase2_irr/irr_kappa_report.json, reports/iteration1/phase2_irr/irr_status.json
  - risks: R1
- `iteration1.irr.build_adjudication_sheet` Build adjudication sheet
  - kind: `build`
  - depends_on: iteration1.irr.prepare_subset
  - inputs: none
  - outputs: data/labels/iteration1/irr/irr_adjudication_sheet.csv, reports/iteration1/phase2_irr/adjudication_status.json
  - risks: R1
- `iteration1.irr.strict_kappa_recheck` Strict kappa recheck
  - kind: `validation`
  - depends_on: iteration1.irr.manual_rater2_handoff
  - inputs: none
  - outputs: reports/iteration1/phase2_irr/irr_status_strict.json
  - risks: R1
- `iteration1.irr.final_adjudicated_merge` Final adjudicated merge
  - kind: `build`
  - depends_on: iteration1.irr.build_adjudication_sheet, iteration1.irr.manual_rater2_handoff
  - inputs: none
  - outputs: data/labels/iteration1/irr/final_labeled_sentences_recovery_adjudicated.csv
  - risks: R1, R6

### iteration1/centroid-retraining
- Title: Centroid Retraining
- Goal: Retrain centroid artifacts only after adjudicated labels and strict IRR gates are available.
- Depends on: iteration1/irr-validation
- Required artifacts: data/validation/hand_labeled_ai_sentences_with_embeddings_mpnet.csv, data/validation/centroids_mpnet.json

#### Tasks
- `iteration1.centroid.freeze_adjudicated_dataset` Freeze adjudicated training dataset
  - kind: `validation`
  - depends_on: iteration1.irr.strict_kappa_recheck, iteration1.irr.final_adjudicated_merge
  - inputs: none
  - outputs: data/labels/iteration1/irr/final_labeled_sentences_recovery_adjudicated.csv
  - risks: R1, R3
- `iteration1.centroid.embed_labeled_sentences` Embed labeled sentences
  - kind: `build`
  - depends_on: iteration1.centroid.freeze_adjudicated_dataset
  - inputs: none
  - outputs: data/validation/hand_labeled_ai_sentences_with_embeddings_mpnet.csv
  - risks: R4
- `iteration1.centroid.compute_centroids` Compute centroids
  - kind: `build`
  - depends_on: iteration1.centroid.embed_labeled_sentences
  - inputs: none
  - outputs: data/validation/centroids_mpnet.json
  - risks: R4, R6
- `iteration1.centroid.fingerprint_centroid_metadata` Fingerprint centroid metadata
  - kind: `reporting`
  - depends_on: iteration1.centroid.compute_centroids
  - inputs: none
  - outputs: reports/iteration1/phase3/centroid_manifest.json
  - risks: R4, R6
- `iteration1.centroid.verify_label_mapping` Verify label mapping compatibility
  - kind: `validation`
  - depends_on: iteration1.centroid.compute_centroids
  - inputs: none
  - outputs: reports/iteration1/phase3/centroid_manifest.json
  - risks: R6

### iteration1/classifier-calibration
- Title: Classifier Calibration
- Goal: Tune and validate classification behavior without leakage.
- Depends on: iteration1/centroid-retraining
- Required artifacts: reports/iteration1/phase4/calibration_report.json

#### Tasks
- `iteration1.calibration.verify_split_registry` Verify split registry
  - kind: `validation`
  - depends_on: iteration1.centroid.verify_label_mapping
  - inputs: none
  - outputs: data/validation/split_registry.json
  - risks: R3, R6
- `iteration1.calibration.threshold_pass` Run threshold pass on validation only
  - kind: `analysis`
  - depends_on: iteration1.calibration.verify_split_registry
  - inputs: none
  - outputs: reports/iteration1/phase4/calibration_report.json
  - risks: R3, R4
- `iteration1.calibration.heldout_evaluation` Run held-out evaluation
  - kind: `validation`
  - depends_on: iteration1.calibration.threshold_pass
  - inputs: none
  - outputs: reports/iteration1/phase4/heldout_eval_metrics.json
  - risks: R4, R6
- `iteration1.calibration.calibration_decision_report` Generate calibration decision report
  - kind: `decision`
  - depends_on: iteration1.calibration.heldout_evaluation
  - inputs: none
  - outputs: reports/iteration1/phase4/calibration_report.json
  - risks: R3, R4

### iteration1/batch-classification-2021-2024
- Title: Batch Classification 2021-2024
- Goal: Run bounded multi-year classification with explicit coverage and aggregation checks.
- Depends on: iteration1/classifier-calibration
- Required artifacts: reports/iteration1/phase5/batch_summary_report.md

#### Tasks
- `iteration1.batch.build_year_file_manifest` Build year/file manifest
  - kind: `diagnostic`
  - depends_on: iteration1.calibration.calibration_decision_report
  - inputs: none
  - outputs: reports/iteration1/phase5/batch_manifest.json
  - risks: R5
- `iteration1.batch.classify_yearly_batches` Classify yearly batches
  - kind: `build`
  - depends_on: iteration1.batch.build_year_file_manifest
  - inputs: none
  - outputs: reports/iteration1/phase5/batch_summary_report.md
  - risks: R5, R6
- `iteration1.batch.coverage_and_skip_audit` Coverage and skip audit
  - kind: `validation`
  - depends_on: iteration1.batch.classify_yearly_batches
  - inputs: none
  - outputs: reports/iteration1/phase5/batch_coverage_report.json
  - risks: R5
- `iteration1.batch.aggregation_sanity_check` Aggregation sanity check
  - kind: `validation`
  - depends_on: iteration1.batch.classify_yearly_batches
  - inputs: none
  - outputs: data/final/ai_frequencies_by_firm_year.csv
  - risks: R5, R6
- `iteration1.batch.batch_summary_report` Batch summary report
  - kind: `reporting`
  - depends_on: iteration1.batch.coverage_and_skip_audit, iteration1.batch.aggregation_sanity_check
  - inputs: none
  - outputs: reports/iteration1/phase5/batch_summary_report.md
  - risks: R5, R6

## Iteration 2 - Scale classification and integrate cross-walks
Goal: Produce full-sample sentence and firm-year outputs for downstream analysis.

### iteration2/full-sample-extraction
- Title: Full-sample extraction
- Goal: Scale extraction with validated lineage.
- Depends on: none
- Required artifacts: none

#### Tasks

### iteration2/full-sample-classification
- Title: Full-sample classification
- Goal: Scale classification with coverage controls.
- Depends on: iteration2/full-sample-extraction
- Required artifacts: none

#### Tasks

### iteration2/aggregation-and-crosswalks
- Title: Aggregation and cross-walk integration
- Goal: Build firm-year measures with validated joins.
- Depends on: iteration2/full-sample-classification
- Required artifacts: none

#### Tasks

## Iteration 3 - Evaluate OpenAI API strategy
Goal: Decide whether LLM classification should augment the deterministic baseline.

### iteration3/llm-pilot
- Title: LLM pilot
- Goal: Run a bounded comparison pilot.
- Depends on: none
- Required artifacts: none

#### Tasks

### iteration3/hybrid-routing-decision
- Title: Hybrid routing decision
- Goal: Record the production decision on LLM usage.
- Depends on: iteration3/llm-pilot
- Required artifacts: none

#### Tasks

## Iteration 4 - Final integration and production hardening
Goal: Deliver a reproducible, auditable, publication-ready package.

### iteration4/panel-assembly
- Title: Panel assembly
- Goal: Build the final panel and downstream datasets.
- Depends on: none
- Required artifacts: none

#### Tasks

### iteration4/robustness-analysis
- Title: Robustness analysis
- Goal: Run final empirical and robustness workflows.
- Depends on: iteration4/panel-assembly
- Required artifacts: none

#### Tasks

### iteration4/release-packaging
- Title: Release packaging
- Goal: Package the repo, outputs, and audit trail for release.
- Depends on: iteration4/robustness-analysis
- Required artifacts: none

#### Tasks
