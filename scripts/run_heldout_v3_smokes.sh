#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${REPO_ROOT}"

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  printf 'OpenAI API key: ' >&2
  stty -echo
  IFS= read -r OPENAI_API_KEY
  stty echo
  printf '\n' >&2
  export OPENAI_API_KEY
fi

python - <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

req = urllib.request.Request(
    "https://api.openai.com/v1/models",
    headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY'].strip()}"},
)
try:
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = json.load(response)
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", "replace")
    print(body, file=sys.stderr)
    raise SystemExit(1)

print(f"[auth] ok models={len(payload.get('data', []))}")
PY

./.venv/bin/python - <<'PY'
import pandas as pd

source = pd.read_csv("data/validation/held_out_v3/held_out_sentences_v3_review_slice40.csv").head(10)
for output in (
    "data/validation/held_out_v3/held_out_sentences_v3_smoke10_gpt5.csv",
    "data/validation/held_out_v3/held_out_sentences_v3_smoke10_gpt5mini.csv",
):
    source.to_csv(output, index=False)
print(f"[smoke-setup] rows={len(source)}")
PY

export PYTHONPATH="src:projects/ai_washing/src:packages/director/src:packages/labcore/src"

./.venv/bin/python -m semantic_ai_washing.labeling.run_assistive_prelabel_restartable \
  --input-csv data/validation/held_out_v3/held_out_sentences_v3_smoke10_gpt5.csv \
  --output-csv data/validation/held_out_v3/held_out_sentences_v3_smoke10_gpt5.csv \
  --report reports/final/ai_washing_heldout_v3_smoke10_gpt5_report_v1.json \
  --progress-report reports/final/ai_washing_heldout_v3_smoke10_gpt5_progress_v1.json \
  --policy director/config/api_assistive_policy_heldout_v3.yaml \
  --mode live \
  --max-rows-per-call 1 \
  --max-requests 10

./.venv/bin/python -m semantic_ai_washing.labeling.run_assistive_prelabel_restartable \
  --input-csv data/validation/held_out_v3/held_out_sentences_v3_smoke10_gpt5mini.csv \
  --output-csv data/validation/held_out_v3/held_out_sentences_v3_smoke10_gpt5mini.csv \
  --report reports/final/ai_washing_heldout_v3_smoke10_gpt5mini_report_v1.json \
  --progress-report reports/final/ai_washing_heldout_v3_smoke10_gpt5mini_progress_v1.json \
  --policy director/config/api_assistive_policy_heldout_v3_mini.yaml \
  --mode live \
  --max-rows-per-call 1 \
  --max-requests 10

echo "[done] smoke runs completed"
