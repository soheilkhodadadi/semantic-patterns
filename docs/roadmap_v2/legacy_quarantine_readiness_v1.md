# Legacy Quarantine Readiness V1

## Purpose

This note answers a narrow hygiene question after the Queue V22 inventory and
scaffold review:

Which legacy/template-looking `ai_washing` data utilities are actually ready
for retire/quarantine right now?

## Surfaces reviewed

Root `semantic_ai_washing` utilities:
- `src/semantic_ai_washing/data/clean_compustat.py`
- `src/semantic_ai_washing/data/clean_crsp.py`
- `src/semantic_ai_washing/data/clean_sec.py`
- `src/semantic_ai_washing/data/download_compustat.py`
- `src/semantic_ai_washing/data/download_crsp.py`
- `src/semantic_ai_washing/data/download_sec.py`

Matching flat compatibility shims:
- `src/data/clean_compustat.py`
- `src/data/clean_crsp.py`
- `src/data/clean_sec.py`
- `src/data/download_compustat.py`
- `src/data/download_crsp.py`
- `src/data/download_sec.py`

## Direct-reference scan result

The reviewed surfaces are still referenced in:
- `docs/director/script_registry.md`
- `director/snapshots/script_inventory.json`
- the flat compatibility shim lane under `src/data/`

This means they are not just old-looking files sitting in isolation. They are
still part of the documented script surface and compatibility mapping.

## Readiness verdict by class

### Retire-ready now
- none

### Quarantine-ready now
- none

### Not ready yet
- `clean_compustat`
- `clean_crsp`
- `clean_sec`
- `download_compustat`
- `download_crsp`
- `download_sec`

## Why none are ready yet

The blockers are structural, not sentimental:
- the director script registry still names these modules as valid entry points
- the director script inventory still records them as canonical or compatibility
  targets
- flat shims still point at the `semantic_ai_washing.data.*` implementations
- there is no completed deprecation mapping yet that says what replaces them or
  whether they should be archived rather than removed

## What must happen before a real quarantine patch

1. Decide whether each utility is:
   - genuinely obsolete
   - archive-only historical material
   - or still a dormant-but-relevant utility
2. Update `docs/director/script_registry.md` to reflect that decision.
3. Update `director/snapshots/script_inventory.json` so the inventory no longer
   advertises the utilities as normal active targets.
4. Only then plan a bounded code patch for:
   - quarantine
   - archive
   - or shim removal

## Recommended posture after Queue V22

- do not delete or quarantine these utilities yet
- treat them as hygiene-follow-on candidates, not active migration targets
- schedule any future retirement work as a dedicated script-deprecation hygiene
  queue, not as part of a migration queue

## Bottom line

Queue V22 clarified something important:

The six legacy/template-looking data utilities are real cleanup candidates, but
they are not cleanly detachable yet. The right next step is not code removal.
The right next step is explicit script-deprecation planning.
