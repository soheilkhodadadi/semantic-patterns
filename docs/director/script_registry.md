<!-- generated_file: true -->
<!-- source_inventory: director/snapshots/script_inventory.json -->
<!-- source_sha256: f5030aedaf5d21d464823c9c50763a2c90eddf7abc728c9e63281a3af3ca85a9 -->
<!-- rendered_at: 2026-04-06T18:00:48.574724+00:00 -->

# Script Registry

This document is generated from the repo script inventory snapshot.

## Summary
- Python modules inventoried: `199`
- Canonical modules: `138`
- Transitional modules: `59`
- Legacy modules: `2`
- Entrypoints: `101`
- Hygiene findings: `44`

## Canonical Entrypoints

| Module | Invocation | Notes |
| --- | --- | --- |
| `semantic_ai_washing.aggregation.aggregate_classification_counts` | `python -m semantic_ai_washing.aggregation.aggregate_classification_counts` | Aggregate per-file classification outputs into firm-year features. |
| `semantic_ai_washing.aggregation.build_ever_speaker_annual_panel` | `python -m semantic_ai_washing.aggregation.build_ever_speaker_annual_panel` | Build an annual ever-speaker panel with calendar-year patent timing. |
| `semantic_ai_washing.aggregation.build_panel` | `python -m semantic_ai_washing.aggregation.build_panel` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.aggregation.build_preliminary_narrative_measures` | `python -m semantic_ai_washing.aggregation.build_preliminary_narrative_measures` | Build preliminary firm-year AI metrics and proposal-defined narrative measures. |
| `semantic_ai_washing.aggregation.export_preliminary_ai_frequencies` | `python -m semantic_ai_washing.aggregation.export_preliminary_ai_frequencies` | Export clean preliminary firm-year AI metrics into the legacy CSV merge shape. |
| `semantic_ai_washing.aggregation.merge_ai_with_patents` | `python -m semantic_ai_washing.aggregation.merge_ai_with_patents` | Merge AI sentence frequencies (firm-year) with patents (firm-year). |
| `semantic_ai_washing.analysis.audit_preliminary_panel_inputs` | `python -m semantic_ai_washing.analysis.audit_preliminary_panel_inputs` | Audit patents and controls coverage before preliminary panel assembly. |
| `semantic_ai_washing.analysis.build_delivery_figures` | `python -m semantic_ai_washing.analysis.build_delivery_figures` | Build standalone delivery-phase figures and review DOCX wrappers. |
| `semantic_ai_washing.analysis.build_delivery_table_docs` | `python -m semantic_ai_washing.analysis.build_delivery_table_docs` | Build standalone journal-style DOCX tables for preliminary delivery. |
| `semantic_ai_washing.analysis.generate_delivery_table_artifacts` | `python -m semantic_ai_washing.analysis.generate_delivery_table_artifacts` | Generate standalone delivery-phase table artifacts. |
| `semantic_ai_washing.analysis.generate_paper_assets` | `python -m semantic_ai_washing.analysis.generate_paper_assets` | Generate paper-facing snippets and tables from current project artifacts. |
| `semantic_ai_washing.analysis.generate_preliminary_regression_spec` | `python -m semantic_ai_washing.analysis.generate_preliminary_regression_spec` | Generate a preliminary regression specification scaffold for the paper lane. |
| `semantic_ai_washing.analysis.prepare_panel_for_regression` | `python -m semantic_ai_washing.analysis.prepare_panel_for_regression` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.analysis.run_modular_regression_portfolio` | `python -m semantic_ai_washing.analysis.run_modular_regression_portfolio` | Run a filtered regression portfolio as a separate artifact bundle. |
| `semantic_ai_washing.analysis.run_regression_portfolio` | `python -m semantic_ai_washing.analysis.run_regression_portfolio` | Run a spec-driven regression portfolio on the prepared panel. |
| `semantic_ai_washing.analysis.run_regressions` | `python -m semantic_ai_washing.analysis.run_regressions` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.classification.classify_all_ai_sentences` | `python -m semantic_ai_washing.classification.classify_all_ai_sentences` | Batch classifier for AI-related sentences using SentenceBERT and cosine similarity. |
| `semantic_ai_washing.core.features` | `python -m semantic_ai_washing.core.features` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.core.plots` | `python -m semantic_ai_washing.core.plots` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.core.score_sentences` | `python -m semantic_ai_washing.core.score_sentences` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.data.build_active_filing_company_universe` | `python -m semantic_ai_washing.data.build_active_filing_company_universe` | Build a broader firm-universe CSV from the indexed active filing window. |
| `semantic_ai_washing.data.build_company_list` | `python -m semantic_ai_washing.data.build_company_list` | Build a reproducible firm list (~50 CIKs) that **have a 10‑K in each year 2021–2024** |
| `semantic_ai_washing.data.clean_sentence_tables` | `python -m semantic_ai_washing.data.clean_sentence_tables` | Post-extraction cleanup for canonical AI sentence parquet tables. |
| `semantic_ai_washing.data.pull_compustat_controls` | `python -m semantic_ai_washing.data.pull_compustat_controls` | Pull Compustat controls from WRDS, build a CIK↔GVKEY crosswalk for your 50 firms, |
| `semantic_ai_washing.diagnostics.environment_audit` | `python -m semantic_ai_washing.diagnostics.environment_audit` | Audit local Python environments against the repo's canonical runtime target. |
| `semantic_ai_washing.diagnostics.phase0_baseline` | `python -m semantic_ai_washing.diagnostics.phase0_baseline` | Phase 0 diagnostics baseline runner for Iteration 1. |
| `semantic_ai_washing.diagnostics.wrds_smoke` | `python -m semantic_ai_washing.diagnostics.wrds_smoke` | Run a live WRDS connectivity smoke test from the canonical repo environment. |
| `semantic_ai_washing.director.__main__` | `python -m semantic_ai_washing.director.__main__` | Compatibility shim for the package-owned director module entrypoint. |
| `semantic_ai_washing.labeling.assistive_prelabel_batch` | `python -m semantic_ai_washing.labeling.assistive_prelabel_batch` | Compatibility shim for the member-owned assistive prelabel helpers. |
| `semantic_ai_washing.labeling.benchmark_prompt_variants` | `python -m semantic_ai_washing.labeling.benchmark_prompt_variants` | Compatibility shim for the member-owned prompt benchmark helpers. |
| `semantic_ai_washing.labeling.freeze_split_registry` | `python -m semantic_ai_washing.labeling.freeze_split_registry` | Compatibility shim for grouped split-registry freezing. |
| `semantic_ai_washing.labeling.publish_rubric_freeze` | `python -m semantic_ai_washing.labeling.publish_rubric_freeze` | Compatibility shim for provisional rubric-freeze publishing. |
| `semantic_ai_washing.labeling.run_assistive_prelabel_restartable` | `python -m semantic_ai_washing.labeling.run_assistive_prelabel_restartable` | Restartable assistive-only prelabel runner for bounded review sheets. |
| `semantic_ai_washing.labeling.sample_heldout_v2_restartable` | `python -m semantic_ai_washing.labeling.sample_heldout_v2_restartable` | Restartable held_out_v2 candidate sampling with progress logging. |
| `semantic_ai_washing.modeling.predict` | `python -m semantic_ai_washing.modeling.predict` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.modeling.train` | `python -m semantic_ai_washing.modeling.train` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.patents.benchmark_keyword_sets` | `python -m semantic_ai_washing.patents.benchmark_keyword_sets` | Benchmark multiple patent keyword sets on the same matched patent candidate pool. |
| `semantic_ai_washing.patents.benchmark_keyword_sets_lightweight` | `python -m semantic_ai_washing.patents.benchmark_keyword_sets_lightweight` | Lightweight patent keyword benchmark using only the Python standard library. |
| `semantic_ai_washing.patents.build_company_lookup` | `python -m semantic_ai_washing.patents.build_company_lookup` | Build a normalized company lookup table for patent matching. |
| `semantic_ai_washing.patents.extract_filtered_patents_lightweight` | `python -m semantic_ai_washing.patents.extract_filtered_patents_lightweight` | Lightweight PatentsView extractor using only the Python standard library. |
| `semantic_ai_washing.tests.evaluate_classifier_on_held_out` | `python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out` | primary implementation namespace under semantic_ai_washing |

