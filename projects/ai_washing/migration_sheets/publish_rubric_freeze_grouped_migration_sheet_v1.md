# AI-Washing Publish Rubric Freeze Grouped Migration Sheet V1

## Authority

Canonical authority:
- `ai_washing_member.labeling.publish_rubric_freeze`

Legacy compatibility path:
- `semantic_ai_washing.labeling.publish_rubric_freeze`

## Direct caller groups

### Group 1

Direct validation caller pressure:
- `tests/test_split_freeze_publishers.py`
- `projects/ai_washing/tests/test_publish_rubric_freeze_member.py`

### Group 2

Workflow confidence surface:
- `tests/test_irr_phase2.py`

### Deferred compatibility edge

Leave unchanged for now:
- `tests/test_director_roadmap_model.py`

Reason:
- the roadmap-model assertion is about the stable project command surface, not
  the internal member authority path
