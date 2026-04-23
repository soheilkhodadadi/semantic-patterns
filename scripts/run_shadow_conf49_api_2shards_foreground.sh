#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="${LOG_DIR:-logs/shadow_conf49}"
mkdir -p "$LOG_DIR"

launch_shard() {
  local shard_name="$1"
  local shard_csv="$2"
  local report_path="$3"
  local progress_path="$4"
  local log_path="$5"

  env \
    PYTHON_BIN="${PYTHON_BIN:-python3}" \
    SHADOW_INPUT_CSV="$shard_csv" \
    SHADOW_OUTPUT_CSV="$shard_csv" \
    SHADOW_REPORT_PATH="$report_path" \
    SHADOW_PROGRESS_PATH="$progress_path" \
    MAX_REQUESTS="${MAX_REQUESTS:-10000}" \
    MAX_ROWS_PER_CALL="${MAX_ROWS_PER_CALL:-25}" \
    MAX_TOTAL_COST_USD="${MAX_TOTAL_COST_USD:-17}" \
    SLEEP_BETWEEN_RUNS="${SLEEP_BETWEEN_RUNS:-2}" \
    MAX_STALLED_RUNS="${MAX_STALLED_RUNS:-3}" \
    ./scripts/run_shadow_conf49_api_shard_loop.sh \
    >>"$log_path" 2>&1 &

  local pid=$!
  echo "$shard_name pid=$pid log=$log_path"
}

launch_shard \
  "conf49_shard01" \
  "data/processed/shadow/deferred_review_sheets/shards/conf49/selective_defer_conf49_shadow_remaining_v1_shard01.csv" \
  "reports/api/shards/conf49_shard01_overnight_report.json" \
  "reports/api/shards/conf49_shard01_overnight_progress.json" \
  "$LOG_DIR/conf49_shard01.log"

launch_shard \
  "conf49_shard02" \
  "data/processed/shadow/deferred_review_sheets/shards/conf49/selective_defer_conf49_shadow_remaining_v1_shard02.csv" \
  "reports/api/shards/conf49_shard02_overnight_report.json" \
  "reports/api/shards/conf49_shard02_overnight_progress.json" \
  "$LOG_DIR/conf49_shard02.log"

echo "waiting on shard workers"
wait
