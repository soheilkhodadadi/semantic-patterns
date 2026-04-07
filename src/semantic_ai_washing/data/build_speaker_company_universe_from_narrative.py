"""Build a speaker-firm universe from one or more narrative-measure tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def normalize_cik(value: object) -> str:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return digits.zfill(10) if digits else ""


def _load_narrative_table(path: str | Path) -> pd.DataFrame:
    table_path = Path(path)
    if not table_path.exists():
        raise FileNotFoundError(f"Missing narrative table: {table_path}")

    if table_path.suffix == ".parquet":
        frame = pd.read_parquet(table_path)
    else:
        frame = pd.read_csv(table_path)

    required = {"source_cik", "source_year"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Narrative table missing required columns {sorted(missing)}: {table_path}")
    return frame


def build_speaker_company_universe(
    narrative_paths: list[str | Path],
    *,
    output_csv: str | Path,
    output_report: str | Path | None = None,
    min_year: int | None = None,
    max_year: int | None = None,
) -> dict[str, object]:
    if not narrative_paths:
        raise ValueError("At least one narrative table is required.")

    frames = [_load_narrative_table(path) for path in narrative_paths]
    combined = pd.concat(frames, ignore_index=True)
    combined["cik"] = combined["source_cik"].apply(normalize_cik)
    combined["year"] = pd.to_numeric(combined["source_year"], errors="coerce").astype("Int64")
    combined = combined[combined["cik"] != ""].copy()
    combined = combined.dropna(subset=["year"]).copy()
    combined["year"] = combined["year"].astype(int)

    if min_year is not None:
        combined = combined[combined["year"] >= int(min_year)].copy()
    if max_year is not None:
        combined = combined[combined["year"] <= int(max_year)].copy()

    combined = combined.drop_duplicates(subset=["cik", "year"]).copy()
    if combined.empty:
        raise ValueError("No speaker firm-years remain after filtering.")

    years = sorted(int(year) for year in combined["year"].unique())
    grouped = (
        combined.groupby("cik", as_index=False)["year"]
        .agg(lambda series: sorted({int(value) for value in series.tolist()}))
        .rename(columns={"year": "years_present"})
    )
    grouped["years_present_count"] = grouped["years_present"].apply(len)
    for year in years:
        grouped[f"year_{year}_present"] = grouped["years_present"].apply(lambda values: year in values)
    grouped["years_present"] = grouped["years_present"].apply(
        lambda values: ",".join(str(value) for value in values)
    )
    grouped = grouped.sort_values("cik").reset_index(drop=True)

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(output_path, index=False)

    summary: dict[str, object] = {
        "status": "passed",
        "input_paths": [str(Path(path)) for path in narrative_paths],
        "rows_input_combined": int(len(combined)),
        "firm_count": int(len(grouped)),
        "year_span": [int(years[0]), int(years[-1])],
        "years_covered": years,
        "output_csv": str(output_path),
    }
    if output_report is not None:
        report_path = Path(output_report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        summary["output_report"] = str(report_path)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--narrative",
        dest="narrative_paths",
        nargs="+",
        required=True,
        help="One or more narrative table paths (csv or parquet).",
    )
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-report", default="")
    parser.add_argument("--min-year", type=int, default=None)
    parser.add_argument("--max-year", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = build_speaker_company_universe(
        args.narrative_paths,
        output_csv=args.output_csv,
        output_report=args.output_report or None,
        min_year=args.min_year,
        max_year=args.max_year,
    )
    print(
        "[speaker-universe] firms={firm_count} firm_years={rows_input_combined} "
        "years={year_span} output={output_csv}".format(**summary)
    )


if __name__ == "__main__":
    main()
