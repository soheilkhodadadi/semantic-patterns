# Lab Transition Architecture V1

## Purpose

This note describes how the current `semantic-patterns` repository should evolve from a thesis-linked project into a reusable lab without forcing a premature refactor.

The aim is to preserve what is already strong:
- governed workflow discipline
- evaluation and IRR discipline
- reproducible outputs
- planning and audit discipline through Director

The aim is not to pretend the repo is already a generalized multi-domain product platform.

## Core architectural claim

The current repo already contains a reusable text-measurement core.

That core consists of repeatable workflow layers:
1. corpus indexing and manifests
2. evidence extraction and stable unitization
3. labeling, IRR, and adjudication
4. benchmark and model evaluation
5. aggregation and panel / summary construction
6. reporting, audit, and planning control

These layers are more reusable than the current AI-specific outputs.

## What is core vs what is project-specific

### Reusable lab core

These are the parts to preserve and make legible:
- source indexing and manifest discipline
- canonical sentence / passage tables
- labeling ops and IRR workflow
- benchmark / held-out evaluation harnesses
- aggregation and review artifacts
- reporting and memo-generation discipline
- Director planning / runbook / governance patterns

Representative anchors already in the repo:
- [data_architecture_target.md](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/docs/director/data_architecture_target.md)
- [script_registry.md](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/docs/director/script_registry.md)
- [README.md](/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/README.md)

### AI-washing project layer

These should be treated as the first completed application, not as the lab definition:
- AI keyword families
- actionable / speculative / irrelevant rubric
- patent-specific validation logic
- current firm-year panel and paper-specific tables
- current narrative around AI washing as the focal empirical question

These are valuable, but they are not the portable layer.

## Application layering model

The repo should be understood in four conceptual layers.

### Layer A. Lab core

What it owns:
- ingestion contracts
- evidence-unit contracts
- labeling and IRR contracts
- evaluation contracts
- aggregation contracts
- audit and artifact contracts

This is the most reusable layer and should change slowly.

### Layer B. Domain semantics

What it owns:
- domain taxonomy
- class definitions
- rubric language
- benchmark construction rules
- domain-specific scoring logic

Examples:
- AI-washing disclosure credibility
- environmental disclosure reliability
- later: project-level sustainability / capital-allocation semantics

This layer is reusable in pattern, but not reusable in content.

### Layer C. Application outputs

What it owns:
- paper tables / figures
- proof runs
- memo exports
- benchmark summaries
- analyst or partner briefing packs

Examples:
- FilingLens proof slice
- ERI pilot outputs
- AI-washing paper support materials

### Layer D. Presentation surfaces

What it owns:
- screenshots
- public-safe docs
- portfolio copy
- future dashboards or light interfaces

This is downstream of the lab. It should not define the architecture.

## Where the future projects sit

### FilingLens

Position in architecture:
- mostly Layer C and D on top of the current AI-washing application

Reuse level:
- very high

What is new:
- packaging
- bounded proof run
- presentation surface
- possibly memo/report templates tuned for external viewers

### ERI

Position in architecture:
- new Layer B domain semantics on top of existing Layer A core
- then new Layer C outputs for interview / pilot / toolkit work

Reuse level:
- high in workflow
- moderate in code
- low in direct taxonomy reuse

What is new:
- climate / environmental disclosure taxonomy
- new benchmark design
- new scoring logic
- likely new corpus sources and provenance rules
- issuer-level reliability aggregation

### AllocationLab

Position in architecture:
- partially reuses Layer A
- requires a genuinely new Layer B and a much larger decision layer beyond the current pattern

Reuse level:
- moderate in infrastructure discipline
- low in immediate application code reuse

What is new:
- project entity resolution
- project-level data model
- multi-criteria decision logic
- financing / sensitivity / policy layer
- sector modules

This is why AllocationLab should remain architecture-first in the near term.

## Repo transition guidance

### What to do now

Do:
- document boundaries
- map source-of-truth artifacts
- define application-specific vs reusable components
- add light adapter notes where needed
- keep artifact lanes explicit

### What not to do now

Do not:
- rename the package to a fully generic brand yet
- split the repo into multiple repos
- extract a new engine package before a second application truly forces it
- move large amounts of code only for aesthetic reasons

## Practical repository model for the next stage

### Tracked, public-safe strategy lane
- `docs/roadmap_v2/`

Use for:
- architecture notes
- boundary memos
- public-safe planning
- FilingLens strategy and proof planning

### Local-private strategy lane
- `local_private/roadmap_v2/`

Use for:
- interview prep
- partner-specific notes
- organization-specific Q&A
- non-public architecture details tied to proposals or collaborations

### Core code lane
- `src/semantic_ai_washing/`

Keep as the code source of truth until a second live application creates a real naming or packaging pressure.

### Application evidence lane
- `reports/analysis/`
- `output/doc/`
- `output/figures/`

Use for:
- paper support
- proof runs
- benchmark summaries
- delivery artifacts

## Split triggers

A repo split or engine extraction should happen only if at least one of these becomes true:
- ERI has a live bounded build and starts duplicating workflow code
- FilingLens becomes an active maintained proof surface with its own release cycle
- AllocationLab leaves the architecture stage and begins real implementation
- package naming meaningfully blocks communication or collaborator onboarding

Until then, documentation and adapters are cheaper and safer than extraction.

## Recommended transition sequence

### Stage 1. Clarify
Outputs:
- engine boundary memo
- source-of-truth map
- artifact policy
- this architecture note

### Stage 2. Surface
Outputs:
- FilingLens thin proof
- one clean public-safe demonstration artifact

### Stage 3. Reuse
Outputs:
- ERI interview kit
- ERI pilot framing
- first small transfer-proof artifact

### Stage 4. Preserve ambition without overbuilding
Outputs:
- AllocationLab architecture memo
- synthetic case
- gap matrix

### Stage 5. Package deliberately
Outputs:
- portfolio-facing summaries
- partner-ready briefing material
- outreach assets derived from real proofs

## Bottom line

The correct move is not to turn the repo into a generalized platform overnight.

The correct move is to make the existing workflow legible as a lab core, use FilingLens as the first proof surface, use ERI as the first real new application, and hold AllocationLab as an ambitious but disciplined architecture track until the lab has crossed its first reuse boundary.
