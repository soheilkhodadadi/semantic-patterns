# Migration Round DE

## Queue

Queue V30

## Batch

`hygiene.repo_root_frontdoor_refresh`

## Purpose

Refresh the repo root front door so it points clearly to the current lab
navigation model while preserving the active AI-washing delivery context.

## Expected surfaces

- `README.md`

## Gate

Required gate:
- front-door narrative updated
- direct links point to current canonical navigation docs
- `git diff --check`

## Outcome

Completed:
- added a `Start Here` section to the repo root `README.md`
- aligned the root restructure pointers with the current `roadmap_v2` front
  door and latest checkpoint
- preserved the active AI-washing delivery context while making the current lab
  navigation easier to follow

Validation:
- repo root front-door links now point to current navigation docs
- `git diff --check` passed
