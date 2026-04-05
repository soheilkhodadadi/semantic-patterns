# Roadmap V4 Multi-Program V1

## Why this revision exists

The earlier roadmap revisions assumed a relatively controlled sequencing:
- hold the AI-washing paper steady
- clarify the reusable engine
- package FilingLens
- incubate ERI
- preserve AllocationLab as architecture-first

That logic was sound for a constrained single-founder path.

The current reality is more complex:
- the AI-washing paper is likely to continue as an active top-tier publication track
- ERI may become active within the next 1-3 months
- AllocationLab may also become active on a similar timeline
- resource constraints may ease if these projects formalize through funded work, research assistance, or a small team

This changes the planning problem.

The goal is no longer just "what should be the next project?"
The goal is now:
- how to run one continuing publication program and up to two application programs in parallel without chaos
- how to make the current repo capable of supporting that parallelism
- how to do this without a premature platform rewrite

## Bottom line

Yes, it is plausible to support three active fronts at once, but only if we stop treating the repo as a single-project workflow and start treating it as a lab with:
- a shared core
- project adapters
- shared delivery surfaces
- a clear operating model
- explicit separation between platform work and project work

If those boundaries do not exist, three parallel projects will collapse into:
- naming confusion
- duplicated scripts
- conflicting artifact outputs
- unclear ownership
- brittle validation
- slow onboarding for assistants and collaborators

So the next design objective is not just "engine boundary."
It is:
- a minimum viable multi-program lab structure

## The new strategic picture

### Program A. AI-washing / FilingLens

This is no longer just a paper.
It is now both:
- an ongoing publication asset
- the first proof surface for the lab

This lane should continue to produce:
- paper-ready empirical outputs
- validation artifacts
- bounded public-safe proof material

This lane is valuable because it is the most mature and can keep producing visible credibility.

### Program B. ERI

ERI is the best candidate for the first real reuse of the core.

Why:
- closest to the current text-measurement pattern
- benchmark / IRR discipline transfers directly
- disclosure reliability is conceptually adjacent to the AI-washing setup
- the deliverables are concrete enough to define a 90-day pilot path

### Program C. AllocationLab

AllocationLab is still the most ambitious lane.

But if it activates, it cannot be treated as "the next coding project."
It has to be treated as:
- a program with shared dependence on the lab core
- plus a separate decision layer that will mature more slowly

This means AllocationLab can be active without dominating implementation immediately.

## Revised planning principle

The near-term objective should be:
- build a lab that can host multiple programs
not:
- fully build three projects at once

That is the crucial distinction.

The lab should make it possible to run three programs in parallel by giving them:
- common ingestion and provenance rules
- common evidence-unit contracts
- common labeling / evaluation discipline
- common artifact lanes
- common reporting surfaces

The projects then differ in:
- corpus
- taxonomy
- scoring logic
- domain outputs
- stakeholders

## The right target: Lab MVP 1.0

The next real destination should be a `Lab MVP 1.0`.

Its job is not to be the final platform.
Its job is to make parallel work possible and controlled.

A good Lab MVP 1.0 would let us say:
- we can onboard a new domain project without reinventing the workflow
- we can keep current publication work alive without blocking new application work
- we can assign a small team across shared core and project-specific pods
- we can produce auditable outputs for different audiences from one governed system

## What Lab MVP 1.0 must include

### 1. Shared core contracts

The lab must define reusable contracts for:
- source registry and manifests
- evidence-unit tables
- benchmark and label tables
- model and evaluation registries
- output artifact classes
- run metadata and provenance

This is the non-negotiable base.

### 2. Project adapters

Each project should live as an adapter around the core.

For example:
- AI-washing adapter
- ERI adapter
- AllocationLab adapter

Each adapter should define:
- domain corpus
- domain taxonomy
- domain benchmark logic
- domain scoring outputs
- domain-specific external validation or downstream analysis

### 3. Shared delivery layer

A multi-program lab needs a shared output surface.

That includes:
- memo generation
- table and figure generation
- dashboard or notebook-facing summary outputs
- partner-safe vs public-safe packaging
- reproducible export paths

This is where FilingLens becomes useful as a proof surface.

### 4. Shared operational layer

The lab needs one place for:
- access rules
- privacy classes
- environment contracts
- monitoring and logging
- batch scheduling or run orchestration
- QA gates

