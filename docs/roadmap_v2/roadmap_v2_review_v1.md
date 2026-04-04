# Roadmap V2 Review V1

## Scope reviewed

Reviewed inputs:
- external roadmap draft:
  - `/Users/soheilkhodadadi/Library/CloudStorage/OneDrive-ConcordiaUniversity-Canada/Portfolio/Roadmap/v2_roadmap.md`
- roadmap conversation export:
  - `/Users/soheilkhodadadi/Library/CloudStorage/OneDrive-ConcordiaUniversity-Canada/Portfolio/Roadmap/Reports/roadmap v2 chat.docx`
- current repo state:
  - `README.md`
  - `docs/preliminary_delivery_status_2026-03-20.md`
  - `reports/analysis/pass_c_technical_audit_2026-03-25_v1.md`

## Bottom line

The strategic direction is strong.

The best part of V2 is the shift away from "launch something small quickly" toward "explain clearly what has already been built and reuse it deliberately." That is the right move given the current repository state. The repo is no longer a loose prototype. It already contains a governed extraction, classification, aggregation, validation, and paper-support pipeline. Treating that as a reusable engine is realistic.

The part I would change is the sequencing.

V2 is conceptually right, but still slightly overloaded as a near-term execution plan. In particular, it keeps too many serious fronts alive at once:
- engine clarification
- ERI interview readiness
- AllocationLab architecture
- FilingLens proof
- public packaging
- Upwork / freelance positioning

All of those are plausible. Running all of them as equal-priority fronts is not.

## What is strong in V2

### 1. Interview-readiness-first is the correct pivot

This is the most important improvement over the earlier portfolio-first idea.

At this moment, the highest-value assets in the repo are:
- a working disclosure-intelligence pipeline
- a real academic paper draft
- a paper-support audit layer
- a controlled planning / governance layer through Director

Those assets are much better suited to:
- supervisor conversations
- partner / postdoc / internship conversations
- research assistant or collaborator credibility

than to generic freelance marketing.

### 2. The shared-engine framing is real, not imagined

The six-layer framing is good:
1. corpus and ingestion
2. evidence unitization / extraction
3. taxonomy and scoring
4. aggregation and benchmarking
5. external validation and diagnostics
6. governance, audit trail, and planning control

That is a credible way to explain what the repo already does.

### 3. "Do not split the repo yet" is exactly right

That guardrail should stay.

The current repo is still the best place to preserve:
- context continuity
- control-plane continuity
- source-of-truth documents
- technical debt visibility

Prematurely extracting three new repos would mostly create maintenance cost.

### 4. Public-safe vs private-local separation is essential

This is one of the best parts of the V2 plan and should become an actual repository habit.

You now have at least three different output classes:
- public-safe proof
- supervisor / interview kits
- partner-sensitive or NDA-bound materials

Those cannot live in the same artifact lane.

## What I would change

### 1. Move FilingLens ahead of AllocationLab in execution order

AllocationLab is intellectually exciting and strategically important, but it is farther from the current engine than FilingLens is.

FilingLens has three practical advantages:
- it reuses the current repo most directly
- it gives you a visible thin proof faster
- it creates a bridge between academic credibility and portfolio / interview credibility

AllocationLab should stay in the roadmap, but I would move it behind the first thin proof.

That means:
- engine memo first
- ERI interview kit second
- FilingLens thin proof third
- AllocationLab architecture fourth

not because AllocationLab matters less, but because it is more likely to sprawl if it starts too early.

### 2. Treat Upwork as a packaging lane, not a strategic driver

Upwork is not the right north star for architecture decisions.

Use Upwork and portfolio positioning as a downstream packaging layer that consumes:
- FilingLens proof
- engine memo language
- public-safe case studies

Do not let freelance positioning define the core roadmap.

### 3. Add one small evidence-of-transfer step before ERI becomes fully persuasive

The ERI interview kit is a good idea, but it risks staying too conceptual if it is docs-only all the way through.

A better version is:
- ERI interview kit first
- then one tiny transfer proof

That transfer proof does **not** need to be a full ERI build.
It could be as small as:
- one draft environmental disclosure taxonomy
- a micro benchmark set
- a sample annotation worksheet
- a mock scoring memo on 2-3 public sustainability reports

