# Migration Round CQ

## Queue

Queue V25

## Batch

`semantic_director.utility_boundary_posture_refresh`

## Purpose

Close Queue V25 with an explicit note about what the queue cleaned up and which
remaining root compatibility imports are still intentionally deferred.

## Outcome

Completed cleanly.

Queue V25 ends with:
- direct-equivalent runtime helpers moved to `semantic_labcore.runtime`
- direct-equivalent responses transport moved to
  `semantic_labcore.openai_responses`
- direct-equivalent schema imports moved to `semantic_director.schemas`

Remaining intentional deferrals:
- `semantic_ai_washing.director.core.security` in `semantic_director.cli`
- `semantic_ai_washing.director.core.utils.run_command` in
  `semantic_director.gates`

## Gate

Required gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`
