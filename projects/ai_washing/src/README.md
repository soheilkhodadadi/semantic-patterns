# AI-Washing Member Source Shell

This directory is the future code shell for the `ai_washing` member.

Current authoritative code still lives in:
- `src/semantic_ai_washing/`

Do not create a duplicate local `semantic_ai_washing` package here until the code authority map is narrower and the package-identity plan is explicit.
## Status
- first real member-owned code slice now lives under this directory
- the member shell is still not a buildable package yet

## Transitional import path

The first bounded code-seed move uses the transitional member-local import path:
- `ai_washing_member.labeling.common`

This avoids duplicating the canonical `semantic_ai_washing` package identity
too early while still giving the member shell a real code owner.

## Current authoritative slice

Current member-owned code:
- `projects/ai_washing/src/ai_washing_member/labeling/common.py`
- `projects/ai_washing/src/ai_washing_member/classification/preliminary_pipeline.py`
- `projects/ai_washing/src/ai_washing_member/classification/model_runtime.py`

Legacy compatibility remains at:
- `src/semantic_ai_washing/labeling/common.py`
