# Legacy Template Hygiene Queue V1

## Purpose

Create a separate bounded cleanup queue for legacy/template debt so we do not
mix deletion, archival, or quarantine work into active authority migrations.

## Operating rule

Hygiene batches must be separate from authority batches.

A hygiene batch may do one or more of these:
- inventory legacy/template surfaces
- mark surfaces as `active`, `dormant`, `archive_candidate`, or `retire_candidate`
- move clearly dead placeholders into a quarantine or legacy lane
- delete only after explicit bounded review and a clean dependency check

A hygiene batch must not:
- change canonical authority for an active workflow
- hide a migration inside a cleanup pass
- delete a surface that still has unresolved direct references

## Proposed queue

### Hygiene Batch 1

Name:
- active-vs-legacy inventory for `ai_washing`

Scope:
- create a bounded inventory of pilot-era and template-era surfaces in
  `src/semantic_ai_washing/labeling/`, `classification/`, `data/`, and selected
  root scaffolds

Output:
- one inventory note with statuses and rationale

### Hygiene Batch 2

Name:
- template/scaffold review for repo-visible placeholders

Scope:
- inspect root/template leftovers and low-value scaffold surfaces that make the
  lab look noisier than it is

Output:
- quarantine or archive recommendations only

### Hygiene Batch 3

Name:
- retire-or-quarantine round for clearly dead pilot surfaces

Scope:
- only surfaces already marked `archive_candidate` or `retire_candidate`
- only after direct-reference checks are clean

Output:
- one bounded cleanup patch with explicit before/after mapping

## Safety gate

Every hygiene batch should pass:
- direct-reference scan for targeted files
- `git diff --check`
- targeted Ruff/`py_compile` only when code files move
- a short written rationale for every archive/delete decision

## Recommendation

Do not start this queue until the next active authority opener is selected and
moving cleanly.

That keeps momentum in the migration lane while still making cleanup a real,
tracked deliverable.
