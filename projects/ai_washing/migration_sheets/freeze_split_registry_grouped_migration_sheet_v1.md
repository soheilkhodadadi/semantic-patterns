# AI-Washing Freeze Split Registry Grouped Migration Sheet V1

## Authority

Canonical authority:
- `ai_washing_member.labeling.freeze_split_registry`

Legacy compatibility path:
- `semantic_ai_washing.labeling.freeze_split_registry`

## Direct caller groups

### Group 1

Direct validation caller pressure:
- `tests/test_split_freeze_publishers.py`
- `projects/ai_washing/tests/test_freeze_split_registry_member.py`

### Deferred compatibility edge

Leave unchanged for now:
- `tests/test_director_roadmap_model.py`

Reason:
- the roadmap-model assertion is about the stable project command surface, not
  about the internal member authority path
