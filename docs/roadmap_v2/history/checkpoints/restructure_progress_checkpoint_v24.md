# Restructure Progress Checkpoint V24

## Purpose

This checkpoint closes Queue V31 and records what the repo-root clutter review
changed in practice.

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Latest Queue V31 commits:
- `f570fe3` `docs: review repo root clutter posture`
- `8a2790a` `docs: refresh repo root clutter posture`

## What Queue V31 proved

Queue V31 completed cleanly with:
1. `hygiene.repo_root_clutter_review`
2. `hygiene.repo_root_clutter_posture_refresh`
3. `hygiene.repo_root_clutter_checkpoint`

This matters because Queue V31 turned the remaining repo-root clutter question
into an explicit, bounded decision instead of a vague late-stage worry.

## Direction check

### Are we still moving in the right direction?

Yes.

Why:
- the queue stayed bounded to repo-root review and posture
- it identified a real retire candidate instead of inventing work
- it did not reopen any settled migration lane

### Are we still on a safe path?

Yes.

Why:
- Queue V31 changed no code behavior
- the review is scan-backed
- the only proposed follow-on cleanup is narrow and explicit
- Atlas/private spillover stayed clean

## What Queue V31 changes in practice

Queue V31 leaves the repo with a clearer late-stage cleanup posture:
- most tracked root files are still justified as repo-contract surfaces
- local-only ignored files are explicitly not treated as tracked cleanup wins
- `old_requirements.txt` is now the only strong tracked retire candidate

## Current ballpark

Current estimated progress:
- `labcore`: ~95-100%
- `director`: ~98-100%
- `ai_washing` active member migration: ~85-93%
- full clean final lab structure: ~93-98%

## Recommended posture after Queue V31

Recommended posture:
- keep Protocol V2
- open V32 only as a narrow root-cleanup queue
- do not mix in local ignored-file cleanup or packaging changes
- if V32 stays bounded to `old_requirements.txt`, it is justified and safe

## Bottom line

Queue V31 was worth doing.

It did not move code authority, but it converted a fuzzy repo-root cleanliness
question into one small, evidence-backed follow-on cleanup.
