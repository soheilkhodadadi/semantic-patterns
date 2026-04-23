"""Build the canonical 2016-2025 ever-speaker annual panel from refresh-era inputs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from pandas.errors import EmptyDataError

from semantic_ai_washing.aggregation.build_ever_speaker_annual_panel import (
    _compute_narrative_features,
    _prepare_application_panel,
    _prepare_patent_panel,
)
from semantic_ai_washing.analysis.build_full_sample_wrds_backbone import build_backbone
from semantic_ai_washing.data.pull_compustat_controls import compute_controls

DEFAULT_NARRATIVE = (
    "data/processed/aggregates/firm_year_narrative_measures_prelim_clean_2016_2025_refresh_v1.parquet"
)
DEFAULT_LOOKUP_PRIMARY = "data/metadata/company_lookup_ever_speaker_2016_2025_hybrid_v1.csv"
DEFAULT_LOOKUP_SECONDARY = "data/metadata/company_lookup_ever_speaker_2016_2025_refresh_v1.csv"
DEFAULT_SEC_FALLBACK = "data/external/cik_ticker_list.csv"
DEFAULT_PATENTS = (
    "data/processed/patents/ai_patent_counts_filtered_ever_speaker_2016_2025_refresh_grant_2014plus.csv"
)
DEFAULT_APPLICATIONS = (
    "data/processed/patents/ai_application_counts_filtered_ever_speaker_2016_2025_hybrid_pregrant_2014plus.csv"
)
DEFAULT_CROSSWALK = "data/externals/crosswalks/cik_gvkey_ever_speaker_2016_2025_refresh_v1.csv"
DEFAULT_FUNDA_RAW = "data/interim/market/wrds_comp_funda_full_sample_v1.parquet"
DEFAULT_MSF_RAW = "data/interim/market/wrds_crsp_msf_full_sample_v1.parquet"
DEFAULT_MSI_RAW = "data/interim/market/wrds_crsp_msi_full_sample_v1.parquet"
DEFAULT_SCAFFOLD = (
    "data/processed/panel/canonical/ever_speaker_scaffold_2016_2025_prehybrid_v1.parquet"
)
DEFAULT_BACKBONE = "data/interim/market/ever_speaker_wrds_backbone_2016_2025_prehybrid_v1.csv"
DEFAULT_CONTROLS = "data/interim/market/annual_controls_ever_speaker_2016_2025_prehybrid_v1.csv"
DEFAULT_MARKET = "data/interim/market/annual_market_features_ever_speaker_2016_2025_prehybrid_v1.csv"
DEFAULT_PANEL_PARQUET = (
    "data/processed/panel/canonical/ever_speaker_panel_2016_2025_prehybrid_v1.parquet"
)
DEFAULT_PANEL_CSV = "data/processed/panel/canonical/ever_speaker_panel_2016_2025_prehybrid_v1.csv"
DEFAULT_REPORT = "reports/analysis/ever_speaker_panel_2016_2025_prehybrid_v1.json"
DEFAULT_DOTENV = ".env"

IDENTITY_COLUMNS = [
    "cik",
    "name",
    "name_clean",
    "ticker",
    "gvkey",
    "sic",
    "identity_name_source",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--narrative", default=DEFAULT_NARRATIVE)
    parser.add_argument("--lookup-primary", default=DEFAULT_LOOKUP_PRIMARY)
    parser.add_argument("--lookup-secondary", default=DEFAULT_LOOKUP_SECONDARY)
    parser.add_argument("--sec-fallback", default=DEFAULT_SEC_FALLBACK)
    parser.add_argument("--patents", default=DEFAULT_PATENTS)
    parser.add_argument("--applications", default=DEFAULT_APPLICATIONS)
    parser.add_argument("--crosswalk", default=DEFAULT_CROSSWALK)
    parser.add_argument("--funda-raw", default=DEFAULT_FUNDA_RAW)
    parser.add_argument("--msf-raw", default=DEFAULT_MSF_RAW)
    parser.add_argument("--msi-raw", default=DEFAULT_MSI_RAW)
    parser.add_argument("--scaffold-output", default=DEFAULT_SCAFFOLD)
    parser.add_argument("--backbone-output", default=DEFAULT_BACKBONE)
    parser.add_argument("--controls-output", default=DEFAULT_CONTROLS)
    parser.add_argument("--market-output", default=DEFAULT_MARKET)
    parser.add_argument("--panel-output-parquet", default=DEFAULT_PANEL_PARQUET)
    parser.add_argument("--panel-output-csv", default=DEFAULT_PANEL_CSV)
    parser.add_argument("--report", default=DEFAULT_REPORT)
    parser.add_argument("--dotenv", default=DEFAULT_DOTENV)
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--patent-buffer-years", type=int, default=2)
    return parser.parse_args()


def _ensure_parent(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def _normalize_cik(value: Any) -> str:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return digits.zfill(10) if digits else ""


def _clean_name(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _coalesce(*values: Any) -> Any:
    for value in values:
        if pd.isna(value):
            continue
        text = str(value).strip()
        if text != "" and text.lower() != "nan":
            return text
    return ""


def _year_mode_map(frame: pd.DataFrame, column: str) -> dict[int, str]:
    if column not in frame.columns:
        return {}
    clean = frame[["year", column]].copy()
    clean[column] = clean[column].fillna("").astype(str).str.strip()
    clean = clean[clean[column] != ""]
    if clean.empty:
        return {}
    return (
        clean.groupby("year", sort=True)[column]
        .agg(lambda values: values.mode().iloc[0])
        .to_dict()
    )


def load_observed_narrative(path: str | Path) -> pd.DataFrame:
    frame = pd.read_parquet(path).copy()
    frame = frame.rename(columns={"source_cik": "cik", "source_year": "year"})
    frame["cik"] = frame["cik"].apply(_normalize_cik)
    frame["year"] = pd.to_numeric(frame["year"], errors="coerce").astype(int)
    return frame


def _load_lookup(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype=str).copy()
    frame["cik"] = frame["cik"].apply(_normalize_cik)
    for column in ["name", "name_clean", "ticker", "gvkey", "sic", "name_source"]:
        if column not in frame.columns:
            frame[column] = ""
        frame[column] = frame[column].fillna("").astype(str).str.strip()
    return frame[["cik", "name", "name_clean", "ticker", "gvkey", "sic", "name_source"]]


def _load_sec_fallback(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype=str).copy()
    frame["cik"] = frame["CIK"].apply(_normalize_cik)
    frame["name"] = frame["Name"].fillna("").astype(str).str.strip()
    frame["ticker"] = frame["Ticker"].fillna("").astype(str).str.strip().str.upper()
    frame["sic"] = frame["SIC"].fillna("").astype(str).str.strip()
    frame["name_source"] = "sec_ticker_list"
    return frame[["cik", "name", "ticker", "sic", "name_source"]].drop_duplicates(subset=["cik"])


def build_identity_lookup(
    universe_ciks: list[str],
    *,
    primary_lookup_path: str | Path,
    secondary_lookup_path: str | Path,
    sec_fallback_path: str | Path,
) -> pd.DataFrame:
    base = pd.DataFrame({"cik": sorted(universe_ciks)})
    primary = _load_lookup(primary_lookup_path).rename(
        columns={
            "name": "name_primary",
            "name_clean": "name_clean_primary",
            "ticker": "ticker_primary",
            "gvkey": "gvkey_primary",
            "sic": "sic_primary",
            "name_source": "name_source_primary",
        }
    )
    secondary = _load_lookup(secondary_lookup_path).rename(
        columns={
            "name": "name_secondary",
            "name_clean": "name_clean_secondary",
            "ticker": "ticker_secondary",
            "gvkey": "gvkey_secondary",
            "sic": "sic_secondary",
            "name_source": "name_source_secondary",
        }
    )
    sec_fallback = _load_sec_fallback(sec_fallback_path).rename(
        columns={
            "name": "name_sec",
            "ticker": "ticker_sec",
            "sic": "sic_sec",
            "name_source": "name_source_sec",
        }
    )

    merged = base.merge(primary, on="cik", how="left")
    merged = merged.merge(secondary, on="cik", how="left")
    merged = merged.merge(sec_fallback, on="cik", how="left")

    merged["name"] = merged.apply(
        lambda row: _coalesce(row.get("name_primary"), row.get("name_secondary"), row.get("name_sec")),
        axis=1,
    )
    merged["name_clean"] = merged.apply(
        lambda row: _coalesce(
            row.get("name_clean_primary"),
            row.get("name_clean_secondary"),
            row.get("name"),
        ),
        axis=1,
    )
    merged["ticker"] = merged.apply(
        lambda row: _coalesce(row.get("ticker_primary"), row.get("ticker_secondary"), row.get("ticker_sec")),
        axis=1,
    )
    merged["gvkey"] = merged.apply(
        lambda row: _coalesce(row.get("gvkey_primary"), row.get("gvkey_secondary")),
        axis=1,
    )
    merged["sic"] = merged.apply(
        lambda row: _coalesce(row.get("sic_primary"), row.get("sic_secondary"), row.get("sic_sec")),
        axis=1,
    )
    merged["identity_name_source"] = merged.apply(
        lambda row: _coalesce(
            row.get("name_source_primary"),
            row.get("name_source_secondary"),
            row.get("name_source_sec"),
        ),
        axis=1,
    )
    return merged[IDENTITY_COLUMNS]


def build_ever_speaker_scaffold(
    narrative: pd.DataFrame,
    *,
    start_year: int,
    end_year: int,
    identity_lookup: pd.DataFrame,
    patents_path: str | Path,
    applications_path: str | Path,
    patent_buffer_years: int,
) -> pd.DataFrame:
    narrative = narrative.loc[narrative["year"].between(start_year, end_year)].copy()
    narrative = narrative.sort_values(["cik", "year"]).drop_duplicates(["cik", "year"], keep="last")

    universe_ciks = sorted(narrative["cik"].unique().tolist())
    scaffold = pd.MultiIndex.from_product(
        [universe_ciks, list(range(start_year, end_year + 1))],
        names=["cik", "year"],
    ).to_frame(index=False)
    scaffold["year"] = scaffold["year"].astype(int)

    keep_narrative = [
        "cik",
        "year",
        "doc_count",
        "n_total",
        "n_A",
        "n_S",
        "n_I",
        "ai_total",
        "source_window_id",
        "model_id",
    ]
    merged = scaffold.merge(narrative[keep_narrative], on=["cik", "year"], how="left")
    for column in ["doc_count", "n_total", "n_A", "n_S", "n_I", "ai_total"]:
        merged[column] = pd.to_numeric(merged[column], errors="coerce").fillna(0)

    source_defaults = _year_mode_map(narrative, "source_window_id")
    model_defaults = _year_mode_map(narrative, "model_id")
    merged["source_window_id"] = merged["source_window_id"].fillna(
        merged["year"].map(source_defaults).fillna("")
    )
    merged["model_id"] = merged["model_id"].fillna(merged["year"].map(model_defaults).fillna(""))

    merged = _compute_narrative_features(merged)
    merged = merged.merge(identity_lookup, on="cik", how="left")

    patents = pd.read_csv(patents_path, low_memory=False)
    patent_panel = _prepare_patent_panel(
        patents,
        ciks=merged["cik"],
        start_year=start_year,
        end_year=end_year,
        buffer_years=patent_buffer_years,
    )
    merged = merged.merge(patent_panel, on=["cik", "year"], how="left")

    try:
        applications = pd.read_csv(applications_path, low_memory=False)
    except EmptyDataError:
        applications = pd.DataFrame(
            columns=[
                "cik",
                "year",
                "applications_total",
                "applications_ai",
                "ai_share_applications",
            ]
        )
    application_panel = _prepare_application_panel(
        applications,
        ciks=merged["cik"],
        start_year=start_year,
        end_year=end_year,
        buffer_years=patent_buffer_years,
    )
    merged = merged.merge(application_panel, on=["cik", "year"], how="left")
    return merged.sort_values(["cik", "year"]).reset_index(drop=True)


def build_controls_from_funda(raw_funda: pd.DataFrame) -> pd.DataFrame:
    controls = compute_controls(raw_funda.copy(), align="fyear")
    controls["gvkey"] = (
        controls["gvkey"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.lstrip("0")
    )
    controls.loc[controls["gvkey"] == "", "gvkey"] = pd.NA
    controls["year"] = pd.to_numeric(controls["year"], errors="coerce").astype("Int64")
    return controls.sort_values(["gvkey", "year"]).reset_index(drop=True)


def _compound_return(values: pd.Series) -> float | None:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if clean.empty:
        return None
    return float(np.prod(1.0 + clean.astype(float).to_numpy()) - 1.0)


def build_annual_market_features(raw_msf: pd.DataFrame, raw_msi: pd.DataFrame) -> pd.DataFrame:
    msf = raw_msf.copy()
    msf["permno"] = msf["permno"].fillna("").astype(str).str.strip()
    msf["date"] = pd.to_datetime(msf["date"], errors="coerce")
    msf = msf.dropna(subset=["date"])
    msf["year"] = msf["date"].dt.year.astype(int)

    market = raw_msi.copy()
    market["date"] = pd.to_datetime(market["date"], errors="coerce")
    market = market.dropna(subset=["date"])
    market["year"] = market["date"].dt.year.astype(int)
    market_year = (
        market.groupby("year", sort=True)
        .agg(
            annual_vwretd=("vwretd", _compound_return),
            annual_ewretd=("ewretd", _compound_return),
            annual_sprtrn=("sprtrn", _compound_return),
        )
        .reset_index()
    )

    annual = (
        msf.groupby(["permno", "year"], sort=True)
        .agg(
            annual_ret=("ret", _compound_return),
            annual_retx=("retx", _compound_return),
            obs_months=("date", "count"),
        )
        .reset_index()
    )

    last_obs = (
        msf.sort_values(["permno", "year", "date"])
        .groupby(["permno", "year"], sort=False)
        .tail(1)
        .copy()
    )
    last_obs["market_cap_year_end"] = (
        pd.to_numeric(last_obs["prc"], errors="coerce").abs()
        * pd.to_numeric(last_obs["shrout"], errors="coerce")
    )
    last_obs = last_obs[
        ["permno", "year", "permco", "date", "prc", "shrout", "vol", "market_cap_year_end"]
    ].rename(columns={"date": "year_end_market_date"})

    annual = annual.merge(last_obs, on=["permno", "year"], how="left")
    annual = annual.merge(market_year, on="year", how="left")
    annual["annual_bhar_vw"] = (
        (1.0 + annual["annual_ret"].astype(float))
        / (1.0 + annual["annual_vwretd"].astype(float))
        - 1.0
    )
    annual["first_market_year"] = annual.groupby("permno", sort=False)["year"].transform("min")
    annual["firm_age_market"] = annual["year"] - annual["first_market_year"] + 1
    return annual.sort_values(["permno", "year"]).reset_index(drop=True)


def merge_panel(
    scaffold: pd.DataFrame,
    backbone: pd.DataFrame,
    controls: pd.DataFrame,
    market: pd.DataFrame,
) -> pd.DataFrame:
    panel = scaffold.copy()
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")
    id_cols = [
        "cik",
        "year",
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
    ]
    backbone_subset = backbone[id_cols].copy()
    for column in ["gvkey", "permno", "permco", "sic", "wrds_bridge_status", "linktype", "linkprim", "linkdt", "linkenddt"]:
        backbone_subset[column] = backbone_subset[column].replace("", pd.NA)

    panel = panel.merge(backbone_subset, on=["cik", "year"], how="left", suffixes=("", "_backbone"))
    panel["gvkey"] = panel["gvkey_backbone"].where(panel["gvkey_backbone"].notna(), panel["gvkey"])
    panel["sic"] = panel["sic_backbone"].where(panel["sic_backbone"].notna(), panel["sic"])
    panel = panel.drop(columns=["gvkey_backbone", "sic_backbone"])
    for column in ["gvkey", "permno", "permco"]:
        panel[column] = (
            panel[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
        )
        panel.loc[panel[column] == "", column] = pd.NA

    controls_subset = controls.copy()
    controls_subset["gvkey"] = (
        controls_subset["gvkey"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )
    controls_subset["year"] = pd.to_numeric(controls_subset["year"], errors="coerce").astype("Int64")
    panel = panel.merge(controls_subset, on=["gvkey", "year"], how="left")

    market_subset = market.copy()
    for column in ["permno", "permco"]:
        market_subset[column] = (
            market_subset[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
        )
        market_subset.loc[market_subset[column] == "", column] = pd.NA
    market_subset["year"] = pd.to_numeric(market_subset["year"], errors="coerce").astype("Int64")
    panel = panel.merge(market_subset, on=["permno", "year"], how="left", suffixes=("", "_market"))
    return panel.sort_values(["cik", "year"]).reset_index(drop=True)


def _report(panel: pd.DataFrame, scaffold: pd.DataFrame, controls: pd.DataFrame, market: pd.DataFrame) -> dict[str, Any]:
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "row_count": int(len(panel)),
        "unique_cik": int(panel["cik"].nunique()),
        "year_min": int(panel["year"].min()),
        "year_max": int(panel["year"].max()),
        "simple_full_scaffold_rows": int(panel["cik"].nunique() * panel["year"].nunique()),
        "positive_talk_rows": int((panel["any_ai_talk"] == 1).sum()),
        "zero_talk_rows": int((panel["any_ai_talk"] == 0).sum()),
        "identity_gvkey_rows": int(panel["gvkey"].replace("", pd.NA).dropna().shape[0]),
        "identity_gvkey_unique": int(panel["gvkey"].replace("", pd.NA).dropna().nunique()),
        "permno_rows": int(panel["permno"].replace("", pd.NA).dropna().shape[0]),
        "permno_unique": int(panel["permno"].replace("", pd.NA).dropna().nunique()),
        "control_rows_nonmissing_ln_assets": int(panel["ln_assets"].notna().sum()),
        "market_rows_nonmissing_annual_ret": int(panel["annual_ret"].notna().sum()),
        "lookup_missing_name_rows": int(panel["name"].fillna("").astype(str).str.strip().eq("").sum()),
        "control_source_rows": int(len(controls)),
        "market_source_rows": int(len(market)),
        "wrds_bridge_status_counts": panel["wrds_bridge_status"].fillna("missing").value_counts(dropna=False).to_dict(),
        "source_window_counts": scaffold["source_window_id"].value_counts(dropna=False).to_dict(),
        "model_id_counts": scaffold["model_id"].value_counts(dropna=False).to_dict(),
        "years_per_cik_summary": panel.groupby("cik")["year"].nunique().describe().to_dict(),
    }


def main() -> None:
    args = parse_args()

    observed = load_observed_narrative(args.narrative)
    identity_lookup = build_identity_lookup(
        sorted(observed["cik"].unique().tolist()),
        primary_lookup_path=args.lookup_primary,
        secondary_lookup_path=args.lookup_secondary,
        sec_fallback_path=args.sec_fallback,
    )
    scaffold = build_ever_speaker_scaffold(
        observed,
        start_year=args.start_year,
        end_year=args.end_year,
        identity_lookup=identity_lookup,
        patents_path=args.patents,
        applications_path=args.applications,
        patent_buffer_years=args.patent_buffer_years,
    )

    scaffold_output = Path(args.scaffold_output)
    _ensure_parent(scaffold_output)
    scaffold.to_parquet(scaffold_output, index=False)

    backbone, _ = build_backbone(
        narrative_path=str(scaffold_output),
        crosswalk_path=args.crosswalk,
        dotenv_path=args.dotenv,
    )
    _ensure_parent(args.backbone_output)
    backbone.to_csv(args.backbone_output, index=False)

    controls_raw = pd.read_parquet(args.funda_raw)
    controls = build_controls_from_funda(controls_raw)
    _ensure_parent(args.controls_output)
    controls.to_csv(args.controls_output, index=False)

    raw_msf = pd.read_parquet(args.msf_raw)
    raw_msi = pd.read_parquet(args.msi_raw)
    market = build_annual_market_features(raw_msf, raw_msi)
    _ensure_parent(args.market_output)
    market.to_csv(args.market_output, index=False)

    panel = merge_panel(scaffold, backbone, controls, market)
    _ensure_parent(args.panel_output_parquet)
    panel.to_parquet(args.panel_output_parquet, index=False)
    _ensure_parent(args.panel_output_csv)
    panel.to_csv(args.panel_output_csv, index=False)

    report = _report(panel, scaffold, controls, market)
    _ensure_parent(args.report)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(
        "[refresh-ever-speaker-panel] "
        f"rows={len(panel)} firms={panel['cik'].nunique()} "
        f"positive_talk_rows={(panel['any_ai_talk'] == 1).sum()} "
        f"zero_talk_rows={(panel['any_ai_talk'] == 0).sum()}"
    )


if __name__ == "__main__":
    main()
