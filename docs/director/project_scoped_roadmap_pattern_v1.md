# Project-Scoped Roadmap Pattern V1

## Purpose

This note defines how `director` should operate now that the repo is moving
beyond a single active AI-washing restructure lane and into a real multi-project
lab.

The goal is simple:
- keep the shared control-plane discipline that worked well
- prevent one giant roadmap from becoming a confusing catch-all for every
  project
- keep project progress, stakeholder expectations, and sensitive context
  separated by project lane

## Core decision

Do not use one global machine-readable roadmap as the live execution surface for
multiple projects.

Instead:
- keep shared `director` policies, playbooks, and review norms centralized
- keep project strategy, stakeholder expectations, and execution roadmaps
  project-scoped

## Why this is needed

The current `director/model/roadmap_model.yaml` was useful because it encoded a
single large AI-washing program with:
- one main stakeholder lane
- one methodology source
- one active execution horizon

That design helped the repo move quickly during restructure and preliminary
results work.

It is no longer the right live control surface for the next lab phase because:
- it is already large
- it is heavily AI-washing-specific
- ERI and AllocationLab have different stakeholders, evidence bases, and risk
  profiles
- a shared roadmap file would create cross-project drift and confusing context

## Recommended control-plane split

### Shared `director` layer

Keep centralized:
- playbook library
- review workflow
- branching policy
- security/runtime/tooling policies
- script inventory and repo-visible governance

These belong to `director` because they are lab-wide operational discipline, not
project semantics.

### Project-scoped planning layer

Each project should own its own planning stack.

Minimum project-scoped planning artifacts:
- stakeholder expectations
- methodology or design basis
- roadmap or execution plan
- project-local review/checkpoint notes when execution becomes real

Preferred home:
- `projects/<project>/docs/`

Optional later machine-readable home, only when warranted:
- `director/model/projects/<project>/`

## Activation levels

### Level 0. Placeholder member

Use when a project is only a future lane.

Expected artifacts:
- `README.md`
- public-safe project-doc note or adapter framing note

### Level 1. Pilot charter

Use when a project is being activated but is not yet a full execution program.

Expected artifacts:
- one-page pilot charter
- pilot scope
- sample/data plan
- intended first output

This is the right level for ERI and AllocationLab now.

### Level 2. Execution roadmap

Use when a project has:
- active work
- real blockers/gates
- multi-step sequencing pressure
- stakeholder-backed objectives

Expected artifacts:
- stakeholder expectations note
- methodology/design note
- roadmap document

Optional:
- lightweight machine-readable model if the project will be actively driven by
  `director`

This is the right level for AI-washing now.

### Level 3. Full machine-readable control

Use only when a project has enough ongoing execution pressure that a
machine-readable roadmap materially reduces confusion.

Do not promote a project to this level just because the mechanism already
exists.

## AI-washing decision

### Current status

AI-washing is no longer in restructure mode.
It is entering a publication-upgrade mode.

### Recommended planning posture

- keep the current `director/model/roadmap_model.yaml` as the canonical archive
  of the preliminary and restructure era
- stop treating that file as the default live roadmap for every next move
- create a project-scoped publication-upgrade roadmap under
  `projects/ai_washing/docs/`
- patch or extend the shared `director` sources only where they remain truly
  canonical for AI-washing

### When to create a new machine-readable AI-washing model

Create a lighter successor only if:
- the publication-upgrade work becomes the main execution lane
- sequencing and review pressure justify it
- the team wants `director` to actively drive that next phase

If created, it should be a new scoped artifact, not another append-only growth
of the existing 6700-line model.

## ERI and AllocationLab decision

Do not force them into full roadmap-model complexity yet.

Recommended posture:
- create pilot charters first
- keep their next-step planning small and project-local
- only introduce machine-readable roadmaps after a real pilot execution lane
  appears

## Privacy and separation rules

Each project should keep:
- its own stakeholder expectations
- its own methodology/design basis
- its own execution roadmap

Shared `director` should keep:
- lab-wide operational policies
- playbooks
- shared governance rules

Private or partner-sensitive details should stay in the corresponding
`local_private/projects/<project>/` lane whenever that lane becomes active.

## Immediate recommendation

Use this pattern for the next phase:

1. AI-washing:
   - create a publication-upgrade roadmap
   - keep it project-scoped
2. ERI:
   - create a pilot charter
3. AllocationLab:
   - create a pilot charter

Do not open another general restructure queue.

## Bottom line

The lab now needs shared discipline and project-local planning at the same
time.

The right solution is not one bigger roadmap.
It is one shared `director` operating system plus separate project-scoped
planning tracks.
