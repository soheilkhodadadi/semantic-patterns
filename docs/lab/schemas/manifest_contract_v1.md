# Manifest Contract V1

## Purpose

This note defines the minimum contract for a tracked manifest in the lab.

A manifest is not the payload itself.
A manifest is the structured description of:
- what an asset set is
- where it came from
- what inputs it depends on
- what outputs it produced
- what status and scope it has

The goal is to make shared artifacts understandable, promotable, and portable across projects.

## What counts as a manifest

A manifest is appropriate when the file's main job is to describe assets or a frozen transformation boundary.

Typical examples:
- source manifests
- benchmark manifests
- split registries
- promotion manifests
- curated dataset manifests
- inventory-style manifests for authoritative shared assets

Not a manifest by default:
- raw payload data
- full analysis narratives
- prose-only reports
- exploratory scratch notes

## Current repo anchors

The current repo already contains manifest-like artifacts, including:
- `data/metadata/splits/split_registry_v1.json`
- files in `data/manifests/`

Those anchors inform this contract, but the contract is meant to be broader than one project.

## Required fields

A tracked manifest should include these fields.

### Identity
- `manifest_id`
  - stable identifier for this manifest object
- `manifest_type`
  - for example: `source_manifest`, `benchmark_manifest`, `split_registry`, `promotion_manifest`, `dataset_manifest`
- `status`
  - one of: `draft`, `working`, `frozen`, `superseded`, `archived`

### Scope and ownership
- `scope`
  - one of: `shared`, `project`
- `project`
  - required when `scope = project`
- `owner_lane`
  - authoritative tracked lane for the manifest

### Provenance
- `generated_at_utc`
- `git_commit`
  - if generated from tracked code
- `producer`
  - script, module, or workflow name that created or last materially updated the manifest

### Inputs
- `inputs`
  - mapping of named inputs to paths or identifiers
- input hashes where feasible for frozen inputs

### Outputs
- `outputs`
  - mapping of named outputs to paths or identifiers
- output hashes where feasible for frozen outputs

### Summary
- `summary`
  - machine-readable compact facts needed to understand the manifest without opening the payloads

## Strongly recommended fields

- `version`
- `notes`
- `parameters`
- `privacy_class`
  - one of: `public_safe`, `internal`, `private_local`
- `supersedes`
  - prior manifest id if this replaces an older frozen object
- `related_evidence_ids`
  - if downstream evidence objects rely on this manifest

## Field expectations

### `manifest_id`
Should be stable, readable, and versioned.

Good pattern:
- `split_registry_v1`
- `ai_washing_panel_manifest_v1`

### `status`
Use `frozen` when:
- inputs are pinned
- outputs are pinned
- summary is final for that version

Use `working` when:
- the object is informative but still subject to revision

### `scope`
Use `shared` only when the manifest is meant to serve more than one project or defines a lab-wide asset family.

If the object mainly serves one project, keep it project-scoped even if others may later borrow ideas from it.

### `summary`
The summary should carry the facts another contributor needs quickly, such as:
- row counts
- split sizes
- class counts
- uniqueness checks
- coverage checks
- freeze state
- seed or assignment method where relevant

## Placement rules

### Shared manifests
Default home:
- `data/manifests/`
- or a future normalized lane under `shared/manifests/`

### Project manifests
Future home:
- `projects/<project>/reports/` or `projects/<project>/docs/` if human-facing
- or `projects/<project>/output/` if generated and versioned there

Near-term transition rule:
- keep current authoritative paths until a migration note promotes a replacement lane

## Format guidance

Preferred tracked formats:
- JSON for machine-readable manifests
- Markdown companion note only when human interpretation is needed

A good default pair is:
- one JSON manifest
- optional one Markdown note that explains why it matters

## Naming guidance

Suggested filenames:
- `<name>_manifest_vN.json`
- `<name>_registry_vN.json`
- `<name>_promotion_vN.json`

Avoid generic names like:
- `manifest.json`
- `final_manifest.json`
- `new_registry.json`

## Acceptance checks

A manifest is in good shape when:
- it has a stable identity
- its scope is explicit
- its producer is named
- its inputs and outputs are named
- frozen artifacts include hashes where practical
- its summary is enough for quick review
- its authoritative lane is unambiguous

## Relationship to evidence objects

A manifest describes an asset boundary.
An evidence object supports a claim about quality, performance, or validity.

Example:
- a split registry is a manifest
- a held-out evaluation report is evidence

The two often point to one another but should not be collapsed into one concept.

## Minimal example shape

```json
{
  "manifest_id": "split_registry_v1",
  "manifest_type": "split_registry",
  "status": "frozen",
  "scope": "shared",
  "owner_lane": "data/metadata/splits/",
  "generated_at_utc": "2026-03-15T20:16:09+00:00",
  "git_commit": "<commit>",
  "producer": "semantic_ai_washing.data.<module>",
  "inputs": {},
  "outputs": {},
  "summary": {}
}
```

## Bottom line

A manifest should tell another contributor:
- what this asset boundary is
- where it came from
- what it produced
- whether it is shared or project-scoped
- whether it is stable enough to trust as a source-of-truth object
