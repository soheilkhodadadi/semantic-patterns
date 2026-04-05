# Engine Boundary Memo V1

## Purpose

This memo defines the first practical boundary between the reusable lab core and the current project-specific implementation.

The goal is not to finalize a platform package design.
The goal is to make it clear:
- what the lab already owns
- what is still AI-washing-specific
- what should be promoted only after reuse pressure appears

## Boundary statement

The reusable engine is the workflow discipline and asset structure, not the current AI taxonomy or patent-specific analytical outputs.

The engine boundary should therefore include:
- control-plane artifacts
- evidence and benchmark infrastructure
- evaluation and registry infrastructure
- shared reporting and export primitives
- environment and execution contracts

The engine boundary should not automatically include:
- AI-specific labels
- patent mismatch logic
- paper-specific panel construction
- current empirical tables and figures

## Current extraction reality

The most defensible immediately-shareable core in the current repo is smaller than the full analytical stack.

Today, the safest shared-core candidate is:
- the `semantic_ai_washing.director` orchestration kernel and its generic planning / review / policy machinery

Today, the following still read primarily as project-specific application code:
- `data`
- `classification`
- `labeling`
- `aggregation`
- `analysis`
- `patents`

Those areas contain reusable workflow patterns, but they are still tightly bound to current AI-washing semantics, data contracts, and output expectations.

That means the first restructure should avoid pretending the whole repo is already a neutral engine package.

## Shared lab core

### 1. Control plane
Includes:
- roadmap and boundary notes
- source-of-truth map
- artifact policy
- project registry
- acceptance gates
- privacy classes

### 2. Evidence core
Includes:
- corpus manifests
- source window definitions
- canonical text units
- label and adjudication tables
- benchmark and split registries

### 3. Evaluation core
Includes:
- held-out evaluation harnesses
- IRR and disagreement diagnostics
- model and scoring registries
- run metadata and provenance

### 4. Shared delivery core
Includes:
- memo and report generation patterns
- standalone table and figure generation patterns
- export conventions for markdown / docx / figures
- audience-aware artifact classes

## Current AI-washing project layer

This application currently owns:
- AI keyword family
- actionable / speculative / irrelevant taxonomy
- patent linkage and mismatch definitions
- ever-speaker panel and downstream regressions
- publication-specific results draft and delivery artifacts

These are first-class outputs of the lab, but they are not the lab definition.

## Candidate future adapters

### ERI adapter
Would add:
- environmental/climate disclosure corpus rules
- ERI-specific taxonomy and reliability dimensions
- ERI benchmark rules
- ERI aggregation and toolkit outputs

### AllocationLab adapter
Would add:
- project-level entity rules
- project ontology and scoring dimensions
- scenario and financing modules
- project-level ranking and sensitivity outputs

## Promotion rules

### Promote to shared core when
- the capability is needed by at least two active programs
- the interface can be named without reference to one project only
- the output contract is stable enough to be reused

### Keep project-specific when
- the logic encodes one project's semantics
- the downstream audience is project-specific
- the interface is still changing rapidly inside one lane

## Immediate implication for restructure

The first restructure should focus on:
- documenting shared-core boundaries
- identifying reusable contracts
- reducing ambiguity in artifact ownership
- preparing project-adapter framing

The first restructure should not focus on:
- massive code motion for cosmetic reasons
- neutral renaming of everything
- speculative extraction of a generalized package

## Near-term boundary pressure points in the current repo

Strongest pressure points already visible:
- legacy and transitional namespaces outside `src/semantic_ai_washing/`
- mixed generations of outputs and reports
- paper-support artifacts living alongside more general workflow assets
- project-specific semantics currently embedded in broadly useful workflow paths

These are good candidates for boundary cleanup.

## Bottom line

The engine is the reusable measurement-and-delivery workflow.
The current AI-washing implementation is the first flagship adapter built on top of it.

That distinction should govern the restructure from here forward.
