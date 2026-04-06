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

## Current status

The first hygiene cycle has now been executed as Queue V22 with three outputs:
- `docs/roadmap_v2/history/rounds/migration_round_cf_hygiene_ai_washing_inventory_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_cg_hygiene_repo_visible_scaffolds_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_ch_hygiene_quarantine_readiness_v1.md`

Result:
- the inventory and scaffold review are now explicit
- no code surfaces were quarantined or deleted
- the six legacy/template-looking data utilities are not retire-ready yet

This means the next hygiene-class follow-on, if scheduled, should be a
script-deprecation and registry/inventory cleanup queue rather than an
immediate code-removal queue.

That follow-on has now been executed as Queue V23 with three outputs:
- `docs/roadmap_v2/history/rounds/migration_round_ci_hygiene_script_inventory_deprecation_rules_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_cj_hygiene_script_registry_publish_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_ck_hygiene_script_deprecation_posture_refresh_v1.md`

Result:
- the six historical data utilities are no longer advertised as current
  canonical front-door entrypoints
- they now appear as transitional script-deprecation surfaces
- they still are not retire-ready for deletion or quarantine

This means any later hygiene queue should focus on script-consumer cleanup or
explicit deprecation mapping, not premature code removal.

That script-consumer cleanup follow-on has now been executed as Queue V24 with
three outputs:
- `docs/roadmap_v2/history/rounds/migration_round_cl_hygiene_script_consumer_rules_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_cm_hygiene_script_consumer_publish_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_cn_hygiene_script_consumer_posture_refresh_v1.md`

Result:
- the flat `src/data/*` shims for the six historical utilities are now rendered
  as legacy consumer surfaces rather than generic compatibility fronts
- no shim was deleted
- no code quarantine or retirement patch was opened

This means the next hygiene-class move, if chosen, should be driven by real
remaining leverage rather than by repeating the same script lane again.
