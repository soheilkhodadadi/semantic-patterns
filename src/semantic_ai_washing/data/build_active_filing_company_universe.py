"""
Build a broader firm-universe CSV from the indexed active filing window.

The output is intentionally simple so it can drive downstream WRDS controls pulls
without requiring an external name/ticker map first.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def normalize_cik(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.extract(r"(\d+)", expand=False)
        .fillna("")
        .str.zfill(10)
        .replace("0000000000", "")
    )


def build_universe(
    index_csv: str,
    output_csv: str,
    source_window_id: str = "active_2021_2024",
    years: list[int] | None = None,
    forms: list[str] | None = None,
    require_all_years: bool = False,
) -> dict:
    years = years or [2021, 2022, 2023, 2024]
    forms = forms or ["10-K", "10-K-A"]

    df = pd.read_csv(index_csv)
    df.columns = df.columns.str.strip().str.lower()
    required = {"cik", "year", "form"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Index is missing required columns: {sorted(missing)}")

    df["cik"] = normalize_cik(df["cik"])
    df["form"] = df["form"].astype(str).str.upper().str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")

    df = df[df["cik"] != ""].copy()
    df = df[df["year"].isin(years)].copy()
    df = df[df["form"].isin([f.upper() for f in forms])].copy()

    if source_window_id and "source_window_id" in df.columns:
        df = df[df["source_window_id"] == source_window_id].copy()

    firm_years = df.groupby("cik")["year"].agg(lambda s: sorted(set(int(v) for v in s.dropna())))
    annual_counts = df.groupby("cik").size().rename("annual_filing_count")
    universe = firm_years.to_frame("years_present").join(annual_counts, how="left").reset_index()

    for year in years:
        universe[f"year_{year}_present"] = universe["years_present"].apply(
            lambda vals: year in vals
        )
    universe["years_present_count"] = universe["years_present"].apply(len)
    universe["years_present"] = universe["years_present"].apply(
        lambda vals: ",".join(str(v) for v in vals)
    )

    if require_all_years:
        universe = universe[universe["years_present_count"] == len(years)].copy()

    universe = universe.sort_values("cik").reset_index(drop=True)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    universe.to_csv(output_path, index=False)

    summary = {
        "rows_index_filtered": int(len(df)),
        "firm_count": int(len(universe)),
        "years": years,
        "forms": [f.upper() for f in forms],
        "require_all_years": require_all_years,
        "output_csv": str(output_path),
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index-csv", default="data/metadata/available_filings_index.csv")
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--source-window-id", default="active_2021_2024")
    parser.add_argument("--years", type=int, nargs="+", default=[2021, 2022, 2023, 2024])
    parser.add_argument("--forms", nargs="+", default=["10-K", "10-K-A"])
    parser.add_argument("--require-all-years", action="store_true")
    args = parser.parse_args()

    summary = build_universe(
        index_csv=args.index_csv,
        output_csv=args.output_csv,
        source_window_id=args.source_window_id,
        years=args.years,
        forms=args.forms,
        require_all_years=args.require_all_years,
    )
    print(
        "[active-universe] firms={firm_count} filtered_rows={rows_index_filtered} output={output_csv}".format(
            **summary
        )
    )


if __name__ == "__main__":
    main()
