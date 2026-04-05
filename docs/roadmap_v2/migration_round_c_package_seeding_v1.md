# Migration Round C Package Seeding V1

## Purpose

This note records the first package/member seeding decisions under the workspace-centric lab model.

Round C is about deciding:
- which units get real local seed plans now
- which units remain staged placeholders
- what package identities and dependency directions the first real seeds should use

## Decision summary

| Unit | Kind | Decision | Distribution name | Import name | Status |
| --- | --- | --- | --- | --- | --- |
| `labcore` | shared package | local package seed plan now | `semantic-labcore` | `semantic_labcore` | seeded plan |
| `director` | shared package | local package seed plan now | `semantic-director` | `semantic_director` | seeded plan |
| `ai_washing` | project member | local member seed plan now | `semantic-ai-washing` | `semantic_ai_washing` | seeded plan |
| `eri` | project member | staged placeholder for now | later | later | planned placeholder |
| `allocationlab` | project member | staged placeholder for now | later | later | planned placeholder |

## Why this split is right now

### Seed locally now
These have enough local substance to justify explicit seeding plans:
- `labcore`
- `director`
- `ai_washing`

### Keep staged for now
These are strategically important but still too early for real member seeds:
- `eri`
- `allocationlab`

That keeps the member model honest and avoids creating empty package shells that pretend maturity before it exists.

## Key naming choice

The most important naming decision is:
- preserve `semantic_ai_washing` as the AI-washing import identity
- give the shared packages their own distinct identities

This reduces migration pain where it matters most while still moving toward a real package-based lab.

## Dependency direction

Intended dependency shape:
- `semantic_labcore` at the bottom
- `semantic_director` above `semantic_labcore`
- `semantic_ai_washing` as a project member that can depend on shared packages where justified
- future `eri` and `allocationlab` members later, once their local boundaries are real

## Outputs created in this round

- `packages/labcore/pyproject_seed_plan_v1.md`
- `packages/director/pyproject_seed_plan_v1.md`
- `projects/ai_washing/member_seed_plan_v1.md`
- `projects/eri/member_seed_decision_v1.md`
- `projects/allocationlab/member_seed_decision_v1.md`

## Bottom line

Round C now has a real package/member seeding stance.
The next migration slices can stop asking "what should this eventually be?" and start asking "what bounded move gets one seeded unit closer to buildable?"
