# Migration Round J: AI-Washing Group 1 Callers V1

## Scope

This round applies the fast-safe migration protocol to the full Group 1
labeling caller family.

Authority already in place:
- `projects/ai_washing/src/ai_washing_member/labeling/common.py`

This round migrates direct Group 1 callers to import from:
- `ai_washing_member.labeling.common`

## Included caller family

Migrated files:
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

## Compatibility posture

Root compatibility remains in place at:
- `src/semantic_ai_washing/labeling/common.py`

This means:
- Group 1 callers now use the member-local path directly
- external or legacy imports can still resolve through the root shim

## Validation gate

Focused gate for this batch:
- `make doctor`
- targeted Ruff format/check
- targeted `py_compile`
- `projects/ai_washing/tests/test_labeling_common_member.py`
- `tests/test_labeling_phase1.py`
- `tests/test_labeling_batch.py`
- `tests/test_load_table_fallback.py`
- `tests/test_irr_phase2.py`
- `tests/test_split_freeze_publishers.py`
- `tests/test_heldout_v2_workflow.py`

## Outcome

This is the first full grouped caller-family migration inside the `ai_washing`
member lane.
