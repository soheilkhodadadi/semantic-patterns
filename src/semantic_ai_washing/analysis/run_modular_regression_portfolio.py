"""Run a filtered regression portfolio as a separate artifact bundle.

This is a thin wrapper around ``run_regression_portfolio`` that keeps the
existing estimation logic intact while allowing smaller reruns by family or
explicit model_id selection.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from semantic_ai_washing.analysis.run_regression_portfolio import run_portfolio


DEFAULT_PANEL = "data/processed/panel/panel_reg_ready_2016_2024_applied_v2_legalnorm_unique.csv"
DEFAULT_SPEC_PATH = "reports/analysis/regression_specification_prelim_v1.json"
DEFAULT_OUTDIR = "results/01_baseline/tables_2016_2024_applied_v2_legalnorm_unique"
DEFAULT_BUNDLE_NAME = "modular_portfolio"


def _slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or DEFAULT_BUNDLE_NAME


def _split_csv_arg(raw_value: str) -> set[str]:
    return {item.strip() for item in raw_value.split(",") if item.strip()}


def _load_payload(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _filter_specs(
    payload: dict[str, Any],
    *,
    tiers: set[str],
    families: set[str],
    model_ids: set[str],
) -> dict[str, Any]:
    filtered = copy.deepcopy(payload)
    specs = filtered.get("specs")
    if specs is None:
        specs = (filtered.get("modeling") or {}).get("portfolio_models", [])
    if not isinstance(specs, list):
        raise ValueError("The supplied spec file does not contain a portfolio spec list.")

    subset: list[dict[str, Any]] = []
    for spec in specs:
        tier = str(spec.get("tier", "baseline"))
        family = str(spec.get("family", ""))
        model_id = str(spec.get("model_id", ""))
        if tiers and tier not in tiers:
            continue
        if families and family not in families:
            continue
        if model_ids and model_id not in model_ids:
            continue
        subset.append(spec)

    if not subset:
        raise ValueError(
            "No portfolio specs matched the requested filters: "
            f"tiers={sorted(tiers)} families={sorted(families)} model_ids={sorted(model_ids)}"
        )

    filtered["specs"] = subset
    if isinstance(filtered.get("modeling"), dict):
        filtered["modeling"]["portfolio_models"] = subset
    return filtered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", default=DEFAULT_PANEL)
    parser.add_argument("--spec-path", default=DEFAULT_SPEC_PATH)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument(
        "--tiers",
        default="baseline,robustness,appendix",
        help="Comma-separated portfolio tiers to run.",
    )
    parser.add_argument(
        "--families",
        default="",
        help="Optional comma-separated spec families to run.",
    )
    parser.add_argument(
        "--model-ids",
        default="",
        help="Optional comma-separated model_id values to run.",
    )
    parser.add_argument(
        "--bundle-name",
        default="",
        help="Optional bundle name. If omitted, one is derived from the selected filters.",
    )
    return parser.parse_args()


def run_modular_portfolio(args: argparse.Namespace) -> None:
    payload = _load_payload(args.spec_path)
    tiers = _split_csv_arg(args.tiers)
    families = _split_csv_arg(args.families)
    model_ids = _split_csv_arg(args.model_ids)
    filtered = _filter_specs(payload, tiers=tiers, families=families, model_ids=model_ids)

    bundle_name = args.bundle_name.strip()
    if not bundle_name:
        parts: list[str] = []
        if families:
            parts.append("families_" + "_".join(sorted(_slugify(f) for f in families)))
        if model_ids:
            parts.append("models_" + "_".join(sorted(_slugify(m) for m in model_ids)))
        if tiers != {"baseline", "robustness", "appendix"}:
            parts.append("tiers_" + "_".join(sorted(_slugify(t) for t in tiers)))
        bundle_name = "_".join(parts) if parts else DEFAULT_BUNDLE_NAME
    bundle_name = _slugify(bundle_name)

    outdir = Path(args.outdir) / bundle_name
    outdir.mkdir(parents=True, exist_ok=True)
    filtered_spec_path = outdir / "filtered_portfolio_spec.json"
    filtered_spec_path.write_text(json.dumps(filtered, indent=2), encoding="utf-8")

    run_args = SimpleNamespace(
        panel=args.panel,
        spec_path=str(filtered_spec_path),
        outdir=str(outdir),
        tiers="baseline,robustness,appendix",
    )
    run_portfolio(run_args)

    print(f"[modular-portfolio] wrote bundle to {outdir}")


def main() -> None:
    args = parse_args()
    run_modular_portfolio(args)


if __name__ == "__main__":
    main()
