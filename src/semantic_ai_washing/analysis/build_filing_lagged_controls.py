"""Attach latest prior annual Compustat controls to each filing event row."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import math
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import pandas as pd
import psycopg2

DEFAULT_EVENT_PANEL = "data/processed/panel/filing_event_panel_v1.parquet"
DEFAULT_OUTPUT = "data/interim/market/filing_lagged_controls_v1.csv"
DEFAULT_REPORT = "reports/analysis/filing_lagged_controls_v1.json"
DEFAULT_DOTENV = ".env"

OUTPUT_COLUMNS = [
    "filing_id",
    "gvkey",
    "filing_date",
    "control_datadate",
    "control_fyear",
    "control_age_days",
    "at",
    "sale",
    "ib",
    "ni",
    "che",
    "dltt",
    "dlc",
    "capx",
    "xrd",
    "emp",
    "ln_assets",
    "leverage",
    "cash",
    "rd_intensity",
    "capx_at",
    "roa",
    "sales_growth",
]


@dataclass(frozen=True)
class FilingKey:
    filing_id: str
    gvkey: str
    filing_date: str


def _normalize_string_key(series: pd.Series, *, zero_fill: int | None = None) -> pd.Series:
    normalized = series.fillna("").astype(str).str.strip()
    if zero_fill is not None:
        normalized = normalized.str.replace(r"\.0$", "", regex=True)
        normalized = normalized.str.zfill(zero_fill)
    return normalized


def load_credentials(dotenv_path: str | Path) -> dict[str, str]:
    load_dotenv(dotenv_path, override=False)
    return {
        "user": os.getenv("WRDS_USER", ""),
        "password": os.getenv("WRDS_PASS", ""),
        "host": os.getenv("WRDS_DB_HOST", ""),
        "port": os.getenv("WRDS_DB_PORT", ""),
    }


def _connect_wrds(dotenv_path: str | Path) -> psycopg2.extensions.connection:
    creds = load_credentials(dotenv_path)
    if not all(creds.values()):
        raise RuntimeError("WRDS credentials are missing from the environment/.env")
    return psycopg2.connect(
        dbname="wrds",
        user=creds["user"],
        password=creds["password"],
        host=creds["host"],
        port=int(creds["port"]),
        connect_timeout=15,
    )


def load_event_panel(path: str | Path) -> pd.DataFrame:
    panel = pd.read_parquet(path)
    panel["filing_id"] = _normalize_string_key(panel["filing_id"])
    panel["gvkey"] = _normalize_string_key(panel["gvkey"])
    panel["filing_date"] = _normalize_string_key(panel["filing_date"])
    return panel


def fetch_compustat_controls(
    gvkeys: list[str],
    *,
    max_filing_date: date,
    dotenv_path: str | Path,
) -> pd.DataFrame:
    if not gvkeys:
        return pd.DataFrame()
    conn = _connect_wrds(dotenv_path)
    try:
        query = """
            select
                gvkey,
                datadate,
                fyear,
                fyr,
                at,
                sale,
                ib,
                ni,
                che,
                dltt,
                dlc,
                capx,
                xrd,
                emp
            from comp.funda
            where gvkey = any(%s)
              and indfmt = 'INDL'
              and consol = 'C'
              and datafmt = 'STD'
              and popsrc = 'D'
              and datadate <= %s
            order by gvkey, datadate
        """
        df = pd.read_sql(query, conn, params=(gvkeys, max_filing_date.isoformat()))
    finally:
        conn.close()

    if df.empty:
        return df

    df["gvkey"] = _normalize_string_key(df["gvkey"])
    df["datadate"] = pd.to_datetime(df["datadate"]).dt.date
    df = df.sort_values(["gvkey", "datadate"]).reset_index(drop=True)
    df["sales_growth"] = df.groupby("gvkey", sort=False)["sale"].pct_change(fill_method=None)
    return df


def _ratio(numerator: Any, denominator: Any) -> float | None:
    if pd.isna(numerator) or pd.isna(denominator):
        return None
    try:
        denominator_float = float(denominator)
        numerator_float = float(numerator)
    except (TypeError, ValueError):
        return None
    if denominator_float == 0:
        return None
    return numerator_float / denominator_float


def derive_controls(record: pd.Series) -> dict[str, Any]:
    at = record.get("at")
    sale = record.get("sale")
    ib = record.get("ib")
    ni = record.get("ni")
    che = record.get("che")
    dltt = record.get("dltt")
    dlc = record.get("dlc")
    capx = record.get("capx")
    xrd = record.get("xrd")

    debt_total = None
    if pd.notna(dltt) or pd.notna(dlc):
        debt_total = (0.0 if pd.isna(dltt) else float(dltt)) + (
            0.0 if pd.isna(dlc) else float(dlc)
        )

    roa_base = ib if pd.notna(ib) else ni
    ln_assets = None
    if pd.notna(at):
        at_float = float(at)
        if at_float > 0:
            ln_assets = math.log(at_float)

    return {
        "ln_assets": ln_assets,
        "leverage": _ratio(debt_total, at),
        "cash": _ratio(che, at),
        "rd_intensity": _ratio(xrd, sale),
        "capx_at": _ratio(capx, at),
        "roa": _ratio(roa_base, at),
        "sales_growth": None
        if pd.isna(record.get("sales_growth"))
        else float(record.get("sales_growth")),
    }


def choose_latest_prior_control(controls: pd.DataFrame, filing_date: date) -> pd.Series | None:
    if controls.empty or "datadate" not in controls.columns:
        return None
    eligible = controls[controls["datadate"] <= filing_date]
    if eligible.empty:
        return None
    return eligible.iloc[-1]


def build_filing_lagged_controls(
    event_panel_path: str = DEFAULT_EVENT_PANEL,
    *,
    dotenv_path: str = DEFAULT_DOTENV,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    event_panel = load_event_panel(event_panel_path)
    keys = event_panel[["filing_id", "gvkey", "filing_date"]].drop_duplicates().copy()
    keys = keys[keys["gvkey"] != ""].reset_index(drop=True)
    filing_dates = pd.to_datetime(keys["filing_date"], format="%Y%m%d").dt.date
    controls_raw = fetch_compustat_controls(
        sorted(keys["gvkey"].unique().tolist()),
        max_filing_date=max(filing_dates),
        dotenv_path=dotenv_path,
    )

    grouped_controls = {
        gvkey: group.reset_index(drop=True)
        for gvkey, group in controls_raw.groupby("gvkey", sort=False)
    }

    rows: list[dict[str, Any]] = []
    matched_count = 0
    for filing in keys.itertuples(index=False):
        filing_dt = datetime.strptime(filing.filing_date, "%Y%m%d").date()
        control_row = choose_latest_prior_control(
            grouped_controls.get(filing.gvkey, pd.DataFrame()), filing_dt
        )
        row = {
            "filing_id": filing.filing_id,
            "gvkey": filing.gvkey,
            "filing_date": filing.filing_date,
            "control_datadate": "",
            "control_fyear": pd.NA,
            "control_age_days": pd.NA,
            "at": pd.NA,
            "sale": pd.NA,
            "ib": pd.NA,
            "ni": pd.NA,
            "che": pd.NA,
            "dltt": pd.NA,
            "dlc": pd.NA,
            "capx": pd.NA,
            "xrd": pd.NA,
            "emp": pd.NA,
            "ln_assets": pd.NA,
            "leverage": pd.NA,
            "cash": pd.NA,
            "rd_intensity": pd.NA,
            "capx_at": pd.NA,
            "roa": pd.NA,
            "sales_growth": pd.NA,
        }
        if control_row is not None:
            matched_count += 1
            derived = derive_controls(control_row)
            row.update(
                {
                    "control_datadate": control_row["datadate"].isoformat(),
                    "control_fyear": control_row.get("fyear"),
                    "control_age_days": (filing_dt - control_row["datadate"]).days,
                    "at": control_row.get("at"),
                    "sale": control_row.get("sale"),
                    "ib": control_row.get("ib"),
                    "ni": control_row.get("ni"),
                    "che": control_row.get("che"),
                    "dltt": control_row.get("dltt"),
                    "dlc": control_row.get("dlc"),
                    "capx": control_row.get("capx"),
                    "xrd": control_row.get("xrd"),
                    "emp": control_row.get("emp"),
                    **derived,
                }
            )
        rows.append(row)

    controls_df = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "event_panel_path": str(Path(event_panel_path).resolve()),
        "dotenv_path": str(Path(dotenv_path).resolve()),
        "row_count": int(len(controls_df)),
        "matched_control_rows": matched_count,
        "match_rate": round(matched_count / len(controls_df), 4) if len(controls_df) else 0.0,
        "control_age_days_summary": {
            "min": None
            if controls_df["control_age_days"].dropna().empty
            else int(controls_df["control_age_days"].dropna().min()),
            "median": None
            if controls_df["control_age_days"].dropna().empty
            else float(controls_df["control_age_days"].dropna().median()),
            "max": None
            if controls_df["control_age_days"].dropna().empty
            else int(controls_df["control_age_days"].dropna().max()),
        },
        "nonmissing_counts": {
            column: int(controls_df[column].notna().sum())
            for column in [
                "ln_assets",
                "leverage",
                "cash",
                "rd_intensity",
                "capx_at",
                "roa",
                "sales_growth",
            ]
        },
    }
    return controls_df, report


def write_controls(df: pd.DataFrame, output_path: str | Path) -> None:
    resolved = Path(output_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(resolved, index=False)


def write_report(report: dict[str, Any], report_path: str | Path) -> None:
    resolved = Path(report_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event-panel", default=DEFAULT_EVENT_PANEL)
    parser.add_argument("--dotenv", default=DEFAULT_DOTENV)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    controls_df, report = build_filing_lagged_controls(
        event_panel_path=args.event_panel,
        dotenv_path=args.dotenv,
    )
    write_controls(controls_df, args.output)
    write_report(report, args.report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
