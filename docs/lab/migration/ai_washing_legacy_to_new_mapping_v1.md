# AI-Washing Legacy To New Mapping V1

## Purpose

This note maps the active AI-washing artifact lanes to the new lab structure created in Wave 2.

It is a replacement map, not a bulk-move instruction.
Its job is to let us keep the live AI-washing lane stable while making future destinations explicit.

## Current rule

- current authoritative AI-washing artifacts stay authoritative where they already live
- new AI-washing artifacts should prefer the new project lanes when there is no stronger legacy convention already in place
- no legacy lane should be deleted until its replacement path is validated in practice

## Mapping sheet

| Artifact family | Current authoritative path(s) | Future destination lane | Scope | Current action | Move trigger |
| --- | --- | --- | --- | --- | --- |
| Project design and empirical spec notes | `reports/analysis/` including `table_*_spec_v1.md`, `figure_*_spec_v1.md`, `main_text_appendix_boundary_v1.md`, `patent_mismatch_construct_v1.md` | `docs/projects/ai_washing/` for durable orientation docs, `reports/projects/ai_washing/` for iterative project reporting | project | keep current paths authoritative | promote once a note stops changing as working analysis and becomes stable project guidance |
| Measurement and technical audit notes | `reports/analysis/pass_c_technical_audit_2026-03-25_v1.md`, `reports/analysis/methodology_metric_role_audit_v1.md`, `reports/analysis/sample_*` | `reports/projects/ai_washing/` | project | keep current paths authoritative | move when we want one curated AI-washing reporting lane rather than mixed analysis notes |
| Held-out evaluation and model benchmark evidence | `reports/evaluation/`, `reports/models/`, selected `reports/labels/` audit files | remain in current shared benchmark/evaluation lanes | shared with AI-washing origin | no move now | only move if a more general lab-wide evaluation registry replaces the existing shared lanes |
| Human-labeling and IRR evidence | `data/labels/`, `reports/labels/` | remain in current lanes for now | benchmark / shared-capable | no move now | move only with an explicit benchmark migration plan, not as part of AI-washing delivery cleanup |
| Authoritative AI-washing processed datasets | `data/processed/aggregates/`, `data/processed/panel/`, `data/processed/patents/` | `data/processed/projects/ai_washing/` for future curated project-scoped datasets | project | keep current paths authoritative | move only after a curated subset and validation map are defined |
| Shared manifest-style source contracts | `data/manifests/` and selected metadata under `data/metadata/` | remain in shared lanes | shared | no move now | promote only when manifest contracts are explicitly normalized for multi-project use |
| Paper-generated markdown tables and snippets | `paper/generated/tables/`, `paper/generated/snippets/` | remain under `paper/generated/` | paper-specific | no move now | keep paper-bound assets in manuscript lanes unless we later split reusable reporting from paper generation |
| Polished delivery tables and figures for review | `output/doc/delivery_tables_v1/`, `output/doc/delivery_figures_v1/`, `output/figures/delivery_figures_v1/` | `output/doc/projects/ai_washing/`, `output/figures/projects/ai_washing/` for future project-scoped outputs | project delivery | keep current paths authoritative | use new lanes for fresh outputs once we deliberately switch the builders |
| Results-writing support docs | `output/doc/results_draft_scaffold_v1.docx`, `output/doc/results_transition_notes_v1.docx`, `output/doc/preliminary_delivery_review_packet_v1.docx` | `output/doc/projects/ai_washing/` | project delivery | keep current paths authoritative | move once we cut a new project-scoped writing-support pass |
| Monthly and supervisor reporting docs | `output/doc/reports/2026-03/`, `output/paper/reports/2026-03/` | `output/doc/projects/ai_washing/` for polished docs and `reports/projects/ai_washing/` for tracked report indexes | project | keep current paths authoritative | move once we normalize monthly reporting into the new lane structure |
| Manuscript source and section files | `paper/sections/`, `paper/source/`, `paper/manuscript.md` and related paper lanes | remain under `paper/` | paper-specific | no move now | do not move into generic lab lanes; manuscript work stays manuscript work |

## Near-term placement rules for AI-washing

### Keep where they are
These remain authoritative in place for now:
- `reports/analysis/`
- `reports/evaluation/`
- `reports/models/`
- `reports/labels/`
- `data/processed/aggregates/`
- `data/processed/panel/`
- `data/processed/patents/`
- `paper/generated/`
- `output/doc/delivery_tables_v1/`
- `output/doc/delivery_figures_v1/`
- `output/figures/delivery_figures_v1/`
- `paper/`

### Use the new destinations first for fresh work when practical
Use these for new materials when there is not already a stronger legacy convention:
- `docs/projects/ai_washing/`
- `reports/projects/ai_washing/`
- `data/processed/projects/ai_washing/`
- `output/doc/projects/ai_washing/`
- `output/figures/projects/ai_washing/`

## Why this map matters

Without an explicit map, later cleanup turns into guesswork and accidental breakage.
This note makes the transition legible before any code or builder moves begin.

## Bottom line

AI-washing remains fully operational in its current lanes.
Wave 3 and later waves should move only curated, justified pieces with this map as the guardrail.
