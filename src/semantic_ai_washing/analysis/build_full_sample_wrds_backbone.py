"""Build a broad firm-year WRDS backbone from observed or expanded panel sources."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.analysis.build_wrds_gvkey_permno_bridge import (
    LinkRow,
    choose_link_candidate,
    choose_lookup_candidate,
    fetch_link_rows,
    fetch_lookup_rows,
)

DEFAULT_NARRATIVE = "data/processed/aggregates/firm_year_narrative_measures_prelim_clean_2016_2025_refresh_v1.parquet"
DEFAULT_CROSSWALK = "data/externals/crosswalks/cik_gvkey_ever_speaker_2016_2025_refresh_v1.csv"
DEFAULT_OUTPUT = "data/interim/market/full_sample_wrds_backbone_v1.csv"
DEFAULT_REPORT = "reports/analysis/full_sample_wrds_backbone_v1.json"
DEFAULT_DOTENV = ".env"
DEFAULT_ALLOWED_LINKTYPES = ("LC", "LU", "LS")
DEFAULT_ALLOWED_LINKPRIM = ("P", "C")
OUTPUT_COLUMNS = [
    "cik",
    "year",
    "year_end_date",
    "gvkey",
    "permno",
    "permco",
    "sic",
    "wrds_bridge_status",
    "valid_candidate_count",
    "linktype",
    "linkprim",
    "linkdt",
    "linkenddt",
    "source_window_id",
    "model_id",
    "ai_total",
    "doc_count",
    "n_A",
    "n_S",
    "n_I",
    "n_total",
    "AI_Focus",
    "log_1p_A",
    "log_1p_S",
    "SpecShare",
    "CredAI",
    "A_S",
]


@dataclass(frozen=True)
class FirmYearRow:
    cik: str
    year: int
    gvkey: str
    sic: str
    source_window_id: str
    model_id: str
    ai_total: float | int | None
    doc_count: float | int | None
    n_A: float | int | None
    n_S: float | int | None
    n_I: float | int | None
    n_total: float | int | None
    AI_Focus: float | int | None
    log_1p_A: float | int | None
    log_1p_S: float | int | None
    SpecShare: float | int | None
    CredAI: float | int | None
    A_S: float | int | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--narrative", default=DEFAULT_NARRATIVE)
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--dotenv", default=DEFAULT_DOTENV)
    return parser.parse_args()


def _ensure_parent(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _normalize_string(series: pd.Series, *, zero_fill: int | None = None) -> pd.Series:
    out = series.fillna("").astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    if zero_fill is not None:
        out = out.str.zfill(zero_fill)
    return out


def load_narrative(path: str | Path) -> pd.DataFrame:
    df = pd.read_parquet(path).copy()
    rename_map = {}
    if "source_cik" in df.columns:
        rename_map["source_cik"] = "cik"
    if "source_year" in df.columns:
        rename_map["source_year"] = "year"
    df = df.rename(columns=rename_map)
    missing = {"cik", "year"} - set(df.columns)
    if missing:
        missing_csv = ", ".join(sorted(missing))
        raise ValueError(
            f"Input panel is missing required firm-year keys: {missing_csv}. "
            "Expected either source_cik/source_year or cik/year."
        )
    df["cik"] = _normalize_string(df["cik"], zero_fill=10)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    defaults: dict[str, Any] = {
        "source_window_id": "",
        "model_id": "",
        "ai_total": 0,
        "doc_count": 0,
        "n_A": 0,
        "n_S": 0,
        "n_I": 0,
        "n_total": 0,
        "AI_Focus": 0.0,
        "log_1p_A": 0.0,
        "log_1p_S": 0.0,
        "SpecShare": 0.0,
        "CredAI": 0.0,
        "A_S": 0.0,
    }
    for column, default in defaults.items():
        if column not in df.columns:
            df[column] = default
    return df


def load_crosswalk(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).copy()
    df["cik"] = _normalize_string(df["cik"], zero_fill=10)
    df["gvkey"] = _normalize_string(df["gvkey"])
    df["sic"] = _normalize_string(df.get("sic", pd.Series([""] * len(df))))
    return df[["cik", "gvkey", "sic"]].drop_duplicates(subset=["cik"])


def build_firm_year_rows(narrative: pd.DataFrame, crosswalk: pd.DataFrame) -> list[FirmYearRow]:
    merged = narrative.merge(crosswalk, on="cik", how="left", suffixes=("", "_xwalk"))
    rows: list[FirmYearRow] = []
    for row in merged.itertuples(index=False):
        rows.append(
            FirmYearRow(
                cik=str(row.cik),
                year=int(row.year),
                gvkey=str(getattr(row, "gvkey", "") or ""),
                sic=str(getattr(row, "sic", "") or ""),
                source_window_id=str(getattr(row, "source_window_id", "") or ""),
                model_id=str(getattr(row, "model_id", "") or ""),
                ai_total=getattr(row, "ai_total", None),
                doc_count=getattr(row, "doc_count", None),
                n_A=getattr(row, "n_A", None),
                n_S=getattr(row, "n_S", None),
                n_I=getattr(row, "n_I", None),
                n_total=getattr(row, "n_total", None),
                AI_Focus=getattr(row, "AI_Focus", None),
                log_1p_A=getattr(row, "log_1p_A", None),
                log_1p_S=getattr(row, "log_1p_S", None),
                SpecShare=getattr(row, "SpecShare", None),
                CredAI=getattr(row, "CredAI", None),
                A_S=getattr(row, "A_S", None),
            )
        )
    return rows


def _year_end(year: int) -> str:
    return date(year, 12, 31).strftime("%Y%m%d")


def build_backbone(
    narrative_path: str = DEFAULT_NARRATIVE,
    crosswalk_path: str = DEFAULT_CROSSWALK,
    *,
    dotenv_path: str = DEFAULT_DOTENV,
    allowed_linktypes: tuple[str, ...] = DEFAULT_ALLOWED_LINKTYPES,
    allowed_linkprim: tuple[str, ...] = DEFAULT_ALLOWED_LINKPRIM,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    narrative = load_narrative(narrative_path)
    crosswalk = load_crosswalk(crosswalk_path)
    firm_year_rows = build_firm_year_rows(narrative, crosswalk)

    gvkeys = sorted({row.gvkey for row in firm_year_rows if row.gvkey})
    ciks = sorted({row.cik for row in firm_year_rows if row.cik})
    link_rows = fetch_link_rows(
        gvkeys,
        dotenv_path=dotenv_path,
        allowed_linktypes=allowed_linktypes,
        allowed_linkprim=allowed_linkprim,
    ) if gvkeys else {}
    lookup_rows = fetch_lookup_rows(dotenv_path=dotenv_path, ciks=ciks) if ciks else {}

    records: list[dict[str, Any]] = []
    for row in firm_year_rows:
        year_end = _year_end(row.year)
        record = {
            "cik": row.cik,
            "year": row.year,
            "year_end_date": year_end,
            "gvkey": row.gvkey,
            "permno": "",
            "permco": "",
            "sic": row.sic,
            "wrds_bridge_status": "unmatched",
            "valid_candidate_count": 0,
            "linktype": "",
            "linkprim": "",
            "linkdt": "",
            "linkenddt": "",
            "source_window_id": row.source_window_id,
            "model_id": row.model_id,
            "ai_total": row.ai_total,
            "doc_count": row.doc_count,
            "n_A": row.n_A,
            "n_S": row.n_S,
            "n_I": row.n_I,
            "n_total": row.n_total,
            "AI_Focus": row.AI_Focus,
            "log_1p_A": row.log_1p_A,
            "log_1p_S": row.log_1p_S,
            "SpecShare": row.SpecShare,
            "CredAI": row.CredAI,
            "A_S": row.A_S,
        }

        chosen_link: LinkRow | None = None
        if row.gvkey:
            chosen_link, valid_count = choose_link_candidate(link_rows.get(row.gvkey, []), year_end)
            if chosen_link is not None:
                record.update(
                    {
                        "permno": chosen_link.permno,
                        "permco": chosen_link.permco,
                        "wrds_bridge_status": "matched",
                        "valid_candidate_count": valid_count,
                        "linktype": chosen_link.linktype,
                        "linkprim": chosen_link.linkprim,
                        "linkdt": chosen_link.linkdt,
                        "linkenddt": chosen_link.linkenddt,
                    }
                )
            else:
                record["wrds_bridge_status"] = "no_valid_link"

        if not record["permno"] and row.cik:
            chosen_lookup, valid_count = choose_lookup_candidate(lookup_rows.get(row.cik, []), year_end)
            if chosen_lookup is not None:
                record.update(
                    {
                        "gvkey": record["gvkey"] or chosen_lookup.gvkey,
                        "permno": chosen_lookup.permno,
                        "permco": chosen_lookup.permco,
                        "wrds_bridge_status": "matched_via_ccm_lookup_fallback",
                        "valid_candidate_count": valid_count,
                        "linkdt": chosen_lookup.linkdt,
                        "linkenddt": chosen_lookup.linkenddt,
                    }
                )
        records.append(record)

    frame = pd.DataFrame.from_records(records, columns=OUTPUT_COLUMNS)
    matched = frame[frame["permno"].astype(str).str.strip() != ""]
    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "narrative_path": str(Path(narrative_path).resolve()),
        "crosswalk_path": str(Path(crosswalk_path).resolve()),
        "row_count": int(len(frame)),
        "year_min": int(frame["year"].min()),
        "year_max": int(frame["year"].max()),
        "unique_cik": int(frame["cik"].nunique()),
        "unique_gvkey": int(frame["gvkey"].replace("", pd.NA).dropna().nunique()),
        "matched_permno_rows": int(len(matched)),
        "matched_permno_rate": round(float(len(matched) / len(frame)), 4) if len(frame) else 0.0,
        "unique_permno": int(matched["permno"].nunique()),
        "wrds_bridge_status_counts": frame["wrds_bridge_status"].value_counts(dropna=False).to_dict(),
        "source_window_counts": frame["source_window_id"].value_counts(dropna=False).to_dict(),
        "model_id_counts": frame["model_id"].value_counts(dropna=False).to_dict(),
    }
    return frame, report


def main() -> None:
    args = parse_args()
    frame, report = build_backbone(
        narrative_path=args.narrative,
        crosswalk_path=args.crosswalk,
        dotenv_path=args.dotenv,
    )
    _ensure_parent(args.output)
    _ensure_parent(args.report)
    frame.to_csv(args.output, index=False)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
