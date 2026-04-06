# Sample Held-Out V2 Candidates Grouped Migration Sheet V1

## Authority

Canonical member-owned authority:
- `ai_washing_member.labeling.sample_heldout_v2_candidates`

Legacy compatibility shim:
- `semantic_ai_washing.labeling.sample_heldout_v2_candidates`

## Group 1: Direct workflow callers

Files:
- `src/semantic_ai_washing/labeling/sample_heldout_v2_restartable.py`
- `tests/test_heldout_v2_workflow.py`

Gate:
- `projects/ai_washing/tests/test_sample_heldout_v2_candidates_member.py`
- `tests/test_heldout_v2_workflow.py`
- `tests/test_restartable_jobs.py`

Status:
- complete

## Follow-on authority candidate

Natural next move in the same workflow lane:
- `ai_washing_member.labeling.freeze_heldout_v2`
