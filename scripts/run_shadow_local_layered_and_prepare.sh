#!/usr/bin/env zsh
set -euo pipefail

cd /Users/soheilkhodadadi/Documents/Projects/semantic-patterns

export PYTHONPATH="src:projects/ai_washing/src:packages/director/src:packages/labcore/src"

LOCAL_MANIFEST="artifacts/models/prelim_selected_model_layered_local_v1.json"
LOCAL_MODEL_ID="layered_binary_relevance_logreg_as_shadow_v1"
LOCAL_OUTPUT_ROOT="data/processed/classifications_shadow_local_layered_v1"
LOCAL_SOURCE_WINDOW_ID="annual_10k_2016_2025_shadow_local_layered_v1"

./.venv/bin/python -m semantic_ai_washing.classification.classify_active_window_preliminary_restartable \
  --input-root data/processed/sentences_clean \
  --years 2016 2017 2018 2019 2020 2021 2022 2023 2024 \
  --selected-model-manifest "$LOCAL_MANIFEST" \
  --output-root "$LOCAL_OUTPUT_ROOT" \
  --output-report reports/classification/active_window_coverage_shadow_local_layered_2016_2024_v1.json \
  --progress-report reports/classification/active_window_coverage_shadow_local_layered_2016_2024_progress_v1.json \
  --model-id "$LOCAL_MODEL_ID" \
  --source-window-id "$LOCAL_SOURCE_WINDOW_ID" \
  --chunk-size 2048

./.venv/bin/python -m semantic_ai_washing.classification.classify_active_window_preliminary_restartable \
  --input-root data/processed/sentences_clean_refresh_2025_v1 \
  --years 2025 \
  --selected-model-manifest "$LOCAL_MANIFEST" \
  --output-root "$LOCAL_OUTPUT_ROOT" \
  --output-report reports/classification/active_window_coverage_shadow_local_layered_2025_v1.json \
  --progress-report reports/classification/active_window_coverage_shadow_local_layered_2025_progress_v1.json \
  --model-id "$LOCAL_MODEL_ID" \
  --source-window-id "$LOCAL_SOURCE_WINDOW_ID" \
  --chunk-size 2048

mkdir -p data/processed/shadow/deferred_review_sheets reports/classification

for policy in conf49 conf54 conf_or_margin; do
  ./.venv/bin/python -m semantic_ai_washing.classification.prepare_shadow_defer_review_sheet \
    --input-root "$LOCAL_OUTPUT_ROOT" \
    --years 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025 \
    --model-id "$LOCAL_MODEL_ID" \
    --policy "$policy" \
    --output-csv "data/processed/shadow/deferred_review_sheets/selective_defer_${policy}_shadow_full_corpus_v1.csv" \
    --output-report "reports/classification/selective_defer_${policy}_shadow_full_corpus_v1.json"
done

echo "shadow local classification and defer-sheet prep complete"
