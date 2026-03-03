# Roadmap Master

This document is the canonical in-repo roadmap source for director ingestion.

## Iteration 0 - Stabilise the Extraction and Packaging
Goal: Establish a reliable packaged baseline that can run end-to-end on a sample year.

- Fix sentence/page fragment reconstruction in extraction.
- Package under `src/semantic_ai_washing` with canonical module execution.
- Add logging and minimal CI + pytest baseline.
- Document run flow and known limitations.

Outcome: Baseline pipeline runs on sample data with reproducible outputs.

## Iteration 1 - Expand Labels and Retrain Centroids
Goal: Improve classifier reliability and readiness while preserving science gates.

- Expand labeled dataset, dedupe, and enforce leakage-safe splits.
- Run IRR gate (`kappa >= 0.6`) before retraining.
- Re-embed labels and recompute centroids.
- Validate held-out accuracy (`>= 0.80`) on canonical evaluator.
- Add observability for A/S/I distributions and batch integrity checks.

Outcome: Retrained classifier with reproducibility metadata and explicit gate evidence.

## Iteration 2 - Scale Classification and Integrate Cross-walks
Goal: Produce full-sample sentence and firm-year outputs for downstream analysis.

- Run extraction/classification for broader year scope.
- Aggregate sentence outputs to firm-year metrics.
- Refresh cross-walk merges and patent/control integrations.
- Add schema validation and integration checks for merged tables.

Outcome: Stable firm-year panel inputs with validated data lineage.

## Iteration 3 - Evaluate OpenAI API Strategy
Goal: Decide whether and where LLM classification should augment existing pipeline.

- Run stratified pilot comparing MPNet vs LLM labels.
- Evaluate cost/time/quality trade-offs.
- Consider hybrid routing for borderline or ambiguous cases.
- Preserve deterministic MPNet path as baseline fallback.

Outcome: Explicit decision record for MPNet-only vs hybrid LLM strategy.

## Iteration 4 - Final Integration and Hardening
Goal: Deliver reproducible, auditable, publication-ready system.

- Assemble final panel and run regression/robustness workflows.
- Finalize docs, packaging, release artifacts, and changelog.
- Harden operations (failure handling, metrics, reproducibility checks).

Outcome: Production-ready research package with full audit trail.

## Global Gates
- IRR gate must pass before retraining.
- Held-out accuracy gate must pass before scaling claims.
- Leakage gate must hold across train/validation/test.
- Artifacts must include hashes, configs, and commit provenance.
- Deferred blockers must include expiry (`until_iteration`, `until_phase`) and re-check criteria.
