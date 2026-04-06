# Migration Round CT

## Queue

Queue V26

## Batch

`semantic_director.wrapper_normalization_posture_refresh`

## Purpose

Close Queue V26 with an explicit note that the remaining `director` package
pressure is no longer boundary normalization but late-stage polish or hygiene.

## Outcome

Completed cleanly.

Queue V26 ends with:
- `semantic_director.security` owning the director-facing security contract
- `semantic_director.runtime` owning the director-facing command-timeout
  contract
- no remaining root `director` compatibility imports inside
  `packages/director/src/semantic_director/`

## Gate

Required gate:
- posture docs updated
- queue/checkpoint docs updated
- `git diff --check`
