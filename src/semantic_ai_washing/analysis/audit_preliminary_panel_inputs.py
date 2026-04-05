"""Audit patents and controls coverage before preliminary panel assembly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.classification.preliminary_pipeline import sha256_file
from ai_washing_member.labeling.common import load_table

ACTIVE_YEARS = {2021, 2022, 2023, 2024}


def _normalize_cik(value: Any) -> str:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return digits.zfill(10) if digits else ""


def _source_mode(paths: list[str]) -> str:
    lowered = [Path(path).name.lower() for path in paths if str(path).strip()]
    if any("sample" in name for name in lowered):
        return "sample"
    if any("external_full" in name or "full" in name for name in lowered):
        return "external_full"
    return "full"


def _load_panel_universe(path: str | Path) -> pd.DataFrame:
    frame = load_table(path)
    required = {"source_cik", "source_year"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Narrative measures file missing columns: {missing}")
    universe = frame[["source_cik", "source_year"]].drop_duplicates().copy()
    universe["source_cik"] = universe["source_cik"].map(_normalize_cik)
    universe["source_year"] = universe["source_year"].astype(int)
    return universe


def _load_input_table(path: str | Path, cik_column: str, year_column: str) -> pd.DataFrame:
    frame = load_table(path)
    required = {cik_column, year_column}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Input table missing columns: {missing}")
    subset = frame[[cik_column, year_column]].drop_duplicates().copy()
    subset["cik"] = subset[cik_column].map(_normalize_cik)
    subset["year"] = pd.to_numeric(subset[year_column], errors="coerce").fillna(0).astype(int)
    subset = subset[(subset["cik"] != "") & (subset["year"] > 0)].copy()
    return subset[["cik", "year"]]


def _coverage_summary(frame: pd.DataFrame, universe: pd.DataFrame) -> dict[str, Any]:
    years = sorted({int(year) for year in frame["year"].unique() if int(year) in ACTIVE_YEARS})
    firms = int(frame["cik"].nunique())
    rows = int(len(frame))
    merged = universe.rename(columns={"source_cik": "cik", "source_year": "year"}).merge(
        frame,
        on=["cik", "year"],
        how="left",
        indicator=True,
    )
    matched = int((merged["_merge"] == "both").sum())
    universe_rows = int(len(universe))
    coverage_share = float(matched / universe_rows) if universe_rows else 0.0
    return {
        "year_coverage": years,
        "unique_firms": firms,
        "row_count": rows,
        "matched_universe_rows": matched,
        "universe_rows": universe_rows,
        "active_window_coverage_share": round(coverage_share, 6),
    }


def run_audit(args: argparse.Namespace) -> dict[str, Any]:
    output_path = Path(args.output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    universe = _load_panel_universe(args.narrative_measures)
    controls_paths = [args.controls, *args.raw_controls]
    patents_paths = [args.patents, *args.raw_patents]
    controls_mode = _source_mode(controls_paths)
    patents_mode = _source_mode(patents_paths)

    controls_frame = _load_input_table(
        args.controls, args.controls_cik_column, args.controls_year_column
    )
    patents_frame = _load_input_table(
        args.patents, args.patents_cik_column, args.patents_year_column
    )

    controls_summary = _coverage_summary(controls_frame, universe)
    patents_summary = _coverage_summary(patents_frame, universe)

    failure_reasons: list[str] = []
    if controls_mode == "sample":
        failure_reasons.append("controls_source_mode_sample")
    if patents_mode == "sample":
        failure_reasons.append("patents_source_mode_sample")
    if set(controls_summary["year_coverage"]) != ACTIVE_YEARS:
        failure_reasons.append("controls_missing_active_window_years")
    if set(patents_summary["year_coverage"]) != ACTIVE_YEARS:
        failure_reasons.append("patents_missing_active_window_years")

    status = "ready" if not failure_reasons else "blocked_refresh_required"
    report = {
        "status": status,
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": {
            "status": status,
            "source_window_id": str(args.source_window_id),
            "failure_reasons": failure_reasons,
            "controls_source_mode": controls_mode,
            "patents_source_mode": patents_mode,
            "controls_year_coverage": controls_summary["year_coverage"],
            "patents_year_coverage": patents_summary["year_coverage"],
        },
        "controls": {
            "source_paths": controls_paths,
            "source_mode": controls_mode,
            "processed_path": str(args.controls),
            "processed_sha256": sha256_file(args.controls),
            **controls_summary,
        },
        "patents": {
            "source_paths": patents_paths,
            "source_mode": patents_mode,
            "processed_path": str(args.patents),
            "processed_sha256": sha256_file(args.patents),
            **patents_summary,
        },
        "crosswalk": {
            "path": str(args.crosswalk),
            "sha256": sha256_file(args.crosswalk),
            "exists": Path(args.crosswalk).exists(),
        },
        "narrative_measures": {
            "path": str(args.narrative_measures),
            "sha256": sha256_file(args.narrative_measures),
            "rows": int(len(universe)),
            "unique_firms": int(universe["source_cik"].nunique()),
            "year_coverage": sorted({int(year) for year in universe["source_year"].unique()}),
        },
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", default="data/interim/controls/controls_by_firm_year.csv")
    parser.add_argument(
        "--patents", default="data/processed/patents/ai_patent_counts_filtered_2019plus.csv"
    )
    parser.add_argument("--crosswalk", default="data/externals/crosswalks/cik_gvkey.csv")
    parser.add_argument(
        "--narrative-measures",
        default="data/processed/aggregates/firm_year_narrative_measures_prelim_v1.parquet",
    )
    parser.add_argument(
        "--raw-controls", nargs="*", default=["data/raw/compustat/compustat_sample.csv"]
    )
    parser.add_argument(
        "--raw-patents", nargs="*", default=["data/raw/patents/sample_patents.csv"]
    )
    parser.add_argument("--controls-cik-column", default="cik")
    parser.add_argument("--controls-year-column", default="year")
    parser.add_argument("--patents-cik-column", default="cik")
    parser.add_argument("--patents-year-column", default="year")
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument(
        "--output-report", default="reports/panels/preliminary_inputs_manifest_v1.json"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_audit(args)
    print(
        "[prelim-panel-inputs] audited "
        f"status={report['status']} failure_reasons={report['summary']['failure_reasons']}"
    )
    print(f"[prelim-panel-inputs] report -> {args.output_report}")


if __name__ == "__main__":
    main()
