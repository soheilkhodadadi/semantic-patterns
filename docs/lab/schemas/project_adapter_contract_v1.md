# Project Adapter Contract V1

## Purpose

This schema note defines the minimum stable shape for a tracked project adapter in Lab MVP 1.0.

## Required fields

- `project`
  - canonical slug
- `mode`
  - current operating mode such as `flagship_publication`, `incubation_reuse_test`, or `architecture_first`
- `purpose`
  - compact statement of what the adapter is for
- `framing_note`
  - tracked project note that explains the adapter boundary in prose
- `docs`
  - tracked docs root
- `reports`
  - tracked reports root
- `processed_data`
  - tracked processed-data root
- `doc_output`
  - tracked document-output root
- `figure_output`
  - tracked figure-output root
- `local_private_root`
  - non-tracked root for sensitive or NDA-bound material
- `shared_dependencies`
  - tuple of currently approved shared-core dependencies

## Initial implementation

The first implementation lives in:
- `semantic_ai_washing.labcore.registry.adapters.ProjectAdapterContract`

## Design rule

The contract should stay small.
If a field is not needed to route work, define ownership, or explain allowed dependencies, it should stay in the project framing notes instead of the contract.
