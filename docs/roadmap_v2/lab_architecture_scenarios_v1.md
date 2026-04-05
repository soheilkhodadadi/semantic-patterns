# Lab Architecture Scenarios V1

## Purpose

This note compares plausible architecture paths for turning the current repository into a multi-program lab.

It is written for a realistic but ambitious setting:
- one ongoing publication program
- one or more emerging application programs
- possible assistants, collaborators, or funded project staff
- strong desire to avoid rebuilding each project from scratch in isolated repos

## Scenario A. Disciplined project host

### Description
Keep the repo mostly as it is and improve it through:
- better docs
- better artifact policies
- better output naming
- a source-of-truth map
- a few shared utilities

### Advantages
- lowest near-term disruption
- safest for current AI-washing work
- easiest to continue using immediately

### Risks
- weak support for parallel projects
- unclear ownership if a team grows
- duplication pressure remains high
- project boundaries still depend too much on oral knowledge

### Verdict
Useful as a stabilization step, but not sufficient if the lab is meant to support multiple real programs.

## Scenario B. Monorepo lab with shared core and project adapters

### Description
Keep one repo, but restructure conceptually around:
- shared lab core
- project adapters
- shared delivery surfaces
- explicit control-plane documents and registries

This does not require an immediate code split, but it does require boundary-setting and selective reorganization.

### Advantages
- supports parallel programs without immediate multi-repo cost
- preserves current context and working code
- creates reusable structure for future projects
- makes team onboarding much easier
- allows gradual promotion of reusable components into shared core

### Risks
- requires disciplined ownership and conventions
- may feel slower at first because boundary work comes before some coding work
- can become messy again if promotion rules are not enforced

### Verdict
This is the recommended near-to-medium-term structure.
It is the right architecture for `Lab MVP 1.0`.

## Scenario C. Split platform with separate product repos

### Description
Extract a neutral platform or core package and split projects into their own repos or services early.

### Advantages
- strongest conceptual separation
- easier product-level branding later
- cleaner long-term if many mature products already exist

### Risks
- high abstraction cost before reuse pressure is proven
- large migration and maintenance burden
- easiest way to break current working pipelines
- likely premature for the current maturity level

### Verdict
This is a possible later `MVP 2.0+` direction, but not the right immediate move.

## Recommended choice

The best current choice is:
- Scenario B now
- with selective elements of Scenario A for safety
- and Scenario C only as a later trigger-based option

In plain terms:
- do a serious restructure
- but keep it monorepo and boundary-driven
- do not jump straight to a generalized platform split

## What Scenario B should look like in practice

### Shared lab core
Owns:
- manifests
- evidence units
- labels and benchmarks
- evaluation harnesses
- artifact registry
- shared reporting/export primitives
- environment and run contracts

### Project adapters
Own:
- domain corpus rules
- taxonomy and rubric
- benchmark specifics
- scoring logic
- downstream analytical outputs

Near-term adapters:
- AI-washing
- ERI
- AllocationLab

### Delivery surfaces
Own:
- paper-support objects
- memos and reports
- proof demos
- partner-facing packages
- public-safe outputs

### Control plane
Owns:
- project registry
- privacy classes
- source-of-truth maps
- acceptance gates
- promotion rules

## Promotion rule

The most important rule is:
- promote to shared core only after second reuse

This keeps the lab from becoming a speculative framework exercise.

## What this means for the next 1-2 months

The next 1-2 months should build the control plane and shared-core boundary, not a polished product shell.

That means the first serious outputs should be:
- engine boundary memo
- source-of-truth map
- artifact policy
- project registry
- FilingLens thin proof definition
- ERI early adapter framing
- AllocationLab architecture boundary

## What this means for the next 3-6 months

Success after 3-6 months would mean:
- AI-washing is still advancing as a publication lane
- FilingLens exists as a bounded proof surface
- ERI has started real reuse of the shared core
- AllocationLab has a real architecture basis and dependency map
- the repo is understandable to collaborators without relying on memory or chat history

## Bottom line

If the ambition is to run several serious programs over time, the correct move is not to keep starting from scratch.
The correct move is to build a monorepo lab with a real shared core and project adapters, then decide later whether the pressure exists for a platform split.
