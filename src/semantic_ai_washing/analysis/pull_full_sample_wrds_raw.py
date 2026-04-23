"""Pull broad-sample raw WRDS fundamentals and monthly CRSP data for the refresh backbone."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg2

from semantic_ai_washing.analysis.build_filing_lagged_controls import load_credentials

DEFAULT_BACKBONE = "data/interim/market/full_sample_wrds_backbone_v1.csv"
DEFAULT_FUNDA_OUTPUT = "data/interim/market/wrds_comp_funda_full_sample_v1.parquet"
DEFAULT_MSF_OUTPUT = "data/interim/market/wrds_crsp_msf_full_sample_v1.parquet"
DEFAULT_MSI_OUTPUT = "data/interim/market/wrds_crsp_msi_full_sample_v1.parquet"
DEFAULT_REPORT = "reports/analysis/wrds_full_sample_raw_pull_v1.json"
DEFAULT_DOTENV = ".env"
DEFAULT_GVKEY_CHUNK = 500
DEFAULT_PERMNO_CHUNK = 500


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backbone", default=DEFAULT_BACKBONE)
    parser.add_argument("--funda-output", default=DEFAULT_FUNDA_OUTPUT)
    parser.add_argument("--msf-output", default=DEFAULT_MSF_OUTPUT)
    parser.add_argument("--msi-output", default=DEFAULT_MSI_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--dotenv", default=DEFAULT_DOTENV)
    parser.add_argument("--gvkey-chunk", type=int, default=DEFAULT_GVKEY_CHUNK)
    parser.add_argument("--permno-chunk", type=int, default=DEFAULT_PERMNO_CHUNK)
    return parser.parse_args()


def _ensure_parent(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


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


def load_backbone(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"cik": str, "gvkey": str, "permno": str, "permco": str})
    df["cik"] = df["cik"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(10)
    df["gvkey"] = df["gvkey"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    df["permno"] = df["permno"].fillna("").astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


def _chunk(values: list[str], size: int) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def fetch_compustat_funda(
    gvkeys: list[str],
    *,
    start_date: date,
    end_date: date,
    dotenv_path: str | Path,
    chunk_size: int,
) -> pd.DataFrame:
    if not gvkeys:
        return pd.DataFrame()
    conn = _connect_wrds(dotenv_path)
    frames: list[pd.DataFrame] = []
    try:
        query = """
            select
                gvkey,
                datadate,
                fyear,
                fyr,
                indfmt,
                consol,
                datafmt,
                popsrc,
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
              and datadate between %s and %s
            order by gvkey, datadate
        """
        for chunk in _chunk(gvkeys, chunk_size):
            frame = pd.read_sql(query, conn, params=(chunk, start_date.isoformat(), end_date.isoformat()))
            if not frame.empty:
                frames.append(frame)
    finally:
        conn.close()
    if not frames:
        return pd.DataFrame()
    funda = pd.concat(frames, ignore_index=True)
    funda["gvkey"] = funda["gvkey"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    funda["datadate"] = pd.to_datetime(funda["datadate"])
    return funda


def fetch_crsp_msf(
    permnos: list[str],
    *,
    start_date: date,
    end_date: date,
    dotenv_path: str | Path,
    chunk_size: int,
) -> pd.DataFrame:
    if not permnos:
        return pd.DataFrame()
    conn = _connect_wrds(dotenv_path)
    frames: list[pd.DataFrame] = []
    try:
        query = """
            select
                permno,
                permco,
                date,
                ret,
                retx,
                prc,
                shrout,
                vol
            from crsp.msf
            where permno = any(%s)
              and date between %s and %s
            order by permno, date
        """
        for chunk in _chunk(permnos, chunk_size):
            ints = [int(value) for value in chunk]
            frame = pd.read_sql(query, conn, params=(ints, start_date.isoformat(), end_date.isoformat()))
            if not frame.empty:
                frames.append(frame)
    finally:
        conn.close()
    if not frames:
        return pd.DataFrame()
    msf = pd.concat(frames, ignore_index=True)
    msf["permno"] = msf["permno"].astype("Int64").astype(str)
    msf["permco"] = msf["permco"].astype("Int64").astype(str)
    msf["date"] = pd.to_datetime(msf["date"])
    return msf


def fetch_crsp_msi(*, start_date: date, end_date: date, dotenv_path: str | Path) -> pd.DataFrame:
    conn = _connect_wrds(dotenv_path)
    try:
        query = """
            select
                date,
                vwretd,
                ewretd,
                sprtrn
            from crsp.msi
            where date between %s and %s
            order by date
        """
        msi = pd.read_sql(query, conn, params=(start_date.isoformat(), end_date.isoformat()))
    finally:
        conn.close()
    if not msi.empty:
        msi["date"] = pd.to_datetime(msi["date"])
    return msi


def pull_raw(
    backbone_path: str = DEFAULT_BACKBONE,
    *,
    dotenv_path: str = DEFAULT_DOTENV,
    gvkey_chunk: int = DEFAULT_GVKEY_CHUNK,
    permno_chunk: int = DEFAULT_PERMNO_CHUNK,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    backbone = load_backbone(backbone_path)
    matched_gvkey = sorted(backbone["gvkey"].replace("", pd.NA).dropna().unique().tolist())
    matched_permno = sorted(backbone["permno"].replace("", pd.NA).dropna().unique().tolist())
    year_min = int(backbone["year"].min())
    year_max = int(backbone["year"].max())
    funda_start = date(year_min - 1, 1, 1)
    funda_end = date(year_max, 12, 31)
    market_start = date(year_min - 1, 1, 1)
    market_end = date(year_max + 1, 12, 31)

    funda = fetch_compustat_funda(
        matched_gvkey,
        start_date=funda_start,
        end_date=funda_end,
        dotenv_path=dotenv_path,
        chunk_size=gvkey_chunk,
    )
    msf = fetch_crsp_msf(
        matched_permno,
        start_date=market_start,
        end_date=market_end,
        dotenv_path=dotenv_path,
        chunk_size=permno_chunk,
    )
    msi = fetch_crsp_msi(start_date=market_start, end_date=market_end, dotenv_path=dotenv_path)

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "backbone_path": str(Path(backbone_path).resolve()),
        "backbone_row_count": int(len(backbone)),
        "backbone_matched_gvkey": int(len(matched_gvkey)),
        "backbone_matched_permno": int(len(matched_permno)),
        "year_min": year_min,
        "year_max": year_max,
        "funda_query_range": [funda_start.isoformat(), funda_end.isoformat()],
        "market_query_range": [market_start.isoformat(), market_end.isoformat()],
        "funda_rows": int(len(funda)),
        "funda_gvkey_coverage": int(funda["gvkey"].nunique()) if not funda.empty else 0,
        "msf_rows": int(len(msf)),
        "msf_permno_coverage": int(msf["permno"].nunique()) if not msf.empty else 0,
        "msi_rows": int(len(msi)),
        "backbone_wrds_bridge_status_counts": backbone["wrds_bridge_status"].value_counts(dropna=False).to_dict(),
    }
    return funda, msf, msi, report


def main() -> None:
    args = parse_args()
    funda, msf, msi, report = pull_raw(
        backbone_path=args.backbone,
        dotenv_path=args.dotenv,
        gvkey_chunk=args.gvkey_chunk,
        permno_chunk=args.permno_chunk,
    )
    for path in [args.funda_output, args.msf_output, args.msi_output, args.report]:
        _ensure_parent(path)
    funda.to_parquet(args.funda_output, index=False)
    msf.to_parquet(args.msf_output, index=False)
    msi.to_parquet(args.msi_output, index=False)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding='utf-8')


if __name__ == "__main__":
    main()
