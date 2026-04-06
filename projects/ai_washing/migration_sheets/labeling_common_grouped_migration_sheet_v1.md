# AI-Washing Labeling Common Grouped Migration Sheet V1

## Purpose

This sheet turns the `labeling/common.py` impact map into an execution-ready,
grouped migration order.

It still does not authorize a code move by itself. It defines the safest order
for a future bounded move once the member-local import path is chosen.

Current transitional member-local import path:
- `ai_washing_member.labeling.common`

## Current source slice

Current source:
- `src/semantic_ai_washing/labeling/common.py`

Current helper surface:
- label vocabulary and normalization
  - `ALLOWED_LABELS`
  - `ensure_allowed_label`
  - `normalize_sentence`
  - `parse_uncertain_flag`
- identity helpers
  - `compute_sentence_id`
  - `compute_sample_id`
  - `row_sha256`
- token and length helpers
  - `token_count`
  - `length_bin_from_tokens`
  - `safe_int`
- table I/O helpers
  - `load_table`
  - `write_excel`

## Recommended migration order

### Group 1: labeling core and tests

Why first:
- highest domain ownership
- strongest existing tests
- no shared-lab ambiguity

Direct callers:
- `src/semantic_ai_washing/labeling/__init__.py`
- `adjudicate_irr_labels.py`
- `build_irr_boundary_benchmark.py`
- `build_labeling_batch.py`
- `build_labeling_sample.py`
- `compute_irr_metrics.py`
- `dedupe_labeled_sentences.py`
- `diagnose_irr_disagreements.py`
- `freeze_heldout_v2.py`
- `freeze_split_registry.py`
- `merge_labeling_batches.py`
- `prepare_irr_subset.py`
- `publish_preliminary_results_readiness.py`
- `publish_rubric_freeze.py`
- `qa_labeled_dataset.py`
- `sample_heldout_v2_candidates.py`

Primary regression bundle:
- `tests/test_labeling_phase1.py`
- `tests/test_labeling_batch.py`
- `tests/test_irr_phase2.py`
- `tests/test_split_freeze_publishers.py`
- `tests/test_heldout_v2_workflow.py`
- `tests/test_load_table_fallback.py`

### Group 2: classification callers

Why second:
- reuses the same helper surface heavily
- still project-local, but slightly farther from the labeling source of truth

Direct callers:
- `benchmark_utils.py`
- `benchmark_preliminary_models.py`
- `classify_active_window_preliminary.py`
- `classify_active_window_preliminary_restartable.py`
- `model_runtime.py`
- `preliminary_pipeline.py`
- `train_binary_relevance_then_as.py`
- `train_logreg_preliminary.py`
- `train_preliminary_centroids.py`

Primary regression bundle:
- `tests/test_preliminary_pipeline.py`
- `tests/test_preliminary_benchmarking.py`
- `tests/test_preliminary_classification_restartable.py`
- `tests/test_preliminary_phase3.py`

### Group 3: aggregation, analysis, and data callers

Why third:
- narrower call surface
- more downstream than labeling/classification
- good place to catch table I/O or fingerprint regressions after the earlier groups are stable

Direct callers:
- `src/semantic_ai_washing/aggregation/build_preliminary_narrative_measures.py`
- `src/semantic_ai_washing/aggregation/merge_ai_with_patents.py`
- `src/semantic_ai_washing/analysis/audit_preliminary_panel_inputs.py`
- `src/semantic_ai_washing/data/materialize_active_window_sentences.py`

Primary regression bundle:
- `tests/test_preliminary_phase3.py`
- `tests/test_preliminary_benchmarking.py`
- `tests/test_load_table_fallback.py`

### Group 4: director-adjacent validation

Why last:
- still AI-washing-owned logic
- but it touches the control-plane lane, so it should move only after the project-local groups are stable

Direct caller:
- `src/semantic_ai_washing/director/tasks/validation_assets.py`

Primary regression bundle:
- `tests/test_director_validation_assets.py`

## Entry criteria for the future move

Do not start Group 1 until:
- the future member-local import path is chosen explicitly
- package-local tests exist for the extracted replacement surface
- a compatibility strategy is chosen for legacy imports
- the first member-owned code lane is ready to host real Python files

## Exit criteria for each group

A group is done only when:
- the grouped callers import from the chosen member-local path
- the primary regression bundle passes
- the legacy compatibility path still works if a shim is part of the round
- no helper cluster is split across two authoritative locations

## Decision

This grouped sheet still looks clean.

The move remains substantial, but the groups are coherent enough that it does
not block a small next `director` extraction slice in parallel.

Current status:
- the authoritative implementation has now moved into the member shell through
  `docs/roadmap_v2/history/rounds/migration_round_i_ai_washing_group1_code_seed_v1.md`
- Group 1 direct callers have now migrated through
  `docs/roadmap_v2/history/rounds/migration_round_j_ai_washing_group1_callers_v1.md`
- Group 2 classification callers have now migrated through
  `docs/roadmap_v2/history/rounds/migration_round_k_ai_washing_group2_callers_v1.md`
- Group 3 aggregation, analysis, and data callers have now migrated through
  `docs/roadmap_v2/history/rounds/migration_round_l_ai_washing_group3_callers_v1.md`
- Group 4 director-adjacent validation has now migrated through
  `docs/roadmap_v2/history/rounds/migration_round_m_ai_washing_group4_validation_v1.md`
- the full grouped migration family is now complete
- the remaining direct root test callers have now migrated through
  `docs/roadmap_v2/history/rounds/migration_round_q_ai_washing_labeling_common_test_tail_v1.md`
