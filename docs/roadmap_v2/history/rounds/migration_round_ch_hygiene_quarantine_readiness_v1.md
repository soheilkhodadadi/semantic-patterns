# Migration Round CH

## Queue

Queue V22

## Batch

`hygiene.quarantine_readiness_shortlist`

## Purpose

Determine whether any of the six legacy/template candidate data utilities are
already safe to retire or quarantine without creating silent registry,
inventory, or compatibility drift.

## Surfaces reviewed

Targeted `semantic_ai_washing` data utilities:
- `clean_compustat.py`
- `clean_crsp.py`
- `clean_sec.py`
- `download_compustat.py`
- `download_crsp.py`
- `download_sec.py`

Direct-reference surfaces checked:
- `docs/director/script_registry.md`
- `director/snapshots/script_inventory.json`
- `src/data/*.py` flat compatibility shims for the same utilities

## Output

Primary output:
- `docs/roadmap_v2/legacy_quarantine_readiness_v1.md`

## Result

No reviewed surface is retire-ready or quarantine-ready yet.

Why:
- the script registry still exposes them
- the script inventory still advertises them
- flat compatibility shims still depend on them

## Gate

Completed:
- direct-reference scan for all six candidate utilities
- written rationale for every not-ready verdict
- `git diff --check`

## Safety result

This batch stayed inside the hygiene class:
- no authority was changed
- no code was deleted
- no migration was hidden inside cleanup language

## Recommended follow-on

If later cleanup is desired, the next bounded queue should be:
- a script-deprecation hygiene queue

That future queue should update registry/inventory posture first and only then
consider code quarantine or removal.