## Transitional Surfaces

| Path | Canonical Target | Replacement Path | Removal Target |
| --- | --- | --- | --- |
| `src/aggregation/aggregate_classification_counts.py` | `semantic_ai_washing.aggregation.aggregate_classification_counts` | python -m semantic_ai_washing.aggregation.aggregate_classification_counts | Iteration 1 deprecation window |
| `src/aggregation/build_panel.py` | `semantic_ai_washing.aggregation.build_panel` | python -m semantic_ai_washing.aggregation.build_panel | Iteration 1 deprecation window |
| `src/aggregation/merge_ai_with_patents.py` | `semantic_ai_washing.aggregation.merge_ai_with_patents` | python -m semantic_ai_washing.aggregation.merge_ai_with_patents | Iteration 1 deprecation window |
| `src/analysis/prepare_panel_for_regression.py` | `semantic_ai_washing.analysis.prepare_panel_for_regression` | python -m semantic_ai_washing.analysis.prepare_panel_for_regression | Iteration 1 deprecation window |
| `src/analysis/run_regressions.py` | `semantic_ai_washing.analysis.run_regressions` | python -m semantic_ai_washing.analysis.run_regressions | Iteration 1 deprecation window |
| `src/analysis/summarize_classification_counts.py` | `semantic_ai_washing.analysis.summarize_classification_counts` | python -m semantic_ai_washing.analysis.summarize_classification_counts | Iteration 1 deprecation window |
| `src/classification/classify_all_ai_sentences.py` | `semantic_ai_washing.classification.classify_all_ai_sentences` | python -m semantic_ai_washing.classification.classify_all_ai_sentences | Iteration 1 deprecation window |
| `src/classification/classify_with_centroids.py` | `semantic_ai_washing.classification.classify_with_centroids` | python -m semantic_ai_washing.classification.classify_with_centroids | Iteration 1 deprecation window |
| `src/classification/compute_centroids.py` | `semantic_ai_washing.classification.compute_centroids` | python -m semantic_ai_washing.classification.compute_centroids | Iteration 1 deprecation window |
| `src/classification/compute_centroids_mpnet.py` | `semantic_ai_washing.classification.compute_centroids_mpnet` | python -m semantic_ai_washing.classification.compute_centroids_mpnet | Iteration 1 deprecation window |
| `src/classification/embed_labeled_sentences.py` | `semantic_ai_washing.classification.embed_labeled_sentences` | python -m semantic_ai_washing.classification.embed_labeled_sentences | Iteration 1 deprecation window |
| `src/classification/embed_labeled_sentences_mpnet.py` | `semantic_ai_washing.classification.embed_labeled_sentences_mpnet` | python -m semantic_ai_washing.classification.embed_labeled_sentences_mpnet | Iteration 1 deprecation window |
| `src/classification/utils.py` | `semantic_ai_washing.classification.utils` | python -m semantic_ai_washing.classification.utils | Iteration 1 deprecation window |
| `src/config/config.py` | `semantic_ai_washing.config.config` | python -m semantic_ai_washing.config.config | Iteration 1 deprecation window |
| `src/core/classify.py` | `semantic_ai_washing.core.classify` | python -m semantic_ai_washing.core.classify | Iteration 1 deprecation window |
| `src/core/features.py` | `semantic_ai_washing.core.features` | python -m semantic_ai_washing.core.features | Iteration 1 deprecation window |
| `src/core/plots.py` | `semantic_ai_washing.core.plots` | python -m semantic_ai_washing.core.plots | Iteration 1 deprecation window |
| `src/core/score_sentences.py` | `semantic_ai_washing.core.score_sentences` | python -m semantic_ai_washing.core.score_sentences | Iteration 1 deprecation window |
| `src/core/sentence_filter.py` | `semantic_ai_washing.core.sentence_filter` | python -m semantic_ai_washing.core.sentence_filter | Iteration 1 deprecation window |
| `src/core/sentence_scorer.py` | `semantic_ai_washing.core.sentence_scorer` | python -m semantic_ai_washing.core.sentence_scorer | Iteration 1 deprecation window |
| `src/data/build_company_list.py` | `semantic_ai_washing.data.build_company_list` | python -m semantic_ai_washing.data.build_company_list | Iteration 1 deprecation window |
| `src/data/clean_compustat.py` | `semantic_ai_washing.data.clean_compustat` | python -m semantic_ai_washing.data.clean_compustat | Iteration 1 deprecation window |
| `src/data/clean_crsp.py` | `semantic_ai_washing.data.clean_crsp` | python -m semantic_ai_washing.data.clean_crsp | Iteration 1 deprecation window |
| `src/data/clean_sec.py` | `semantic_ai_washing.data.clean_sec` | python -m semantic_ai_washing.data.clean_sec | Iteration 1 deprecation window |
| `src/data/download_compustat.py` | `semantic_ai_washing.data.download_compustat` | python -m semantic_ai_washing.data.download_compustat | Iteration 1 deprecation window |
| `src/data/download_crsp.py` | `semantic_ai_washing.data.download_crsp` | python -m semantic_ai_washing.data.download_crsp | Iteration 1 deprecation window |
| `src/data/download_sec.py` | `semantic_ai_washing.data.download_sec` | python -m semantic_ai_washing.data.download_sec | Iteration 1 deprecation window |
| `src/data/extract_ai_sentences.py` | `semantic_ai_washing.data.extract_ai_sentences` | python -m semantic_ai_washing.data.extract_ai_sentences | Iteration 1 deprecation window |
| `src/data/extract_sample_filings.py` | `semantic_ai_washing.data.extract_sample_filings` | python -m semantic_ai_washing.data.extract_sample_filings | Iteration 1 deprecation window |
| `src/data/index_sec_filings.py` | `semantic_ai_washing.data.index_sec_filings` | python -m semantic_ai_washing.data.index_sec_filings | Iteration 1 deprecation window |
| `src/data/pull_compustat_controls.py` | `semantic_ai_washing.data.pull_compustat_controls` | python -m semantic_ai_washing.data.pull_compustat_controls | Iteration 1 deprecation window |
| `src/modeling/predict.py` | `semantic_ai_washing.modeling.predict` | python -m semantic_ai_washing.modeling.predict | Iteration 1 deprecation window |
| `src/modeling/train.py` | `semantic_ai_washing.modeling.train` | python -m semantic_ai_washing.modeling.train | Iteration 1 deprecation window |
| `src/patents/build_company_lookup.py` | `semantic_ai_washing.patents.build_company_lookup` | python -m semantic_ai_washing.patents.build_company_lookup | Iteration 1 deprecation window |
| `src/patents/define_keywords.py` | `semantic_ai_washing.patents.define_keywords` | python -m semantic_ai_washing.patents.define_keywords | Iteration 1 deprecation window |
| `src/patents/extract_ai_patents.py` | `semantic_ai_washing.patents.extract_ai_patents` | python -m semantic_ai_washing.patents.extract_ai_patents | Iteration 1 deprecation window |
| `src/patents/extract_filtered_patents.py` | `semantic_ai_washing.patents.extract_filtered_patents` | python -m semantic_ai_washing.patents.extract_filtered_patents | Iteration 1 deprecation window |
| `src/patents/extract_from_patentsview.py` | `semantic_ai_washing.patents.extract_from_patentsview` | python -m semantic_ai_washing.patents.extract_from_patentsview | Iteration 1 deprecation window |
| `src/patents/filter_relevant_patent_ids.py` | `semantic_ai_washing.patents.filter_relevant_patent_ids` | python -m semantic_ai_washing.patents.filter_relevant_patent_ids | Iteration 1 deprecation window |
| `src/scripts/build_company_list.py` | `semantic_ai_washing.data.build_company_list` | python -m semantic_ai_washing.data.build_company_list | Iteration 3 |
| `src/scripts/extract_sample_filings.py` | `semantic_ai_washing.data.extract_sample_filings` | python -m semantic_ai_washing.data.extract_sample_filings | Iteration 3 |
| `src/scripts/filter_ai_sentences.py` | `semantic_ai_washing.data.extract_ai_sentences` | python -m semantic_ai_washing.data.extract_ai_sentences | Iteration 3 |
| `src/scripts/index_sec_filings.py` | `semantic_ai_washing.data.index_sec_filings` | python -m semantic_ai_washing.data.index_sec_filings | Iteration 3 |
| `src/scripts/run_pipeline.py` | `semantic_ai_washing.scripts.run_pipeline` | python -m semantic_ai_washing.scripts.run_pipeline | Iteration 3 |
| `src/scripts/score_sentences.py` | `semantic_ai_washing.core.score_sentences` | python -m semantic_ai_washing.core.score_sentences | Iteration 3 |
| `src/semantic_ai_washing/data/clean_compustat.py` | `semantic_ai_washing.data.clean_compustat` | pending script-deprecation decision; keep operational but do not extend | queue-v23/script-deprecation-hygiene |
| `src/semantic_ai_washing/data/clean_crsp.py` | `semantic_ai_washing.data.clean_crsp` | pending script-deprecation decision; keep operational but do not extend | queue-v23/script-deprecation-hygiene |
| `src/semantic_ai_washing/data/clean_sec.py` | `semantic_ai_washing.data.clean_sec` | pending script-deprecation decision; keep operational but do not extend | queue-v23/script-deprecation-hygiene |
| `src/semantic_ai_washing/data/download_compustat.py` | `semantic_ai_washing.data.download_compustat` | pending script-deprecation decision; keep operational but do not extend | queue-v23/script-deprecation-hygiene |
| `src/semantic_ai_washing/data/download_crsp.py` | `semantic_ai_washing.data.download_crsp` | pending script-deprecation decision; keep operational but do not extend | queue-v23/script-deprecation-hygiene |
| `src/semantic_ai_washing/data/download_sec.py` | `semantic_ai_washing.data.download_sec` | pending script-deprecation decision; keep operational but do not extend | queue-v23/script-deprecation-hygiene |
| `src/semantic_ai_washing/data/extract_ai_sentences.py` | `semantic_ai_washing.data.extract_ai_sentences` | semantic_ai_washing.data.extract_sentence_table | iteration1/sentence-table-pilot-2024 |
| `src/semantic_ai_washing/data/extract_sample_filings.py` | `semantic_ai_washing.data.extract_sample_filings` | semantic_ai_washing.data.build_filing_manifest + semantic_ai_washing.data.extract_sentence_table | iteration1/source-index-contract |
| `src/semantic_ai_washing/scripts/run_pipeline.py` | `semantic_ai_washing.scripts.run_pipeline` | director runbooks or a future explicit pipeline CLI | iteration5/release-packaging |
| `src/tests/evaluate_classifier_on_held_out.py` | `semantic_ai_washing.tests.evaluate_classifier_on_held_out` | python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out | Iteration 1 deprecation window |
| `src/tests/spot_check_classifications.py` | `semantic_ai_washing.tests.spot_check_classifications` | python -m semantic_ai_washing.tests.spot_check_classifications | Iteration 1 deprecation window |
| `src/tests/test_classifier.py` | `semantic_ai_washing.tests.test_classifier` | python -m semantic_ai_washing.tests.test_classifier | Iteration 1 deprecation window |
| `src/tmp/aggregate_ai_sentences.py` | `semantic_ai_washing.tmp.aggregate_ai_sentences` | python -m semantic_ai_washing.tmp.aggregate_ai_sentences | Iteration 1 deprecation window |
| `src/tmp/clean_ai_sentences.py` | `semantic_ai_washing.tmp.clean_ai_sentences` | python -m semantic_ai_washing.tmp.clean_ai_sentences | Iteration 1 deprecation window |

