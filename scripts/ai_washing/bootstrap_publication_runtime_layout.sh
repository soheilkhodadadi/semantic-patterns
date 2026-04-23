#!/usr/bin/env bash

set -euo pipefail

ROOT="${1:-/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing}"
CREATE_VENV="${2:-}"
PY311_BIN="${PY311_BIN:-/opt/homebrew/opt/python@3.11/libexec/bin/python}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p \
  "$ROOT/runtime_venvs" \
  "$ROOT/logs" \
  "$ROOT/tmp" \
  "$ROOT/raw/sec" \
  "$ROOT/raw/wrds" \
  "$ROOT/raw/patents" \
  "$ROOT/raw/external" \
  "$ROOT/derived/panels" \
  "$ROOT/derived/event_study" \
  "$ROOT/derived/returns" \
  "$ROOT/derived/tables" \
  "$ROOT/derived/figures" \
  "$ROOT/derived/test_runs/test_01_mismatch_surge" \
  "$ROOT/derived/test_runs/test_02_filing_date_car" \
  "$ROOT/derived/test_runs/test_03_post_filing_drift" \
  "$ROOT/derived/test_runs/test_04_portfolio_sorts" \
  "$ROOT/derived/test_runs/test_05_size_heterogeneity" \
  "$ROOT/derived/test_runs/test_06_real_effects" \
  "$ROOT/derived/test_runs/test_07_chatgpt_did" \
  "$ROOT/derived/test_runs/test_08_financing_valuation" \
  "$ROOT/derived/test_runs/validation_refresh" \
  "$REPO_ROOT/paper/generated/latex" \
  "$REPO_ROOT/paper/generated/writer_packets"

cat > "$ROOT/README.md" <<EOF
# AI-Washing DataWork Runtime Root

This directory is the non-iCloud heavy runtime root for the AI-washing paper.

Use it for:
- runtime virtual environments
- heavy intermediate datasets
- event-study windows
- return panels
- test-run artifacts

Keep code, guides, and light paper exports in the repo:
- $REPO_ROOT
EOF

if [[ "$CREATE_VENV" == "--with-venv" ]]; then
  "$PY311_BIN" -m venv "$ROOT/runtime_venvs/ai_washing_py311"
  printf '%s\n' "created venv: $ROOT/runtime_venvs/ai_washing_py311"
fi

printf '%s\n' "bootstrapped publication runtime layout:"
printf '  %s\n' "$ROOT"
