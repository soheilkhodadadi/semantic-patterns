# Project Registry V1

## Purpose

This registry is the first public-safe catalog of active and likely-near-term programs in the lab.

It is intentionally lightweight.
Its purpose is to make program status, maturity, and reuse relationships explicit.

## Registry fields

- `project`
- `current mode`
- `maturity`
- `privacy class`
- `primary audience`
- `shared-core dependencies`
- `new domain semantics`
- `next 90-day deliverable`

## Current registry

| Project | Current mode | Maturity | Privacy class | Primary audience | Shared-core dependencies | New domain semantics | Next 90-day deliverable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| AI-washing | flagship publication program | active | mixed: public-safe + internal | coauthors, supervisor, journal pipeline | manifests, sentence units, labels, IRR, evaluation, reporting | AI disclosure taxonomy, patent linkage, mismatch logic | maintain publication lane and freeze a reusable baseline |
| FilingLens | proof surface / packaging lane | bounded proof | public-safe | portfolio, demos, external explanation | same as AI-washing baseline plus delivery surface | none beyond presentation and bounded proof framing | one end-to-end public-safe proof slice |
| ERI | incubation / pilot lane | emerging | local-private until cleared | supervisor, partner, interview/pilot stakeholders | manifests, text units, labels, IRR, evaluation, reporting | environmental/climate disclosure reliability taxonomy | interview kit, pilot framing, taxonomy v0.1 |
| AllocationLab | architecture and synthetic-case lane | concept-to-architecture | local-private until clarified | supervisor, partner, future team | manifests, evidence contracts, reporting, governance | project ontology, scenario logic, financing and ranking layer | architecture memo, gap matrix, synthetic case |

## Working interpretation

### AI-washing
This is the anchor lane.
It proves the lab can deliver serious outputs and should be treated as the current flagship benchmark program.

### FilingLens
This is not a separate research program.
It is the first outward-facing surface built on the AI-washing baseline.

### ERI
This is the first real test of cross-domain reuse.
It is the leading candidate for the next live application lane.

### AllocationLab
This is strategically important, but should remain architecture-first unless a dedicated implementation lane and staffing exist.

## Registry rules

### Add a project when
- it has a real audience and a plausible 90-day deliverable
- it can identify shared-core dependencies
- it has a clear privacy class

### Do not treat as active build when
- it has no bounded 90-day deliverable
- it depends on undefined new semantics and infrastructure simultaneously
- it does not yet have an owner or mode

## Bottom line

The lab should think in terms of a portfolio of programs, not a list of ideas.
The registry is the first lightweight control-plane object for that portfolio.
