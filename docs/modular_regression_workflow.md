# Modular Regression Workflow

Use the modular runner when you want to refresh one regression family or a small set of model variants without rebuilding the entire paper bundle.

The runner filters the existing portfolio spec, writes a separate artifact bundle under `results/`, and reuses the same estimation code as the main portfolio path.

For the current preliminary-delivery lane, prefer the rebuilt ever-speaker annual panel unless you are intentionally reproducing the older conditional speaking-only regressions.

## Full rerun

```bash
cd /Users/soheilkhodadadi/Documents/Projects/semantic-patterns
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.analysis.run_modular_regression_portfolio \
  --panel data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv \
  --spec-path reports/analysis/regression_specification_prelim_v1.json \
  --outdir results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique \
  --bundle-name full_portfolio
```

## One family

```bash
cd /Users/soheilkhodadadi/Documents/Projects/semantic-patterns
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.analysis.run_modular_regression_portfolio \
  --panel data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv \
  --spec-path reports/analysis/regression_specification_prelim_v1.json \
  --outdir results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique \
  --families headline_dual \
  --bundle-name headline_dual_only
```

## Specific model IDs

```bash
cd /Users/soheilkhodadadi/Documents/Projects/semantic-patterns
env PYTHONPATH=src ./.venv/bin/python -m semantic_ai_washing.analysis.run_modular_regression_portfolio \
  --panel data/processed/panel/panel_reg_ready_ever_speaker_2016_2024_v1.csv \
  --spec-path reports/analysis/regression_specification_prelim_v1.json \
  --outdir results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique \
  --model-ids portfolio_lpm_anypat_k1_actionable_only_fe,portfolio_lpm_anypat_k1_speculative_only_fe \
  --bundle-name action_spec_only
```

## Notes

- The modular runner writes its own bundle directory under `results/`.
- Each bundle contains a manifest, a summary markdown table, a summary CSV, and coefficient exports.
- The default portfolio runner remains available for full canonical reruns.
- If you want the older conditional panel on purpose, pass `data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv` explicitly.
