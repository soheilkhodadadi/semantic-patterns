# Group 3 Readiness Checkpoint V1

## Purpose

This checkpoint pauses after the Group 2 classification caller migration and
confirms whether the next chunk should proceed as another fast-safe batch.

## Current state

Completed `ai_washing` member-local authority and caller moves:
- Group 1 code seed into `ai_washing_member.labeling.common`
- Group 1 labeling caller-family migration
- Group 2 classification caller-family migration

Validation state at this checkpoint:
- `make doctor`: passed
- targeted Ruff gate: passed
- targeted compile gate: passed
- focused Group 2 pytest bundle: `9 passed`

## What changed in this checkpoint

Two small baseline blockers were repaired during the Group 2 gate:
- restartable classification warm-up now degrades cleanly when runtime metadata
  is absent in lightweight test scenarios
- active-window sentence materialization now honors the existing max-token
  default when a namespace omits that argument

These were accepted because they were:
- already exposed by the declared Group 2 regression bundle
- small in blast radius
- directly tied to restoring the acceptance gate

## Group 3 shape

Next planned family:
- aggregation, analysis, and data callers still using the legacy labeling common
  path

Expected Group 3 direct callers:
- `src/semantic_ai_washing/aggregation/build_preliminary_narrative_measures.py`
- `src/semantic_ai_washing/aggregation/merge_ai_with_patents.py`
- `src/semantic_ai_washing/analysis/audit_preliminary_panel_inputs.py`
- `src/semantic_ai_washing/data/materialize_active_window_sentences.py`

Expected primary regression bundle:
- `tests/test_preliminary_phase3.py`
- `tests/test_preliminary_benchmarking.py`
- `tests/test_load_table_fallback.py`

## Recommendation

Proceed to Group 3 only as one bounded family under the same protocol:
- one authority already in force
- one caller family
- one focused doc update
- one acceptance gate

Do not mix a new shared-package extraction into the same batch.
