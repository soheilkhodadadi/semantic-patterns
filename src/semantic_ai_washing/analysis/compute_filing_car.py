"""Compute filing-level CAR and BHAR measures from daily event-return windows."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_DAILY_RETURNS = "data/interim/market/filing_event_returns_daily_v1.parquet"
DEFAULT_AI_MEASURES = "data/interim/market/filing_ai_measures_v1.csv"
DEFAULT_BRIDGE = "data/interim/market/filing_wrds_bridge_v1.csv"
DEFAULT_OUTPUT = "data/processed/panel/filing_event_panel_v1.parquet"
DEFAULT_REPORT = "reports/analysis/filing_event_panel_v1.json"

CAR_WINDOWS = {
    "car_m1_p1": (-1, 1),
    "car_m2_p2": (-2, 2),
}
BHAR_WINDOWS = {
    "bhar_1m": (0, 21),
    "bhar_3m": (0, 63),
    "bhar_6m": (0, 126),
    "bhar_12m": (0, 252),
}


def _load_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path, low_memory=False)


def _window_complete(relative_days: pd.Series, start_day: int, end_day: int) -> bool:
    observed = set(relative_days[(relative_days >= start_day) & (relative_days <= end_day)].tolist())
    expected = set(range(start_day, end_day + 1))
    return observed == expected


def _compute_car(group: pd.DataFrame, start_day: int, end_day: int) -> float | None:
    if not _window_complete(group["relative_day"], start_day, end_day):
        return None
    window = group[(group["relative_day"] >= start_day) & (group["relative_day"] <= end_day)]
    if window["abnormal_ret_vw"].isna().any():
        return None
    return float(window["abnormal_ret_vw"].sum())


def _compute_bhar(group: pd.DataFrame, start_day: int, end_day: int) -> float | None:
    if not _window_complete(group["relative_day"], start_day, end_day):
        return None
    window = group[(group["relative_day"] >= start_day) & (group["relative_day"] <= end_day)]
    if window[["ret", "vwretd"]].isna().any().any():
        return None
    gross_stock = float(np.prod(1.0 + window["ret"].astype(float).to_numpy()))
    gross_market = float(np.prod(1.0 + window["vwretd"].astype(float).to_numpy()))
    return gross_stock - gross_market


def _normalize_string_key(series: pd.Series, *, zero_fill: int | None = None) -> pd.Series:
    normalized = series.fillna("").astype(str).str.strip()
    if zero_fill is not None:
        normalized = normalized.str.replace(r"\.0$", "", regex=True)
        normalized = normalized.str.zfill(zero_fill)
    return normalized


def build_filing_event_panel(
    daily_returns_path: str = DEFAULT_DAILY_RETURNS,
    *,
    ai_measures_path: str = DEFAULT_AI_MEASURES,
    bridge_path: str = DEFAULT_BRIDGE,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    daily = pd.read_parquet(daily_returns_path)
    ai_measures = _load_csv(ai_measures_path)
    bridge = _load_csv(bridge_path)

    if daily.empty:
        report = {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "daily_returns_path": str(Path(daily_returns_path).resolve()),
            "row_count": 0,
        }
        return pd.DataFrame(), report

    for frame in (daily, ai_measures, bridge):
        if "filing_id" in frame.columns:
            frame["filing_id"] = _normalize_string_key(frame["filing_id"])
        if "source_filename" in frame.columns:
            frame["source_filename"] = _normalize_string_key(frame["source_filename"])
        if "gvkey" in frame.columns:
            frame["gvkey"] = _normalize_string_key(frame["gvkey"])
        if "cik" in frame.columns:
            frame["cik"] = _normalize_string_key(frame["cik"], zero_fill=10)
        if "filing_date" in frame.columns:
            frame["filing_date"] = _normalize_string_key(frame["filing_date"])

    daily["relative_day"] = pd.to_numeric(daily["relative_day"], errors="coerce").astype(int)
    daily = daily.sort_values(["filing_id", "relative_day", "trade_date"]).reset_index(drop=True)

    rows: list[dict[str, Any]] = []
    coverage = {key: 0 for key in [*CAR_WINDOWS, *BHAR_WINDOWS]}

    for filing_id, group in daily.groupby("filing_id", sort=False):
        first = group.iloc[0]
        row = {
            "filing_id": filing_id,
            "source_filename": first["source_filename"],
            "cik": first["cik"],
            "gvkey": first["gvkey"],
            "permno": first["permno"],
            "permco": first["permco"],
            "filing_date": first["filing_date"],
            "anchor_trading_date": first["anchor_trading_date"],
            "anchor_calendar_shift_days": int(first["anchor_calendar_shift_days"]),
            "wrds_bridge_status": first["wrds_bridge_status"],
            "daily_rows_available": int(len(group)),
        }
        for key, (start_day, end_day) in CAR_WINDOWS.items():
            value = _compute_car(group, start_day, end_day)
            row[key] = value
            row[f"{key}_complete"] = 0 if value is None else 1
            coverage[key] += int(value is not None)
        for key, (start_day, end_day) in BHAR_WINDOWS.items():
            value = _compute_bhar(group, start_day, end_day)
            row[key] = value
            row[f"{key}_complete"] = 0 if value is None else 1
            coverage[key] += int(value is not None)
        rows.append(row)

    panel = pd.DataFrame(rows)
    panel = panel.merge(
        ai_measures,
        on=["filing_id"],
        how="left",
        suffixes=("", "_ai"),
    )
    bridge_keep = bridge[[
        "filing_id",
        "valid_candidate_count",
        "linktype",
        "linkprim",
        "linkdt",
        "linkenddt",
    ]].copy()
    panel = panel.merge(bridge_keep, on="filing_id", how="left")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "daily_returns_path": str(Path(daily_returns_path).resolve()),
        "ai_measures_path": str(Path(ai_measures_path).resolve()),
        "bridge_path": str(Path(bridge_path).resolve()),
        "row_count": int(len(panel)),
        "coverage_counts": coverage,
        "car_nonmissing_count": int(panel["car_m1_p1"].notna().sum()),
        "bhar_6m_nonmissing_count": int(panel["bhar_6m"].notna().sum()),
        "date_min": str(panel["filing_date"].min()) if not panel.empty else "",
        "date_max": str(panel["filing_date"].max()) if not panel.empty else "",
    }
    return panel, report


def write_panel(panel: pd.DataFrame, output_path: str | Path) -> None:
    resolved = Path(output_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(resolved, index=False)


def write_report(report: dict[str, Any], report_path: str | Path) -> None:
    resolved = Path(report_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(report, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--daily-returns", default=DEFAULT_DAILY_RETURNS)
    parser.add_argument("--ai-measures", default=DEFAULT_AI_MEASURES)
    parser.add_argument("--bridge", default=DEFAULT_BRIDGE)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    panel, report = build_filing_event_panel(
        daily_returns_path=args.daily_returns,
        ai_measures_path=args.ai_measures,
        bridge_path=args.bridge,
    )
    write_panel(panel, args.output)
    write_report(report, args.report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
