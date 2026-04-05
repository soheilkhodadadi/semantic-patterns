# Target Repo Layout V1

## Purpose

This note defines the target repository shape for `Lab MVP 1.0`.

It is a target layout, not an instruction to move everything immediately.
The point is to make the intended steady-state structure explicit before migration waves begin.

## Design constraints

The target layout must satisfy five constraints:
- preserve the working AI-washing lane while restructure happens
- allow multiple programs to coexist without naming confusion
- avoid a premature multi-repo split
- avoid pretending the whole repo is already a neutral platform package
- create a path toward future extraction if real reuse pressure appears

## High-level structure

The target repo should behave like a monorepo lab with five top-level concerns:
1. control plane
2. shared code core
3. project adapters
4. data and artifact lanes
5. delivery surfaces

## Target tracked structure

```text
semantic-patterns/
├── src/
│   └── semantic_ai_washing/
│       ├── director/
│       ├── labcore/
│       │   ├── manifests/
│       │   ├── evidence/
│       │   ├── evaluation/
│       │   ├── registry/
│       │   └── delivery/
│       ├── adapters/
│       │   ├── ai_washing/
│       │   ├── eri/
│       │   └── allocationlab/
│       ├── legacy/
│       └── tmp/
├── docs/
│   ├── director/
│   ├── roadmap_v2/
│   ├── lab/
│   │   ├── control_plane/
│   │   ├── schemas/
│   │   ├── migration/
│   │   └── onboarding/
│   └── projects/
│       ├── ai_washing/
│       ├── eri/
│       └── allocationlab/
├── data/
│   ├── metadata/
│   ├── manifests/
│   ├── labels/
│   ├── processed/
│   │   ├── shared/
│   │   └── projects/
│   └── interim/
├── reports/
│   ├── evaluation/
│   ├── labels/
│   ├── registry/
│   └── projects/
│       ├── ai_washing/
│       ├── eri/
│       └── allocationlab/
├── output/
│   ├── doc/
│   │   ├── shared/
│   │   └── projects/
│   ├── figures/
│   │   ├── shared/
│   │   └── projects/
│   └── paper/
├── paper/
├── director/
└── local_private/
    ├── roadmap_v2/
    └── projects/
        ├── eri/
        └── allocationlab/
```

## Why the package namespace stays for now

The current canonical package namespace is still:
- `src/semantic_ai_washing/`

This remains the least risky immediate choice because:
- it already contains the working implementation lane
- packaging already points there
- renaming now would add migration cost before the shared-core boundaries are proven

So the target layout assumes:
- package continuity now
- possible package-neutral extraction later if a true `MVP 2.0` pressure appears

## Shared code target

### `director/`
Keep as the orchestration and control-plane kernel.

This is currently the closest thing to a reusable shared engine seed.

### `labcore/`
This is the intended home for shared workflow code once it becomes genuinely cross-project.

Expected responsibilities:
- manifests and source contracts
- evidence-unit schemas
- benchmark and evaluation helpers
- registries
- delivery/export primitives

Important rule:
- do not populate `labcore/` by moving code there speculatively
- only promote code into `labcore/` after second reuse

### `adapters/`
Each active program gets its own adapter lane.

Near-term adapters:
- `ai_washing/`
- `eri/`
- `allocationlab/`

Each adapter should own:
- domain semantics
- project-specific corpus logic
- project-specific benchmark rules
- downstream analytical outputs

## Documentation target

### `docs/lab/`
This should become the long-lived operational documentation lane for the lab itself.

Proposed subfolders:
- `control_plane/`
- `schemas/`
- `migration/`
- `onboarding/`

### `docs/projects/`
This should become the stable tracked documentation lane for project-specific public-safe notes.

Near-term projects:
- `ai_washing/`
- `eri/`
- `allocationlab/`

### `docs/roadmap_v2/`
This remains the strategy and transition workspace until the lab structure is stable enough to fold the stable docs into `docs/lab/`.

## Data and artifact target

### Shared lanes
These should hold cross-project or potentially cross-project assets:
- `data/metadata/`
- `data/manifests/`
- `data/labels/`
- `reports/evaluation/`
- `reports/registry/`
- `output/doc/shared/`
- `output/figures/shared/`

### Project lanes
These should hold project-specific analytical and delivery outputs:
- `data/processed/projects/<project>/`
- `reports/projects/<project>/`
- `output/doc/projects/<project>/`
- `output/figures/projects/<project>/`

## Delivery target

The lab should eventually have one shared delivery discipline and multiple project-specific surfaces.

Shared delivery primitives belong conceptually in:
- `labcore/delivery/`

Project-facing outputs belong in:
- `output/doc/projects/<project>/`
- `output/figures/projects/<project>/`
- `paper/` for publication-specific manuscript work

## Local-private target

Sensitive materials should never be normalized into the tracked repo.

The expected local-private target is:
- `local_private/roadmap_v2/`
- `local_private/projects/eri/`
- `local_private/projects/allocationlab/`

This allows partner and interview work to coexist with a public-safe repo structure.

## What should remain explicitly legacy

These should remain visibly transitional until removed or replaced:
- flat mirror roots under `src/aggregation`, `src/analysis`, `src/classification`, etc.
- transitional outputs under older `results/` lanes
- scratch and tmp code that is kept only for traceability

The target layout assumes these are being retired, not promoted.

## Migration guidance implied by this layout

The most important idea is:
- create the future lanes first
- move usage and ownership gradually
- remove legacy only after replacement is established

That means:
- structure first
- promotion second
- deletion last

## Bottom line

The target repo should become a monorepo lab with a small shared core, explicit project adapters, and clear artifact lanes.

It should not become a generalized platform shell all at once.