That would materially improve credibility in conversations without forcing a major new pipeline build.

### 4. Make "source-of-truth map" non-optional

The repo now contains a lot of real value, but it also contains a lot of history.

If the engine boundary memo happens without a source-of-truth map, you risk reintroducing ambiguity about:
- which panel is current
- which measurement artifacts are current
- which outputs are preliminary vs authoritative
- which reports are paper-support vs legacy

So I would explicitly elevate `source_of_truth_map_v1` to the same importance as the engine memo itself.

## Realism check

### What is realistic in the next 30-40 days

Realistic:
- engine boundary memo
- source-of-truth map
- artifact policy
- ERI interview kit
- one thin FilingLens proof
- one high-level AllocationLab architecture memo

Potentially unrealistic if all treated as full builds:
- a polished public FilingLens release
- a real ERI system build
- a serious AllocationLab implementation
- broad freelance packaging at the same time

So the practical rule should be:
- one serious proof
- one serious interview kit
- one architecture memo
- then packaging

not three serious builds in parallel.

## Recommended Roadmap V3

### Lane 0. Hold the paper lane steady

Do not reopen the main empirical lane until the supervisor / coauthor feedback arrives.

Use the current paper state as:
- credibility
- source material
- proof of execution discipline

The `2016-2024` scope is currently coherent and defensible for AI. There is no reason to force a year-2000 expansion unless feedback explicitly demands it.

### Lane 1. Engine clarity and source-of-truth

Goal:
- explain what has already been built
- define what is reusable
- define what is still project-specific

Deliverables:
- `engine_boundary_memo_v1.md`
- `source_of_truth_map_v1.md`
- `artifact_policy_v1.md`

Gate:
- you can explain the repo as a reusable disclosure-intelligence engine in 5 minutes

### Lane 2. ERI interview readiness

Goal:
- make the current engine legible as a direct precursor to ERI

Deliverables:
- `eri_interview_kit_v1.md`
- `eri_90_day_pilot_v1.md`
- `eri_q_and_a_v1.md`

Preferred extra:
- one tiny transfer proof artifact, not a full build

Gate:
- you can answer corpus, taxonomy, benchmark, validation, ownership, and first-90-day questions clearly

### Lane 3. FilingLens thin proof

Goal:
- produce one visible, real proof of reuse from the current engine

Deliverables:
- `filinglens_thin_slice_spec_v1.md`
- `filinglens_sample_set_v1.md`
- `filinglens_public_artifact_policy_v1.md`
- one reproducible proof run on 3-5 public filings

Gate:
- one clean example can be shown without explanation gymnastics

### Lane 4. AllocationLab architecture

Goal:
- preserve the opportunity without pretending it is ready for implementation

Deliverables:
- `allocationlab_architecture_v1.md`
- `allocationlab_gap_matrix_v1.md`
- `allocationlab_synthetic_case_v1.md`

Gate:
- you can explain what phase 1 actually is and what remains later-stage

### Lane 5. Packaging and outreach

Goal:
- convert the strongest artifacts into portfolio / outreach material

Deliverables:
- supervisor briefing pack
- public-safe proof pack
- short portfolio case-study copy
- lightweight Upwork positioning only after the above exists

Gate:
- every artifact has a clear audience and a clear privacy level

## Operational guardrails

1. Do not create multiple repos yet.
2. Do not extract a shared engine package yet.
3. Keep Packet 1 and Packet 2 docs-first.
4. Keep public-safe and private-local outputs physically separated.
5. Require one acceptance gate per Codex packet.
6. Require a git checkpoint before each serious packet.
7. Do not let FilingLens turn into a full product build before the thin proof is stable.
8. Do not let AllocationLab turn into a vague architecture rabbit hole; timebox it.

## My recommendation for the immediate next move

Start with:
- `docs/roadmap_v2/engine_boundary_memo_v1.md`
- `docs/roadmap_v2/source_of_truth_map_v1.md`

That is still the right first move from V2, and it remains the highest-leverage transition step.

The only sequencing change I recommend after that is:
- ERI kit next
- FilingLens thin proof after that
- AllocationLab architecture after the first visible proof exists

That keeps the roadmap ambitious, but more realistic and easier to execute well.