This does not need enterprise infrastructure on day one.
But it does need clear conventions.

## What changes from the earlier roadmap

### Earlier assumption
- one main lane at a time

### New assumption
- one mature publication lane plus one or two emerging application lanes

### Earlier priority
- sequencing only

### New priority
- concurrency architecture plus sequencing

### Earlier question
- what should we do next?

### New question
- what structure lets us do several things at once without breaking quality?

## Recommended operating model

If a 5-6 person team becomes available, the right model is not six people all editing the same codebase ad hoc.

The right model is:

### Core pod
Owns:
- manifests
- evidence tables
- benchmark contracts
- evaluation harnesses
- artifact registry
- shared reporting / packaging tools

Likely size:
- 2 people

### Project pods
Each active project gets a bounded pod around the shared core.

#### AI-washing / FilingLens pod
Owns:
- paper-specific empirical work
- FilingLens proof surface
- public-safe demo packaging

#### ERI pod
Owns:
- climate/environment taxonomy
- benchmark design
- early pilot corpus and scoring logic

#### AllocationLab pod
Owns:
- architecture
- ontology
- synthetic case design
- later project-level decision logic

Likely size:
- 1-2 people per active lane, depending on maturity

### Program lead / integration lead
Owns:
- cross-program prioritization
- acceptance gates
- what gets promoted from project code into shared core
- what stays project-specific

This is likely your role.

## The key design rule

Promote upward only when reused twice.

That means:
- if a component only serves AI-washing, keep it in that project layer
- if ERI and AI-washing both need a capability, then consider promoting it to shared core
- if AllocationLab later reuses the same capability, it confirms the promotion

This keeps the lab from becoming a speculative abstraction exercise.

## Practical 3-6 month roadmap under the new reality

### Phase 0. Immediate stabilization
Time horizon:
- next 1-2 weeks

Goals:
- acknowledge AI-washing as an ongoing publication track
- define the lab target clearly
- define project classes and privacy classes

Deliverables:
- Lab MVP 1.0 blueprint
- artifact policy
- source-of-truth map
- project classification map

### Phase 1. Core enablement
Time horizon:
- weeks 2-6

Goals:
- make the shared core legible and usable by more than one person
- create the minimum conventions needed for assistants or collaborators

Deliverables:
- engine boundary memo
- runbook map
- canonical output / artifact registry
- shared memo/report export conventions

### Phase 2. AI-washing as proof surface
Time horizon:
- weeks 3-8

Goals:
- preserve the publication lane
- shape FilingLens as the first visible proof of the lab

Deliverables:
- FilingLens thin proof
- public-safe example outputs
- AI-washing delivery pack as reusable proof material

### Phase 3. ERI incubation
Time horizon:
- weeks 4-12

Goals:
- test real cross-domain reuse
- create the first non-AI application on top of the lab core

Deliverables:
- ERI interview kit
- ERI pilot plan
- ERI taxonomy v0.1
- first small transfer-proof artifact

### Phase 4. AllocationLab architecture track
Time horizon:
- weeks 6-16

Goals:
- keep the opportunity alive without letting it consume the implementation roadmap

Deliverables:
- architecture memo
- gap matrix
- synthetic case
- explicit dependency map on the shared lab core

### Phase 5. Lab MVP 1.0 checkpoint
Time horizon:
- months 3-6

Goals:
- verify whether the lab can actually support parallel programs
- identify what should become Lab MVP 2.0

Success looks like:
- AI-washing still moving
- FilingLens proof usable
- ERI has a credible pilot path
- AllocationLab architecture is structured, not vague
- assistants can onboard without oral tradition

## What not to do yet

Do not do yet:
- a full platform rewrite
- a large package renaming initiative without pressure from real reuse
- a new multi-repo split
- a full UI/dashboard program for all projects
- deep AllocationLab build-out before the shared core proves itself on ERI

## Critical implication for the repo

The repo must now be designed as a lab host, not just as a chapter host.

That does not mean a rewrite.
It means the repo should gradually gain:
- shared core maps
- project adapter boundaries
- artifact classes
- privacy classes
- onboarding clarity

## Immediate next move

The next move should be to define `Lab MVP 1.0` explicitly.

That should answer:
- what layers exist
- which ones are shared
- which ones are project-specific
- how multiple projects can run in parallel
- what the minimum viable team operating model is
- what must exist before we can say the lab is real
