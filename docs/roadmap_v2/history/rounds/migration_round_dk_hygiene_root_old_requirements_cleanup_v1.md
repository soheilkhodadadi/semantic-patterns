# Migration Round DK

## Queue

Queue V32

## Batch

`hygiene.root_old_requirements_cleanup`

## Purpose

Retire the single tracked root-level cleanup candidate identified by Queue V31.

## Expected surfaces

- `old_requirements.txt`

## Gate

Required gate:
- direct-reference scan for `old_requirements.txt`
- `git diff --check`

## Outcome

Completed:
- removed `old_requirements.txt` from the repo root
- kept the cleanup strictly limited to the reviewed retire candidate

Validation:
- no non-documentation repo references to `old_requirements.txt` remain
- `git diff --check` passed
