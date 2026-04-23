#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

KEY_FILE="${OPENAI_KEY_FILE:-$HOME/.config/semantic-patterns/openai_api_key}"
if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  if [[ ! -f "$KEY_FILE" ]]; then
    echo "missing API key file: $KEY_FILE" >&2
    exit 1
  fi
  export OPENAI_API_KEY="$(<"$KEY_FILE")"
fi

INPUT_CSV="${SHADOW_INPUT_CSV:-data/processed/shadow/deferred_review_sheets/selective_defer_conf49_shadow_full_corpus_v1.csv}"
OUTPUT_CSV="${SHADOW_OUTPUT_CSV:-$INPUT_CSV}"
REPORT_PATH="${SHADOW_REPORT_PATH:-reports/api/shadow_conf49_api_tranche_v1_report.json}"
PROGRESS_PATH="${SHADOW_PROGRESS_PATH:-reports/api/shadow_conf49_api_tranche_v1_progress.json}"
POLICY_PATH="${SHADOW_POLICY_PATH:-director/config/api_assistive_policy_shadow_full_corpus_mini_v2.yaml}"
COST_POLICY_PATH="${SHADOW_COST_POLICY_PATH:-director/config/cost_policy_gpt5mini.yaml}"

MAX_ROWS_PER_CALL="${MAX_ROWS_PER_CALL:-25}"
MAX_REQUESTS="${MAX_REQUESTS:-4}"
MAX_TOTAL_COST_USD="${MAX_TOTAL_COST_USD:-3.0}"
SLEEP_SECONDS="${SLEEP_SECONDS:-0.0}"

PYTHON_BIN="${PYTHON_BIN:-python3}"
BASE_PYTHONPATH="src:projects/ai_washing/src:packages/director/src:packages/labcore/src"
EXTRA_PYTHONPATH="${PYTHONPATH_EXTRA:-}"
if [[ -z "$EXTRA_PYTHONPATH" && "$PYTHON_BIN" != "./.venv/bin/python" ]]; then
  for candidate in ./.venv/lib/python*/site-packages; do
    if [[ -d "$candidate" ]]; then
      EXTRA_PYTHONPATH="$candidate"
      break
    fi
  done
fi
if [[ -n "$EXTRA_PYTHONPATH" ]]; then
  BASE_PYTHONPATH="$BASE_PYTHONPATH:$EXTRA_PYTHONPATH"
fi

PYTHONPATH="$BASE_PYTHONPATH" \
"$PYTHON_BIN" -m semantic_ai_washing.labeling.run_assistive_prelabel_restartable \
  --input-csv "$INPUT_CSV" \
  --output-csv "$OUTPUT_CSV" \
  --report "$REPORT_PATH" \
  --progress-report "$PROGRESS_PATH" \
  --policy "$POLICY_PATH" \
  --cost-policy "$COST_POLICY_PATH" \
  --mode live \
  --max-rows-per-call "$MAX_ROWS_PER_CALL" \
  --max-requests "$MAX_REQUESTS" \
  --max-total-cost-usd "$MAX_TOTAL_COST_USD" \
  --sleep-seconds "$SLEEP_SECONDS"
