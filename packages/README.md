# Packages Workspace

## Purpose

This lane is for shared packages that are stable, reusable, and clearly
separated from project-specific semantics.

## Start here

Current package fronts:
- `packages/labcore/README.md`
- `packages/director/README.md`

Current package posture:
- `docs/roadmap_v2/current_state_navigation_v1.md`
- `docs/roadmap_v2/history/checkpoints/restructure_progress_checkpoint_v22.md`

## Current packages

### `labcore`
- low-level shared runtime, security, audit, transport, and registry helpers
- canonical code under `packages/labcore/src/semantic_labcore/`

### `director`
- shared orchestration and control-plane package
- canonical code under `packages/director/src/semantic_director/`

## Rules

- keep shared packages thin
- do not move project semantics here prematurely
- only promote logic upward when reuse is durable and the contract is stable

A package in this lane should eventually satisfy:
- `docs/lab/schemas/workspace_member_contract_v1.md`

## Background references

- `packages/labcore/pyproject_seed_plan_v1.md`
- `packages/director/pyproject_seed_plan_v1.md`
- `docs/roadmap_v2/history/rounds/migration_round_d_package_shells_v1.md`
