# Source Control Cleanup Plan

This plan is intended to reduce VS Code source-control noise without deleting
real project work or mixing empirical and non-empirical feature lanes.

## Goal

Keep tracked:

- source code
- tests
- paper source
- selected generated paper/report artifacts that support the manuscript

Untrack or ignore:

- rerunnable processed data
- bulk results/output artifacts
- progress/debug files
- cache and junk files

## Step 1: Commit Real Work First

Commit the empirical-paper lane before any cleanup of generated files.

Recommended empirical commit scope:

- `src/semantic_ai_washing/analysis/**`
- `src/semantic_ai_washing/aggregation/**`
- `src/semantic_ai_washing/classification/**`
- `src/semantic_ai_washing/core/**`
- `src/semantic_ai_washing/data/**`
- `src/semantic_ai_washing/labeling/**`
- `src/semantic_ai_washing/patents/**`
- `tests/**`
- `paper/sections/**`
- `paper/guides/**`
- `paper/generated/**`
- `docs/preliminary_results_execution_plan.md`
- `docs/iteration_log.md`
- `docs/source_control_cleanup_plan.md`
- `scripts/build_paper.py`

Keep the `director` subsystem separate:

- `docs/director/**`
- `src/semantic_ai_washing/director/**`
- `tests/test_director_*.py`

That should be its own commit or its own branch decision.

## Step 2: Canonical Generated Artifacts to Keep Tracked

Keep tracked because they support the manuscript and are lightweight:

- `paper/generated/snippets/*.md`
- `paper/generated/tables/*.md`
- `reports/analysis/*.json`

Optional to keep tracked if cited directly:

- selected `results/**.md`
- selected `results/**.csv`

## Step 3: Generated Artifacts to Untrack

These are rerunnable and are the main noise source.

- `data/processed/**`
- `data/interim/**`
- `data/externals/crosswalks/*.csv`
- `results/**`
- `output/**`
- `tmp/**`
- `reports/**/progress*.json`
- `reports/classification/debug_*.json`
- `reports/data/patent_extraction_progress_*.json`
- `reports/controls_progress_*.json`

Important:

- if these files are already tracked, `.gitignore` is not enough
- they need to be removed from the git index with `git rm --cached ...`

## Step 4: Cache/Junk to Delete

These can be deleted safely.

- `**/__pycache__/**`
- `*.pyc`
- `.pytest_cache/**`
- `.ruff_cache/**`
- `.DS_Store`
- `tmp/*.log`
- `tmp/*_progress.json`
- `tmp/*_report.json`
- `.venv_atlas_broken_*`

## Step 5: Manual Review Before Deleting

These look like duplicates or backups and should be reviewed once before
removal.

- `data/labels/v1/*.bak.*`
- `data/labels/v1/* 2.csv`
- `data/labels/v1/*.numbers`
- `reports/labels/* 2.json`
- `data/labels/v1/irr_adjudication_completed.xlsx.xlsx`

Keep the canonical `.csv` / `.xlsx` files, then prune obvious duplicates.

## Step 6: Suggested `.gitignore` Additions

Add or confirm patterns for:

- `results/**`
- `output/**`
- `tmp/**`
- `reports/**/progress*.json`
- `reports/classification/debug_*.json`
- `.venv_atlas_broken_*`

## Step 7: Safe Execution Order

1. Commit empirical source/test/paper changes.
2. Decide whether to commit or park the `director` subsystem separately.
3. Update `.gitignore`.
4. Remove tracked generated artifacts from the index.
5. Delete cache/junk.
6. Manually review label/backups and then prune them.
7. Reopen VS Code source control and confirm the remaining diff is mostly real work.

## Recommended Execution Commands

Use these only after the empirical commit is secured.

```bash
git rm -r --cached data/processed data/interim results output tmp
git rm --cached data/externals/crosswalks/*.csv
git rm --cached reports/classification/debug_*.json
git rm --cached reports/data/patent_extraction_progress_*.json
git rm --cached reports/controls_progress_*.json
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
rm -rf .pytest_cache .ruff_cache
find . -name '.DS_Store' -delete
rm -rf .venv_atlas_broken_* 2>/dev/null || true
rm -f tmp/*.log tmp/*_progress.json tmp/*_report.json
```

## Success Condition

After cleanup:

- source control should mostly show real code/docs changes
- generated data/results noise should be largely gone
- manuscript-supporting generated markdown can remain tracked
- the repo should still rebuild outputs from scripts when needed
