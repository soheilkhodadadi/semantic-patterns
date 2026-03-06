<!-- generated_file: true -->
<!-- source_inventory: director/snapshots/script_inventory.json -->
<!-- source_sha256: 4dc66e19a24313cf68451bdf15654378949e2712ee79ba81874b23cbdad27390 -->
<!-- rendered_at: 2026-03-06T07:45:13.098417+00:00 -->

# Script Registry

This document is generated from the repo script inventory snapshot.

## Summary
- Python modules inventoried: `133`
- Canonical modules: `78`
- Transitional modules: `53`
- Legacy modules: `2`
- Entrypoints: `89`
- Hygiene findings: `37`

## Canonical Entrypoints

| Module | Invocation | Notes |
| --- | --- | --- |
| `semantic_ai_washing.aggregation.aggregate_classification_counts` | `python -m semantic_ai_washing.aggregation.aggregate_classification_counts` | Aggregate per-file classification outputs into firm-year features. |
| `semantic_ai_washing.aggregation.build_panel` | `python -m semantic_ai_washing.aggregation.build_panel` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.aggregation.merge_ai_with_patents` | `python -m semantic_ai_washing.aggregation.merge_ai_with_patents` | Merge AI sentence frequencies (firm-year) with patents (firm-year). |
| `semantic_ai_washing.analysis.prepare_panel_for_regression` | `python -m semantic_ai_washing.analysis.prepare_panel_for_regression` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.analysis.run_regressions` | `python -m semantic_ai_washing.analysis.run_regressions` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.classification.classify_all_ai_sentences` | `python -m semantic_ai_washing.classification.classify_all_ai_sentences` | Batch classifier for AI-related sentences using SentenceBERT and cosine similarity. |
| `semantic_ai_washing.core.features` | `python -m semantic_ai_washing.core.features` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.core.plots` | `python -m semantic_ai_washing.core.plots` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.core.score_sentences` | `python -m semantic_ai_washing.core.score_sentences` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.data.build_company_list` | `python -m semantic_ai_washing.data.build_company_list` | Build a reproducible firm list (~50 CIKs) that **have a 10‑K in each year 2021–2024** |
| `semantic_ai_washing.data.build_filing_manifest` | `python -m semantic_ai_washing.data.build_filing_manifest` | Build a deterministic filing manifest for the bounded 2024 sentence-table pilot. |
| `semantic_ai_washing.data.clean_compustat` | `python -m semantic_ai_washing.data.clean_compustat` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.data.clean_crsp` | `python -m semantic_ai_washing.data.clean_crsp` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.data.clean_sec` | `python -m semantic_ai_washing.data.clean_sec` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.data.download_compustat` | `python -m semantic_ai_washing.data.download_compustat` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.data.download_crsp` | `python -m semantic_ai_washing.data.download_crsp` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.data.download_sec` | `python -m semantic_ai_washing.data.download_sec` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.data.extract_sentence_table` | `python -m semantic_ai_washing.data.extract_sentence_table` | Extract a canonical sentence table from a bounded filing manifest. |
| `semantic_ai_washing.data.index_sec_filings` | `python -m semantic_ai_washing.data.index_sec_filings` | Index the external SEC corpus and emit source-window metadata. |
| `semantic_ai_washing.data.pull_compustat_controls` | `python -m semantic_ai_washing.data.pull_compustat_controls` | Pull Compustat controls from WRDS, build a CIK↔GVKEY crosswalk for your 50 firms, |
| `semantic_ai_washing.diagnostics.phase0_baseline` | `python -m semantic_ai_washing.diagnostics.phase0_baseline` | Phase 0 diagnostics baseline runner for Iteration 1. |
| `semantic_ai_washing.director.__main__` | `python -m semantic_ai_washing.director.__main__` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.director.cli` | `python -m semantic_ai_washing.director.cli` | CLI entrypoint for the autonomous director package. |
| `semantic_ai_washing.director.tasks.script_inventory` | `python -m semantic_ai_washing.director.tasks.script_inventory` | Generate a repo script inventory and a human-readable script registry. |
| `semantic_ai_washing.director.tasks.validation_assets` | `python -m semantic_ai_washing.director.tasks.validation_assets` | Generate a canonical registry for current validation assets. |
| `semantic_ai_washing.labeling.adjudicate_irr_labels` | `python -m semantic_ai_washing.labeling.adjudicate_irr_labels` | Create adjudication artifacts and optionally merge final IRR labels. |
| `semantic_ai_washing.labeling.build_labeling_sample` | `python -m semantic_ai_washing.labeling.build_labeling_sample` | Build Phase 1 labeling sample with leakage controls and stable IDs. |
| `semantic_ai_washing.labeling.compute_irr_metrics` | `python -m semantic_ai_washing.labeling.compute_irr_metrics` | Compute IRR metrics (Cohen's kappa + disagreement taxonomy). |
| `semantic_ai_washing.labeling.dedupe_labeled_sentences` | `python -m semantic_ai_washing.labeling.dedupe_labeled_sentences` | Deduplicate and merge labeled datasets for Phase 1. |
| `semantic_ai_washing.labeling.prepare_irr_subset` | `python -m semantic_ai_washing.labeling.prepare_irr_subset` | Prepare a stratified IRR subset and blinded rater templates. |
| `semantic_ai_washing.labeling.qa_labeled_dataset` | `python -m semantic_ai_washing.labeling.qa_labeled_dataset` | QA checks for Phase 1 expanded labeled dataset. |
| `semantic_ai_washing.modeling.predict` | `python -m semantic_ai_washing.modeling.predict` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.modeling.train` | `python -m semantic_ai_washing.modeling.train` | primary implementation namespace under semantic_ai_washing |
| `semantic_ai_washing.patents.build_company_lookup` | `python -m semantic_ai_washing.patents.build_company_lookup` | Builds a normalized company lookup table for patents work. |
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
