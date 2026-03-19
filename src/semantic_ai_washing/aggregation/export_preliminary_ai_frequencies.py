"""Export clean preliminary firm-year AI metrics into the legacy CSV merge shape."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def run_export(args: argparse.Namespace) -> Path:
    input_path = Path(args.input_parquet)
    output_path = Path(args.output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(input_path).copy()
    required = {"source_cik", "source_year", "doc_count", "n_A", "n_S", "n_I", "n_total", "ai_total"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"AI metrics parquet missing columns: {missing}")

    if args.years:
        years = {int(year) for year in args.years}
        df = df.loc[df["source_year"].astype(int).isin(years)].copy()

    df["cik"] = df["source_cik"].astype(str).str.extract(r"(\d+)")[0].fillna("").str.zfill(10)
    df["year"] = df["source_year"].astype(int)

    denom = df["n_total"].replace(0, pd.NA)
    df["share_A"] = (df["n_A"] / denom).fillna(0.0)
    df["share_S"] = (df["n_S"] / denom).fillna(0.0)
    df["share_I"] = (df["n_I"] / denom).fillna(0.0)

    exported = df[
        [
            "cik",
            "year",
            "doc_count",
            "n_total",
            "n_A",
            "n_S",
            "n_I",
            "ai_total",
            "share_A",
            "share_S",
            "share_I",
        ]
    ].sort_values(["cik", "year"])

    exported.to_csv(output_path, index=False)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-parquet",
        default="data/processed/aggregates/firm_year_ai_metrics_prelim_clean_v1.parquet",
    )
    parser.add_argument(
        "--output-csv",
        default="data/processed/aggregates/ai_frequencies_prelim_clean_v1.csv",
    )
    parser.add_argument("--years", nargs="*", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = run_export(args)
    print(f"[prelim-ai-export] wrote {path}")


if __name__ == "__main__":
    main()