## Legacy and Scratch Modules

| Path | Classification Note | Planned Action |
| --- | --- | --- |
| `src/semantic_ai_washing/tmp/aggregate_ai_sentences.py` | scratch/temporary namespace retained for traceability, not part of the canonical workflow | archive or remove during release packaging |
| `src/semantic_ai_washing/tmp/clean_ai_sentences.py` | scratch/temporary namespace retained for traceability, not part of the canonical workflow | archive or remove during release packaging |

## Planned Replacements

- `src/semantic_ai_washing/data/extract_sample_filings.py`: Replace raw filing copying with source index + bounded filing manifests.
- `src/semantic_ai_washing/data/extract_ai_sentences.py`: Replace per-filing *_ai_sentences.txt outputs with year-partitioned sentence tables.

Current canonical raw-source contract is `SEC_SOURCE_DIR` plus the source index. Per-filing copied raw filings and per-filing AI sentence text outputs remain operational but are not the target architecture.

## Hygiene Findings
- `python_cache_dir`: `src/__pycache__`
- `python_cache_dir`: `src/aggregation/__pycache__`
- `python_cache_dir`: `src/analysis/__pycache__`
- `python_cache_dir`: `src/classification/__pycache__`
- `python_cache_dir`: `src/config/__pycache__`
- `python_cache_dir`: `src/core/__pycache__`
- `python_cache_dir`: `src/data/__pycache__`
- `python_cache_dir`: `src/modeling/__pycache__`
- `python_cache_dir`: `src/patents/__pycache__`
- `python_cache_dir`: `src/scripts/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/aggregation/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/analysis/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/classification/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/config/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/core/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/data/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/diagnostics/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/director/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/director/adapters/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/director/core/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/director/policies/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/director/tasks/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/labcore/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/labcore/delivery/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/labcore/evaluation/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/labcore/evidence/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/labcore/manifests/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/labcore/registry/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/labeling/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/legacy/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/modeling/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/patents/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/scripts/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/tests/__pycache__`
- `python_cache_dir`: `src/semantic_ai_washing/tmp/__pycache__`
- `python_cache_dir`: `src/tests/__pycache__`
- `python_cache_dir`: `src/tmp/__pycache__`
- `macos_metadata`: `src/.DS_Store`
- `macos_metadata`: `src/semantic_ai_washing/aggregation/.DS_Store`
- `macos_metadata`: `src/semantic_ai_washing/data/.DS_Store`
- `python_cache_dir`: `tests/__pycache__`
- `macos_metadata`: `docs/.DS_Store`
- `macos_metadata`: `director/.DS_Store`
