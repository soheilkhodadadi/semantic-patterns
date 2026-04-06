# Fresh Authority Comparison V13

## Purpose

Choose the Queue V10 opener after Queue V9 completed cleanly.

## Candidates compared

1. `ai_washing_member.labeling.initialize_review_sheet`
2. `semantic_director.planner`

## Candidate A: `ai_washing_member.labeling.initialize_review_sheet`

Why it is attractive:
- it is the cleanest remaining current-stage labeling workflow surface
- direct caller pressure is concentrated in `benchmark_prompt_variants` and
  `tests/test_iteration2_parallel.py`
- it naturally opens `merge_labeling_batches` as an adjacent follow-on round
- roadmap-model command strings can stay on the compatibility path for now

Risk shape:
- low
- one workflow family
- no Atlas-adjacent boundary pressure

## Candidate B: `semantic_director.planner`

Why it is attractive:
- high-leverage downstream `director` boundary
- now sits behind canonical `cost`, `llm`, `roadmap_model`, and `task_graph`
- meaningful package move with real CLI/test leverage

Risk shape:
- medium
- broader dependency surface than the labeling workflow opener
- stronger as the closing rotation after two `ai_washing` workflow moves

## Decision

Chosen Queue V10 opener:
- `ai_washing_member.labeling.initialize_review_sheet`

## Why this wins now

It is the cleaner opener and lets Queue V10 form a coherent shape:

1. `initialize_review_sheet`
2. `merge_labeling_batches`
3. `semantic_director.planner`

That keeps the first two rounds inside one active `ai_washing` workflow family,
then closes with one larger but now well-supported `director` planning move.
