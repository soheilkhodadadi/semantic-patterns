# Restructure Short-Term Rounds V1

## Purpose

This note converts the current architecture review and parallel protocol into the next short-term execution ladder.

The intent is to make the next restructure rounds easy to execute, easy to review, and easy to stop after any batch if priorities change.

## Current checkpoint

Completed already:
- Wave 1 control-plane setup
- Wave 2 lane scaffolding
- Wave 3 low-level shared helper round
  - registry helpers
  - runtime helpers
  - audit helpers
  - security helpers
  - OpenAI Responses helpers
- project adapter framing and adapter registry

This means the repo now has a real shared-control foundation.

## Next rounds

### Round A. Shared contracts

Objective:
- define the first truly reusable contracts above the helper level

Primary outputs:
- manifest contract note
- evidence-unit contract note
- minimal code placeholders only if justified

Work mode:
- serialized control-plane definition
- small parallel drafting around README pointers or test scaffolds

Acceptance gate:
- a collaborator can tell what a manifest is, what an evidence unit is, and what fields are shared across projects

### Round B. Adapter namespace preparation

Objective:
- make room for real code-side adapter ownership without forcing immediate migrations

Primary outputs:
- `src/semantic_ai_washing/adapters/ai_washing/`
- `src/semantic_ai_washing/adapters/eri/`
- `src/semantic_ai_washing/adapters/allocationlab/`
- one orientation note per namespace

Work mode:
- parallel by project

Acceptance gate:
- the repo has an obvious code-side landing zone for each project adapter even if most logic remains legacy for now

### Round C. First caller migrations

Objective:
- prove that extracted helpers are actually shared in use, not only shared in storage

Primary outputs:
- one bounded runtime-caller migration batch
- one bounded audit-caller migration batch
- one bounded security-caller migration batch
- one bounded responses-caller migration batch

Work mode:
- parallel by helper family

Acceptance gate:
- selected callers import from `labcore` directly
- compatibility shims remain for untouched callers
- no behavioral regressions on touched slices

### Round D. Artifact-lane normalization

Objective:
- make future authoritative outputs land in project/shared lanes by default

Primary outputs:
- project-specific output landing updates
- registry pointer updates
- mapping note refreshes where authoritative paths change

Work mode:
- parallel by project or artifact family

Acceptance gate:
- newly created artifacts stop defaulting into ambiguous legacy locations

## Recommended pacing

The right near-term order is:
1. Round A
2. Round B
3. Round C
4. Round D

Reason:
- contracts should come before migrations
- namespaces should come before broader project code moves
- caller migrations should come after shared APIs are explicit
- artifact relocation should happen after ownership is clearer

## What not to do yet

Still defer:
- package rename
- multi-repo split
- large deletions of legacy AI-washing paths
- broad analytical refactors under the name of lab cleanup
- forcing ERI or AllocationLab into deeper implementation before the contracts are stable

## Bottom line

The first shared-helper round is complete.
The next serious acceleration should come from contracts, namespaces, and bounded caller migrations, not from extracting random code just because it looks reusable.
