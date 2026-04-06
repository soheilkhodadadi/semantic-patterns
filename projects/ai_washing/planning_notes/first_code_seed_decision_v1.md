# AI-Washing First Code Seed Decision V1

## Decision

The first true member-owned code seed for `ai_washing` should be the
`labeling/common.py` utility slice, not the higher-level analysis or manuscript
builders.

## Recommended first seed contents

Candidate first seed:
- `src/semantic_ai_washing/labeling/common.py`

Possible immediate companions only if needed in the same round:
- `src/semantic_ai_washing/labeling/__init__.py`

## Why this is the right first seed

This slice is the best first project-owned code move because it is:
- clearly project-specific
- widely reused inside the AI-washing stack
- not a shared cross-project infrastructure concern
- stable enough to justify package-shaped ownership later

It also keeps the first member-owned code seed focused on domain semantics
rather than on manuscript outputs or orchestration plumbing.

## Why other slices should wait

Do not start with:
- `analysis/` delivery builders
- `paper/` assets
- `director`-dependent orchestration code
- panel/regression pipelines with broad data-lane assumptions

Those are all important, but they are not the safest first member-owned code
seed.

## Important caution

This is a decision note, not a go-ahead to move the code immediately.

`labeling/common.py` is reused broadly enough that a real move should happen
only after:
- the authority map is narrowed further
- the member package plan is explicit
- the affected callers are enumerated and grouped

## Acceptance target for a future move

Promote this code-seed candidate into an actual migration round only when:
- all import dependents are mapped
- test coverage for the slice is bundled explicitly
- the member-local package lane is ready to host code, not just shell docs

## Bottom line

`labeling/common.py` is the right first true AI-washing code-seed candidate,
but it should be migrated as its own controlled round rather than folded into a
larger project move.
