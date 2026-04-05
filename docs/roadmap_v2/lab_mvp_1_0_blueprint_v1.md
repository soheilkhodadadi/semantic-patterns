# Lab MVP 1.0 Blueprint V1

## Purpose

This blueprint defines the minimum viable structure needed for the current repository and workflow to operate as a multi-program lab.

The aim is not to describe the final platform.
The aim is to define the minimum structure that would let:
- AI-washing continue as a publication program
- FilingLens emerge as a proof surface
- ERI start as a real second application
- AllocationLab remain active as an architecture program

## Design goal

Lab MVP 1.0 should make three things possible:
1. parallel work without chaos
2. reuse without premature abstraction
3. delivery without rebuilding outputs from scratch for each project

## The target structure

Lab MVP 1.0 should be understood as five layers.

### Layer 1. Control plane

Purpose:
- define what is allowed, current, and authoritative

Responsibilities:
- source-of-truth maps
- artifact policy
- project registry
- privacy classes
- run metadata
- acceptance gates
- planning and review discipline

Current foundation already exists in:
- Director notes
- script registry
- data architecture notes
- review / reporting workflow

### Layer 2. Shared data and evidence core

Purpose:
- create stable, reusable evidence objects across programs

Responsibilities:
- corpus manifests
- source windows
- canonical text units
- labels and adjudication tables
- benchmark and split registries
- model artifact registry
- shared evaluation outputs

This is the first truly reusable technical core.

### Layer 3. Domain adapters

Purpose:
- let each project define its own semantics while reusing the shared evidence core

Each adapter should own:
- domain corpus rules
- taxonomy / rubric
- benchmark rules
- scoring logic
- domain outputs

Near-term adapters:
- AI-washing adapter
- ERI adapter
- AllocationLab adapter

### Layer 4. Analytics and downstream modules

Purpose:
- convert scores and evidence into domain-relevant analysis

Examples:
- patent timing and market consequences for AI-washing
- reliability aggregation and toolkit outputs for ERI
- project ranking, scenario analysis, and financing sensitivity for AllocationLab

This layer is where the projects will differ most.

### Layer 5. Delivery surfaces

Purpose:
- turn analysis into reusable outputs for different audiences

Surface types:
- paper support assets
- memo exports
- reporting packs
- bounded proof demos
- dashboards or lightweight workbenches later

This layer should be shared in pattern even when outputs differ.

## Minimum viable repo behavior

Lab MVP 1.0 should support the following behavior:

### A. One shared run discipline
Every substantial run should have:
- manifest reference
- model or scoring version
- output path
- QA note
- audience / privacy class

### B. One artifact taxonomy
Every major output should be clearly tagged as one of:
- benchmark artifact
- evaluation artifact
- analysis artifact
- delivery artifact
- public-safe proof artifact
- partner/private artifact

### C. One project registry
The lab should explicitly know which projects are active and what they reuse.

Suggested registry fields:
- project name
- maturity stage
- privacy class
- primary audience
- shared core dependencies
- project-specific adapters
- lead owner

### D. One output discipline
All projects should be able to emit:
- human-readable note or memo
- reviewable table or figure artifacts where relevant
- machine-readable structured outputs where relevant

## MVP 1.0 team model

Assuming a 5-6 person team plus agents, the most plausible structure is:

### Role 1. Lab lead / integration lead
Responsibilities:
- priorities
- project boundaries
- what gets promoted to shared core
- what remains project-specific
- review and acceptance gates

### Role 2. Core platform engineer
Responsibilities:
- manifests
- shared schemas
- registries
- orchestration
- environment contracts
- common utilities

### Role 3. ML / evaluation engineer
Responsibilities:
- labeling ops support
- evaluation harnesses
- benchmark tracking
- confidence and calibration work
- model quality QA

### Role 4. Domain research lead
Responsibilities:
- taxonomy design
- annotation rules
- economic or domain interpretation
- literature alignment

### Role 5. Data and analytics engineer
Responsibilities:
- downstream datasets
- joins and analytical tables
- figures
- structured outputs

### Role 6. Delivery and reporting engineer
Responsibilities:
- memo/report surfaces
- proof packaging
- dashboards or workbench outputs later
- export and formatting systems

A smaller team can combine roles. The key point is the separation of core, domain, analytics, and delivery ownership.

## What external platform precedents suggest, abstractly

Without adopting any private or proprietary specifics, public platform examples reinforce a few good architectural instincts:
- separate presentation from analytics from integration from data/storage
- treat monitoring and QA as first-class, not afterthoughts
- keep security/privacy rules explicit rather than implicit
- let one engine support multiple workflows through adapters and connectors
- tie recommendations or outputs back to auditable evidence and confidence

What we should borrow in principle:
- layered architecture
- explicit operating layers
- validation and observability mindset
- team separation by layer and responsibility

What we should not borrow directly right now:
- heavy enterprise infrastructure for its own sake
- stack complexity before workflow clarity
- production-scale deployment assumptions before the lab proves reuse internally

## What MVP 1.0 should not require

It does not need:
- Kubernetes
- multi-cloud deployment
- complex real-time infrastructure
- a polished SaaS product shell
- a full generalized package extraction

It does need:
- structure
- contracts
- artifact discipline
- reproducible outputs
- clear boundaries

## Suggested project layout concept

Not an immediate refactor, but the conceptual target should be:

- shared lab core
  - control plane
  - manifests
  - evidence units
  - labeling and evaluation
  - artifact registry
- project adapters
  - ai_washing
  - eri
  - allocationlab
- delivery surfaces
  - papers
  - proof demos
  - partner reports
  - public-safe outputs

This can initially live as documentation and conventions before code moves.

## The first acceptance test for Lab MVP 1.0

We should be able to answer yes to all of these:
- Can a new assistant tell which outputs are authoritative?
- Can we explain what is shared vs project-specific?
- Can we run AI-washing without blocking ERI planning?
- Can we define ERI without contaminating the AI-washing source of truth?
- Can we describe AllocationLab as an active program without pretending it is already implemented?
- Can we produce public-safe proof outputs without exposing private or partner-sensitive material?

If not, the lab is not at MVP 1.0 yet.

## Likely MVP 1.0 deliverables

The minimum concrete set is:
- engine boundary memo
- source-of-truth map
- artifact policy
- project registry
- FilingLens thin proof
- ERI interview and pilot kit
- AllocationLab architecture pack
- one shared reporting / memo discipline note

## What MVP 2.0 would mean later

Only after MVP 1.0 is functioning should we talk seriously about MVP 2.0.

Likely MVP 2.0 questions:
- do we need a neutral package namespace?
- do we need a separate lab-core package?
- do we need a workbench UI?
- do we need scheduled pipelines or agent orchestration for multiple active programs?
- do we need dedicated project repos?

Those are real future questions, but they should come after MVP 1.0 proves that the lab can host parallel programs at all.

## Bottom line

Lab MVP 1.0 is not a product release.
It is the minimum structure that lets this repo become a serious multi-program lab instead of a growing pile of related projects.
