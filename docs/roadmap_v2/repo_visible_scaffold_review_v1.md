# Repo-Visible Scaffold Review V1

## Purpose

This note classifies the repo-visible scaffold surfaces that still affect how
intuitive the workspace feels.

The goal is not to delete anything in this round. The goal is to distinguish
what is now a canonical front door from what is historical, compatibility-only,
or low-signal placeholder material.

## Canonical front-door lanes

These are the lanes that should stay visually prominent:
- `packages/`
- `projects/`
- `shared/`
- `director/`
- `docs/roadmap_v2/`
- `src/semantic_ai_washing/`
- `tests/`

Why:
- they now express the lab shape directly
- they are where current canonical package/member/control-plane work actually
  lives

## Active historical and output lanes to keep visible

These lanes are not the new front door, but they remain real and useful:
- `data/`
- `reports/`
- `output/`
- `paper/`
- `artifacts/`
- `results/`
- `notebooks/`

Why:
- they hold real project artifacts, exploratory assets, or delivery history
- they would become misleading only if we described them as placeholders

Recommended posture:
- keep them visible
- continue clarifying their purpose in README/index docs rather than hiding them

## Compatibility scaffolds to keep but de-emphasize

These lanes are mostly migration-era or pre-lab compatibility structure:
- `src/aggregation/`
- `src/analysis/`
- `src/classification/`
- `src/config/`
- `src/core/`
- `src/data/`
- `src/modeling/`
- `src/patents/`
- `src/scripts/`
- `src/tests/`
- `src/tmp/`

Why:
- they still expose legacy-compatible module paths or historical workflow entry
  points
- they are not template junk, but they are no longer the best mental model for
  the repo

Recommended posture:
- keep them for now
- do not promote new work into them
- treat them as compatibility/deprecation scaffolds for a later retirement pass

## Low-signal placeholders and later review candidates

These surfaces currently carry very little signal on their own:
- `models/`
- `references/`

Current scan result:
- both are present mainly as placeholder lanes with `.gitkeep`
- neither looks like a strong candidate for immediate migration or active use

Recommended posture:
- keep them for now
- revisit only after the broader cleanup/archival picture is clearer

## Issues surfaced during the review

### Duplicate-looking data lane names
- `data/external/`
- `data/externals/`

Why this matters:
- the naming is visually confusing even though both currently contain real files
- this should be handled as a later data-lane cleanup decision, not by
  opportunistic renaming inside an unrelated migration queue

### Local Finder noise exists, but it is not the tracked repo problem

Scan result:
- many `.DS_Store` files exist in the working tree
- they are not tracked by git in the current repo state

Recommended posture:
- treat them as local machine noise, not as the primary V22 cleanup target
- if needed, address them later with ignore/local-hygiene policy rather than
  mixing them into migration logic

## Bottom line

The repo-visible clutter now falls into three real buckets:
1. canonical front doors we want to emphasize
2. active historical/output lanes we should keep readable
3. compatibility or low-signal scaffold lanes we should de-emphasize and later
   retire deliberately

That is a much better position than treating everything outside the canonical
packages/projects lanes as generic mess.
