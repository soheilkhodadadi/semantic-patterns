# Documentation Index

This directory holds the repo’s working documentation for environment setup, pipeline usage, delivery planning, and status tracking.

If you are new to the project, start here:

## Environment and setup

- [environment_setup.md](environment_setup.md)
  - repo-local `.venv`, Apple Silicon notes, WRDS configuration, and common environment fixes

## Current delivery state

- [preliminary_delivery_status_2026-03-20.md](preliminary_delivery_status_2026-03-20.md)
  - authoritative artifacts, current empirical read, and immediate next work
- [preliminary_results_execution_plan.md](preliminary_results_execution_plan.md)
  - current execution plan for the preliminary delivery phase

## Running analysis

- [modular_regression_workflow.md](modular_regression_workflow.md)
  - how to rerun one regression family or a small bundle without rebuilding everything

## Pipeline notes

- [pipeline_map.md](pipeline_map.md)
  - legacy-oriented map of the original extract/classify/aggregate workflow
  - useful for understanding the repo foundation, but not sufficient on its own for the current `2016-2024` delivery lane

## Delivery and storytelling notes

Most delivery-planning documents live under `reports/analysis/`, including:

- sample audits
- table spec cards
- story roadmaps
- monthly reporting workflow notes

Good starting files there include:

- `reports/analysis/preliminary_delivery_story_roadmap_v1.md`
- `reports/analysis/preliminary_delivery_blueprint_v1.md`
- `reports/analysis/sample_construction_audit_v1.md`

## Building docs locally

This repo also supports MkDocs-based static documentation.

Build locally with:

```bash
mkdocs build
```

Serve locally with:

```bash
mkdocs serve
```
