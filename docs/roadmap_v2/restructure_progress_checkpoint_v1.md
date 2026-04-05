# Restructure Progress Checkpoint V1

## Purpose

This checkpoint records how far the restructure has actually progressed after
Rounds A through I and identifies where faster execution is now justified.

## Current branch state

Active branch:
- `codex/lab-mvp1/restructure-foundation`

Recent checkpoint commits:
- `27e0cd6` `refactor: complete first labcore extraction wave`
- `92541d7` `refactor: wire workspace imports and plan next seeds`
- `2ef828a` `refactor: extract director schema surface`
- `5cc0be2` `refactor: extract director policies and group labeling move`
- `58d049b` `refactor: seed ai-washing member labeling common`

## What is now materially real

### Shared packages

`packages/labcore` is now materially real with canonical code for:
- runtime
- audit
- security
- OpenAI Responses transport
- registry lanes and adapters

`packages/director` is now materially real with canonical code for:
- schema/export surface
- default policy templates
- roadmap-model loading and query helpers
- roadmap rendering helpers

### Project members

`projects/ai_washing` is no longer just a placeholder.
It now has:
- project-owned docs/report/output shell lanes
- a grouped migration map for the first code seed
- a real first member-owned code slice under `projects/ai_washing/src/`
- a completed full `labeling/common.py` migration family to the member-local path

### Control plane

The restructure now has:
- workspace/member contracts
- manifest/evidence contracts
- package/member acceptance checklist
- extraction protocol
- grouped migration planning notes

## What has worked repeatedly

The following migration pattern has worked cleanly multiple times:
1. choose one bounded authority move
2. copy canonical implementation into the future package/member destination
3. replace the legacy path with a compatibility shim
4. add local tests for the new canonical destination
5. run focused regressions on the legacy caller side
6. run build smoke when a shared package is touched
7. clean leftovers and commit the batch

This is now proven for:
- `labcore`
- `director`
- the first `ai_washing` member-owned code seed
- the first larger-batch `ai_washing` classification support migration
- the second larger-batch `ai_washing` SEC index migration
- the first four-family `ai_washing` sentence-table migration
- a fresh-authority `ai_washing` benchmark-utils seed round under Protocol V2
- a fresh-authority `director` roadmap-model seed round under Protocol V2
- a fresh-authority `director` render seed round under Protocol V2

## Current bottlenecks

The remaining bottlenecks are not conceptual anymore. They are operational:
- import-path coordination across workspace members
- deciding which grouped caller family to move together
- keeping migration notes and authority maps current as the repo changes
- avoiding accidental broad edits outside the intended family
- choosing the next migration family now that the `labeling/common.py` family is complete

## What is now safe to speed up

It is now reasonable to speed up by batching:
- one authority move
- one direct-caller family
- one focused validation bundle
- one doc/update bundle

in the same round.

What is still not safe to batch aggressively:
- unrelated caller families in different domains
- shared-package extraction and project-member extraction in the same write scope
- broad deletions of legacy lanes
- simultaneous changes to import paths and package identity assumptions

## Bottom line

The restructure is past the speculative phase.

We now have enough real package/member moves to use a faster protocol without
losing control, as long as the batch unit stays:
- one bounded authority move
- up to four tightly related families in one lane
- one shared acceptance gate

The current upper bound is still conditional:
- the larger batch must stay inside one existing authority
- the validation/import edge can count as one family
- the gate must already cover the full batch

Recent scan result:
- the remaining already-member-owned `ai_washing` surfaces now have only a
  shallow direct legacy-root tail
- after the classification support tail, the next meaningful acceleration will
  likely require a fresh authority move rather than another established-surface
  cleanup batch
- that fresh authority move has now been taken through
  `docs/roadmap_v2/migration_round_s_ai_washing_benchmark_utils_seed_v1.md`
- the next fresh-authority move has now also been taken through
  `docs/roadmap_v2/migration_round_t_director_roadmap_model_seed_v1.md`
- the next follow-on fresh-authority move has now been taken through
  `docs/roadmap_v2/migration_round_u_director_render_seed_v1.md`
