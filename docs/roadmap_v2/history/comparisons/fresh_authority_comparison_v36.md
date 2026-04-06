# Fresh Authority Comparison V36

## Purpose

Choose the next bounded late-stage queue after Queue V32.

## Candidates

### Option A
- `hygiene.final_repo_visible_clutter_polish`

### Option B
- `hygiene.roadmap_history_archive_export_prep`

## Comparison

### Final repo-visible clutter/polish

Pros:
- keeps attention on first-contact clarity
- could tighten a few remaining repo-visible placeholders or posture notes

Cons:
- Queue V31 and Queue V32 already reduced the real root-level ambiguity
- the remaining root tracked files now mostly belong
- risks inventing polish work where there is no longer a strong clutter problem

### Roadmap-history archive/export prep

Pros:
- the history layer is now large enough to merit an explicit retention/export
  posture
- can clarify what should stay in-repo, what is archival history, and what a
  later export pass would actually do
- complements Queue V29 instead of repeating it

Cons:
- mostly documentation posture, not visible repo cleanup
- should not turn into another physical re-bucketing pass

## Decision

Choose:
- `hygiene.roadmap_history_archive_export_prep`

## Why

The repo-visible clutter problem is now mostly solved. The more honest next
late-stage move is to define the archive/export posture for the history layer so
we know what “done” means there without forcing another cleanup wave.
