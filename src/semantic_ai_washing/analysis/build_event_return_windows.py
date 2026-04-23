"""Build filing-level daily event-return windows from WRDS CRSP daily returns."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import pandas as pd
import psycopg2

DEFAULT_BRIDGE = "data/interim/market/filing_wrds_bridge_v1.csv"
DEFAULT_OUTPUT = "data/interim/market/filing_event_returns_daily_v1.parquet"
DEFAULT_REPORT = "reports/analysis/filing_event_returns_daily_v1.json"
DEFAULT_DOTENV = ".env"
DEFAULT_PRE_DAYS = 2
DEFAULT_POST_DAYS = 252
MATCHED_STATUSES = {"matched", "matched_via_ccm_lookup_fallback"}
WINDOW_DEFINITIONS = {
    "car_m1_p1": (-1, 1),
    "car_m2_p2": (-2, 2),
    "bhar_1m": (0, 21),
    "bhar_3m": (0, 63),
    "bhar_6m": (0, 126),
    "bhar_12m": (0, 252),
}

OUTPUT_COLUMNS = [
    "filing_id",
    "source_filename",
    "cik",
    "gvkey",
    "permno",
    "permco",
    "filing_date",
    "anchor_trading_date",
    "anchor_calendar_shift_days",
    "wrds_bridge_status",
    "trade_date",
    "relative_day",
    "ret",
    "retx",
    "vwretd",
    "ewretd",
    "sprtrn",
    "abnormal_ret_vw",
    "abnormal_ret_ew",
    "prc",
    "shrout",
    "vol",
]


@dataclass(frozen=True)
class FilingBridgeRow:
    filing_id: str
    source_filename: str
    cik: str
    gvkey: str
    permno: str
    permco: str
    filing_date: str
    wrds_bridge_status: str


@dataclass(frozen=True)
class WindowCoverage:
    available_rows: int
    expected_rows: int
    is_complete: bool


def normalize_permno(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    try:
        numeric = float(text)
    except ValueError:
        return text
    if math.isnan(numeric):
        return ""
    return str(int(numeric))


def parse_yyyymmdd(value: str) -> date:
    return datetime.strptime(str(value), "%Y%m%d").date()


def load_bridge_rows(path: str | Path) -> list[FilingBridgeRow]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[FilingBridgeRow] = []
        for row in reader:
            status = str(row.get("wrds_bridge_status", "") or "").strip()
            if status not in MATCHED_STATUSES:
                continue
            permno = normalize_permno(row.get("permno", ""))
            permco = normalize_permno(row.get("permco", ""))
            if not permno:
                continue
            rows.append(
                FilingBridgeRow(
                    filing_id=str(row.get("filing_id", "") or "").strip(),
                    source_filename=str(row.get("source_filename", "") or "").strip(),
                    cik=str(row.get("cik", "") or "").strip(),
                    gvkey=str(row.get("gvkey", "") or "").strip(),
                    permno=permno,
                    permco=permco,
                    filing_date=str(row.get("filing_date", "") or "").strip(),
                    wrds_bridge_status=status,
                )
            )
    return rows


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


def fetch_crsp_daily_returns(
    permnos: list[str],
    *,
    start_date: date,
    end_date: date,
    dotenv_path: str | Path,
    batch_size: int | None = None,
) -> pd.DataFrame:
    if not permnos:
        return pd.DataFrame(
            columns=["permno", "trade_date", "ret", "retx", "prc", "shrout", "vol"]
        )
    conn = _connect_wrds(dotenv_path)
    try:
        query = """
            select
                permno,
                date,
                ret,
                retx,
                prc,
                shrout,
                vol
            from crsp.dsf
            where permno = any(%s)
              and date between %s and %s
            order by permno, date
        """
        parsed_permnos = [int(value) for value in permnos]
        effective_batch_size = batch_size or len(parsed_permnos)
        frames: list[pd.DataFrame] = []
        for start_idx in range(0, len(parsed_permnos), effective_batch_size):
            batch = parsed_permnos[start_idx : start_idx + effective_batch_size]
            params = (batch, start_date.isoformat(), end_date.isoformat())
            print(
                "[event-returns] fetching CRSP daily "
                f"permnos={start_idx + 1}-{start_idx + len(batch)} "
                f"of {len(parsed_permnos)}",
                flush=True,
            )
            frames.append(pd.read_sql(query, conn, params=params))
        df = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    finally:
        conn.close()

    if df.empty:
        return pd.DataFrame(
            columns=["permno", "trade_date", "ret", "retx", "prc", "shrout", "vol"]
        )

    df = df.rename(columns={"date": "trade_date"})
    df["permno"] = df["permno"].astype("Int64").astype(str)
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
    return df


def fetch_crsp_market_index(
    *,
    start_date: date,
    end_date: date,
    dotenv_path: str | Path,
) -> pd.DataFrame:
    conn = _connect_wrds(dotenv_path)
    try:
        query = """
            select
                date,
                vwretd,
                ewretd,
                sprtrn
            from crsp.dsi
            where date between %s and %s
            order by date
        """
        df = pd.read_sql(query, conn, params=(start_date.isoformat(), end_date.isoformat()))
    finally:
        conn.close()

    if df.empty:
        return pd.DataFrame(columns=["trade_date", "vwretd", "ewretd", "sprtrn"])

    df = df.rename(columns={"date": "trade_date"})
    df["trade_date"] = pd.to_datetime(df["trade_date"]).dt.date
    return df


def choose_anchor_index(trade_dates: list[date], filing_date: date) -> int | None:
    for idx, trade_date in enumerate(trade_dates):
        if trade_date >= filing_date:
            return idx
    return None


def summarize_window_coverage(
    relative_days: list[int], start_day: int, end_day: int
) -> WindowCoverage:
    expected_rows = end_day - start_day + 1
    observed = {day for day in relative_days if start_day <= day <= end_day}
    return WindowCoverage(
        available_rows=len(observed),
        expected_rows=expected_rows,
        is_complete=len(observed) == expected_rows,
    )


def build_event_return_windows(
    bridge_path: str = DEFAULT_BRIDGE,
    *,
    dotenv_path: str = DEFAULT_DOTENV,
    pre_days: int = DEFAULT_PRE_DAYS,
    post_days: int = DEFAULT_POST_DAYS,
    permno_batch_size: int | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    bridge_rows = load_bridge_rows(bridge_path)
    if not bridge_rows:
        report = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "bridge_path": str(Path(bridge_path).resolve()),
            "row_count": 0,
            "matched_filing_count": 0,
            "daily_return_row_count": 0,
        }
        return pd.DataFrame(columns=OUTPUT_COLUMNS), report

    filing_dates = [parse_yyyymmdd(row.filing_date) for row in bridge_rows]
    query_start = min(filing_dates) - timedelta(days=10)
    query_end = max(filing_dates) + timedelta(days=max(370, post_days + 30))
    permnos = sorted({row.permno for row in bridge_rows})

    returns_df = fetch_crsp_daily_returns(
        permnos,
        start_date=query_start,
        end_date=query_end,
        dotenv_path=dotenv_path,
        batch_size=permno_batch_size,
    )
    market_df = fetch_crsp_market_index(
        start_date=query_start,
        end_date=query_end,
        dotenv_path=dotenv_path,
    )

    merged_returns = returns_df.merge(market_df, on="trade_date", how="left")
    permno_groups = {
        permno: group.sort_values("trade_date").reset_index(drop=True)
        for permno, group in merged_returns.groupby("permno", sort=False)
    }

    event_rows: list[dict[str, Any]] = []
    no_anchor_count = 0
    shifted_anchor_count = 0
    exact_anchor_count = 0
    complete_counts = {name: 0 for name in WINDOW_DEFINITIONS}

    for filing in bridge_rows:
        permno_df = permno_groups.get(filing.permno)
        if permno_df is None or permno_df.empty:
            no_anchor_count += 1
            continue
        trade_dates = permno_df["trade_date"].tolist()
        filing_dt = parse_yyyymmdd(filing.filing_date)
        anchor_index = choose_anchor_index(trade_dates, filing_dt)
        if anchor_index is None:
            no_anchor_count += 1
            continue

        anchor_date = trade_dates[anchor_index]
        if anchor_date == filing_dt:
            exact_anchor_count += 1
        else:
            shifted_anchor_count += 1

        start_idx = max(0, anchor_index - pre_days)
        end_idx = min(len(permno_df) - 1, anchor_index + post_days)
        window_df = permno_df.iloc[start_idx : end_idx + 1].copy()
        window_df["relative_day"] = [idx - anchor_index for idx in range(start_idx, end_idx + 1)]

        relative_days = window_df["relative_day"].tolist()
        for name, (start_day, end_day) in WINDOW_DEFINITIONS.items():
            coverage = summarize_window_coverage(relative_days, start_day, end_day)
            if coverage.is_complete:
                complete_counts[name] += 1

        for _, row in window_df.iterrows():
            ret = row.get("ret")
            vwretd = row.get("vwretd")
            ewretd = row.get("ewretd")
            abnormal_ret_vw = (ret - vwretd) if pd.notna(ret) and pd.notna(vwretd) else pd.NA
            abnormal_ret_ew = (ret - ewretd) if pd.notna(ret) and pd.notna(ewretd) else pd.NA
            event_rows.append(
                {
                    "filing_id": filing.filing_id,
                    "source_filename": filing.source_filename,
                    "cik": filing.cik,
                    "gvkey": filing.gvkey,
                    "permno": filing.permno,
                    "permco": filing.permco,
                    "filing_date": filing.filing_date,
                    "anchor_trading_date": anchor_date.isoformat(),
                    "anchor_calendar_shift_days": (anchor_date - filing_dt).days,
                    "wrds_bridge_status": filing.wrds_bridge_status,
                    "trade_date": row["trade_date"].isoformat(),
                    "relative_day": int(row["relative_day"]),
                    "ret": ret,
                    "retx": row.get("retx"),
                    "vwretd": vwretd,
                    "ewretd": ewretd,
                    "sprtrn": row.get("sprtrn"),
                    "abnormal_ret_vw": abnormal_ret_vw,
                    "abnormal_ret_ew": abnormal_ret_ew,
                    "prc": row.get("prc"),
                    "shrout": row.get("shrout"),
                    "vol": row.get("vol"),
                }
            )

    output_df = pd.DataFrame(event_rows, columns=OUTPUT_COLUMNS)
    if not output_df.empty:
        numeric_cols = [
            "ret",
            "retx",
            "vwretd",
            "ewretd",
            "sprtrn",
            "abnormal_ret_vw",
            "abnormal_ret_ew",
            "prc",
            "shrout",
            "vol",
        ]
        for column in numeric_cols:
            output_df[column] = pd.to_numeric(output_df[column], errors="coerce")
        output_df["relative_day"] = output_df["relative_day"].astype(int)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "bridge_path": str(Path(bridge_path).resolve()),
        "dotenv_path": str(Path(dotenv_path).resolve()),
        "query_start": query_start.isoformat(),
        "query_end": query_end.isoformat(),
        "matched_filing_count": len(bridge_rows),
        "unique_permno_count": len(permnos),
        "permno_batch_size": permno_batch_size,
        "daily_return_row_count": int(len(output_df)),
        "no_anchor_count": no_anchor_count,
        "exact_anchor_count": exact_anchor_count,
        "shifted_anchor_count": shifted_anchor_count,
        "complete_window_counts": complete_counts,
        "window_definitions": {
            key: {"start_day": start, "end_day": end}
            for key, (start, end) in WINDOW_DEFINITIONS.items()
        },
    }
    return output_df, report


def write_event_returns(df: pd.DataFrame, output_path: str | Path) -> None:
    resolved = Path(output_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(resolved, index=False)


def write_report(report: dict[str, Any], report_path: str | Path) -> None:
    resolved = Path(report_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge", default=DEFAULT_BRIDGE)
    parser.add_argument("--dotenv", default=DEFAULT_DOTENV)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--pre-days", type=int, default=DEFAULT_PRE_DAYS)
    parser.add_argument("--post-days", type=int, default=DEFAULT_POST_DAYS)
    parser.add_argument("--permno-batch-size", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    df, report = build_event_return_windows(
        bridge_path=args.bridge,
        dotenv_path=args.dotenv,
        pre_days=args.pre_days,
        post_days=args.post_days,
        permno_batch_size=args.permno_batch_size or None,
    )
    write_event_returns(df, args.output)
    write_report(report, args.report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
