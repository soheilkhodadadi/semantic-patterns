# Packages

This lane is for shared infrastructure packages that are small, stable, and genuinely reusable across
multiple projects.

Near-term intended packages:
- `packages/labcore/`
- `packages/director/`
- later `packages/labdelivery/` only if delivery reuse becomes real

Rules:
- keep shared packages thin
- do not move project semantics here prematurely
- only promote logic upward when reuse is durable and the contract is stable

A package in this lane should eventually satisfy the workspace-member contract in:
- `docs/lab/schemas/workspace_member_contract_v1.md`

Current seed plans:
- `packages/labcore/pyproject_seed_plan_v1.md`
- `packages/director/pyproject_seed_plan_v1.md`

Current package-shell anchor:
- `docs/roadmap_v2/migration_round_d_package_shells_v1.md`
