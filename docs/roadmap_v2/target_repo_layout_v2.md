# Target Repo Layout V2

## Purpose

This note revises the target layout so the repo can support:
- package-style project members
- teammate module intake
- later package or subrepo export

The key revision is that major projects should no longer be treated as just subfolders inside one dominant package tree.

## Revised target

The target is a workspace monorepo with:
- root control plane
- root shared artifact lanes
- shared infrastructure packages
- project workspace members

## Revised tracked structure

```text
semantic-patterns/
├── pyproject.toml                # workspace root
├── uv.lock                       # shared workspace lockfile when appropriate
├── README.md
├── docs/
│   └── lab/
│       ├── control_plane/
│       ├── schemas/
│       ├── migration/
│       └── onboarding/
├── shared/
│   ├── manifests/
│   ├── labels/
│   ├── evaluation/
│   └── registry/
├── packages/
│   ├── labcore/
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   ├── src/
│   │   └── tests/
│   ├── director/
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   ├── src/
│   │   └── tests/
│   └── labdelivery/             # only if reuse proves real
│       ├── pyproject.toml
│       ├── README.md
│       ├── src/
│       └── tests/
├── projects/
│   ├── ai_washing/
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   ├── src/
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── configs/
│   │   ├── reports/
│   │   └── output/
│   ├── eri/
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   ├── src/
│   │   ├── tests/
│   │   ├── docs/
│   │   ├── configs/
│   │   ├── reports/
│   │   └── output/
│   └── allocationlab/
│       ├── pyproject.toml
│       ├── README.md
│       ├── src/
│       ├── tests/
│       ├── docs/
│       ├── configs/
│       ├── reports/
│       └── output/
├── paper/                        # manuscript lane stays distinct
├── director/                     # transitional roadmap/playbook lane
└── local_private/
    └── projects/
        ├── eri/
        └── allocationlab/
```

## What is different from V1

V1 assumed:
- one dominant package root
- root-level project docs and outputs as the main project lanes

V2 assumes:
- project-local docs, tests, configs, reports, and outputs inside each project member
- root-level shared lanes only for truly shared artifacts and control-plane assets
- shared code promoted into `packages/`, not left mixed into one project namespace forever

## Why this is better

### Better for teammate intake

A teammate can hand over a coherent project module that already has:
- `pyproject.toml`
- `src/`
- `tests/`
- `README`

That module can be:
- added as a workspace member
- or initially referenced as a path dependency and later promoted

### Better for later export

If a project member becomes valuable on its own, it can be:
- built and published as a package
- copied into a separate repo with less surgery
- shared with a client or collaborator without dragging the whole monorepo with it

### Better for local reasoning

A contributor can understand one project member without reading the entire lab.

## What should stay shared

Shared at root:
- control-plane docs
- schemas
- registries
- manifests
- labels
- evaluation assets that are genuinely cross-project
- shared infrastructure packages

Not shared by default:
- project-specific docs
- project-specific reports
- project-specific outputs
- project-specific domain logic

## Import and package strategy

Near-term practical rule:
- keep the current package namespace where needed during migration

Revised end-state rule:
- major shared packages and major project members should each have their own package identity
- avoid one giant import namespace for everything if exportability is a real goal

## Migration implication

This revised target means the next roadmap should gradually shift from:
- root-level project folders and one dominant package tree

toward:
- workspace members under `projects/`
- shared packages under `packages/`
- thinner root shared lanes

This is a stronger end-state, but it also means the migration should be staged carefully.

## Bottom line

If the repo must be able to absorb other teams' modules and also give birth to exportable subpackages later, then the target layout should be package-centric and workspace-based.

That is the strongest long-term shape for this lab.
