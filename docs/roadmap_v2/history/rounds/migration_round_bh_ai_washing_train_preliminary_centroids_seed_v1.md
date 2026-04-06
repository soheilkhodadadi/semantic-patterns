# Migration Round BH: AI-Washing Train Preliminary Centroids Seed V1

## Purpose

Seed the canonical member-owned centroid-training authority for the active preliminary classification lane and migrate its direct test callers.

## Canonical authority

- `projects/ai_washing/src/ai_washing_member/classification/train_preliminary_centroids.py`

## Compatibility shim

- `src/semantic_ai_washing/classification/train_preliminary_centroids.py`

## Direct callers migrated

- `tests/test_preliminary_phase3.py`
- `tests/test_preliminary_benchmarking.py`

## Validation gate

- `make doctor`
- targeted Ruff/`py_compile`
- `projects/ai_washing/tests/test_train_preliminary_centroids_member.py`
- `tests/test_preliminary_benchmarking.py -k "train_wave1_models_hash_backend"`
- `git diff --check`
