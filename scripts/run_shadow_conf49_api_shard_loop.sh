#!/usr/bin/env zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

SLEEP_BETWEEN_RUNS="${SLEEP_BETWEEN_RUNS:-2}"
MAX_STALLED_RUNS="${MAX_STALLED_RUNS:-3}"

if [[ -z "${SHADOW_INPUT_CSV:-}" ]]; then
  echo "SHADOW_INPUT_CSV is required" >&2
  exit 1
fi

snapshot_counts() {
  python3 - "$SHADOW_INPUT_CSV" <<'PY'
import csv, sys
from pathlib import Path
path = Path(sys.argv[1])
done = total = 0
with path.open(newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1
        if (row.get('assistive_label') or '').strip():
            done += 1
print(done, total - done)
PY
}

stalled_runs=0
run_index=0

while true; do
  read -r done_before pending_before <<< "$(snapshot_counts)"
  echo "[loop] run=$run_index done=$done_before pending=$pending_before" >&2

  if [[ "$pending_before" -le 0 ]]; then
    echo "[loop] no pending rows remain" >&2
    break
  fi

  set +e
  ./scripts/run_shadow_conf49_api_tranche.sh
  tranche_exit=$?
  set -e

  read -r done_after pending_after <<< "$(snapshot_counts)"
  echo "[loop] run=$run_index tranche_exit=$tranche_exit after done=$done_after pending=$pending_after" >&2

  if [[ "$done_after" -le "$done_before" ]]; then
    stalled_runs=$((stalled_runs + 1))
    echo "[loop] no forward progress detected (stalled=$stalled_runs/$MAX_STALLED_RUNS)" >&2
  else
    stalled_runs=0
  fi

  if [[ "$pending_after" -le 0 ]]; then
    echo "[loop] completed shard" >&2
    break
  fi

  if [[ "$stalled_runs" -ge "$MAX_STALLED_RUNS" ]]; then
    echo "[loop] stopping after repeated stalled runs" >&2
    break
  fi

  run_index=$((run_index + 1))
  sleep "$SLEEP_BETWEEN_RUNS"
done
