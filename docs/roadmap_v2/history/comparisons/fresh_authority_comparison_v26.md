# Fresh Authority Comparison V26

## Purpose

Choose Queue V23 after Queue V22 completed cleanly.

## Candidates compared

1. `semantic_director.utility_followon_bundle`
2. `hygiene.script_deprecation_followon`

## Candidate A: `semantic_director.utility_followon_bundle`

Representative surfaces:
- `semantic_ai_washing.director.core.utils`
- `semantic_ai_washing.director.core.security`
- `semantic_ai_washing.director.core.openai_responses`

Why it is attractive:
- these are visible remaining root imports from the package lane
- a narrow follow-on could make the `director` package look even more complete

Risk shape:
- medium
- the remaining pressure is shallow and mostly intentional
- all three surfaces are already shared-helper compatibility layers backed by
  `labcore`
- forcing another `director` utility queue now would risk creating motion
  without much practical leverage

## Candidate B: `hygiene.script_deprecation_followon`

Representative surfaces:
- `semantic_ai_washing.data.clean_compustat`
- `semantic_ai_washing.data.clean_crsp`
- `semantic_ai_washing.data.clean_sec`
- `semantic_ai_washing.data.download_compustat`
- `semantic_ai_washing.data.download_crsp`
- `semantic_ai_washing.data.download_sec`

Why it is attractive:
- Queue V22 proved these are the highest-signal remaining cleanup candidates
- the script registry and script inventory still advertise them as canonical
  current entrypoints
- this is the next honest late-stage clarity move before any quarantine or
  deletion discussion

Risk shape:
- low to medium
- generated-output changes are involved, so the source-of-truth rule must be
  updated first
- still bounded because the queue does not delete code or change canonical
  runtime authority

## Decision

Chosen Queue V23 opener:
- `hygiene.script_deprecation_followon`

## Why this wins now

Queue V22 already showed the real late-stage pressure:
- active migration pressure is low
- script-deprecation posture is still muddy

So the honest next move is to downgrade those six historical data utilities in
the generated registry/inventory layer before any future retirement queue is
considered.
