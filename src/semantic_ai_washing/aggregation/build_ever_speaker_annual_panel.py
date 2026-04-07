"""Build an annual ever-speaker panel with buffered calendar-year patent timing."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_NARRATIVE = "data/processed/aggregates/firm_year_narrative_measures_prelim_clean_v1.parquet"
DEFAULT_PATENTS = (
    "data/processed/patents/ai_patent_counts_filtered_active_annual_allyears_2016plus_applied_v2_legalnorm_unique_lightweight.csv"
)
DEFAULT_CONTROLS = (
    "data/interim/controls/controls_by_firm_year_active_annual_allyears_2016_2024_v3.csv"
)
DEFAULT_LOOKUP = "data/metadata/company_lookup_active_annual_allyears_2021_2024.csv"
DEFAULT_OUT = "data/processed/panel/panel_ai_patents_controls_ever_speaker_2016_2024_v1.csv"
DEFAULT_QC = "reports/merge_qc_ever_speaker_2016_2024_v1.md"
DEFAULT_PATENT_BUFFER_YEARS = 2

NARRATIVE_COUNT_COLS = ["ai_total", "doc_count", "n_A", "n_S", "n_I", "n_total"]
CONTROL_COLS = [
    "gvkey",
    "sic",
    "ln_assets",
    "leverage",
    "cash",
    "rd_intensity",
    "capx_at",
    "roa",
    "sales_growth",
    "emp",
]


def normalize_cik(value) -> str:
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return digits.zfill(10) if digits else ""


def _zscore(series: pd.Series) -> pd.Series:
    std = float(series.std(ddof=0))
    if std == 0.0 or np.isnan(std):
        return pd.Series(np.zeros(len(series)), index=series.index, dtype=float)
    return (series - float(series.mean())) / std


def _df_to_md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    out = []
    out.append("| " + " | ".join(cols) + " |")
    out.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for _, row in df.iterrows():
        out.append(
            "| "
            + " | ".join("" if pd.isna(row[col]) else str(row[col]) for col in cols)
            + " |"
        )
    return "\n".join(out)


def _build_scaffold(ciks: pd.Series, years: range) -> pd.DataFrame:
    index = pd.MultiIndex.from_product(
        [sorted(set(ciks.astype(str))), list(years)],
        names=["cik", "year"],
    )
    scaffold = index.to_frame(index=False)
    scaffold["cik"] = scaffold["cik"].astype(str)
    scaffold["year"] = scaffold["year"].astype(int)
    return scaffold


def _compute_narrative_features(df: pd.DataFrame) -> pd.DataFrame:
    panel = df.copy()
    panel["n_total"] = panel["n_total"].fillna(panel[["n_A", "n_S", "n_I"]].sum(axis=1))
    panel["ai_total"] = panel["ai_total"].fillna(panel["n_total"])
    panel["any_ai_talk"] = (panel["ai_total"] > 0).astype(int)

    denom_total = panel["n_total"].replace(0, np.nan)
    panel["share_A"] = (panel["n_A"] / denom_total).fillna(0.0)
    panel["share_S"] = (panel["n_S"] / denom_total).fillna(0.0)
    panel["share_I"] = (panel["n_I"] / denom_total).fillna(0.0)

    denom_talk = (panel["n_A"] + panel["n_S"]).replace(0, np.nan)
    panel["ActShare"] = (panel["n_A"] / denom_talk).fillna(0.0)
    panel["SpecShare"] = (panel["n_S"] / denom_talk).fillna(0.0)
    panel["SpecMinusAct"] = panel["SpecShare"] - panel["ActShare"]

    panel["AI_Focus"] = np.log1p(panel["ai_total"])
    panel["log_1p_A"] = np.log1p(panel["n_A"])
    panel["log_1p_S"] = np.log1p(panel["n_S"])
    panel["log_n_A"] = panel["log_1p_A"]
    panel["log_n_S"] = panel["log_1p_S"]
    panel["has_actionable"] = (panel["n_A"] > 0).astype(int)
    panel["has_spec_only"] = ((panel["n_S"] > 0) & (panel["n_A"] == 0)).astype(int)
    panel["A_S"] = np.log1p(panel["n_A"] / (1.0 + panel["n_S"]))
    panel["CredAI"] = _zscore(panel["n_A"].astype(float)) - _zscore(panel["n_S"].astype(float))
    return panel


def _add_calendar_patent_timing(df: pd.DataFrame) -> pd.DataFrame:
    panel = df.sort_values(["cik", "year"]).copy()
    panel["patents_ai"] = pd.to_numeric(panel["patents_ai"], errors="coerce").fillna(0)
    for k in [0, 1, 2]:
        if k == 0:
            panel[f"patents_ai_lead{k}"] = panel["patents_ai"]
        else:
            panel[f"patents_ai_lead{k}"] = panel.groupby("cik")["patents_ai"].shift(-k)
        panel[f"log_patents_ai_lead{k}"] = np.log1p(panel[f"patents_ai_lead{k}"])
        panel[f"any_pat_{k}"] = (panel[f"patents_ai_lead{k}"].fillna(0) > 0).astype(float)

    for k in [1, 2]:
        panel[f"patents_ai_lag{k}"] = panel.groupby("cik")["patents_ai"].shift(k)
        panel[f"log_patents_ai_lag{k}"] = np.log1p(panel[f"patents_ai_lag{k}"])
        panel[f"any_pat_lag{k}"] = (panel[f"patents_ai_lag{k}"].fillna(0) > 0).astype(float)
    return panel


def _prepare_patent_panel(
    patents: pd.DataFrame,
    *,
    ciks: pd.Series,
    start_year: int,
    end_year: int,
    buffer_years: int = DEFAULT_PATENT_BUFFER_YEARS,
) -> pd.DataFrame:
    padded_start = int(start_year) - max(int(buffer_years), 0)
    padded_end = int(end_year) + max(int(buffer_years), 0)

    patent_series = patents.copy()
    patent_series["cik"] = patent_series["cik"].apply(normalize_cik)
    patent_series["year"] = pd.to_numeric(patent_series["year"], errors="coerce").astype(int)
    patent_series = patent_series.loc[
        patent_series["year"].between(padded_start, padded_end)
    ].copy()
    patent_series = patent_series.sort_values(["cik", "year"]).drop_duplicates(
        ["cik", "year"], keep="last"
    )

    scaffold = _build_scaffold(ciks, range(padded_start, padded_end + 1))
    patent_keep = ["cik", "year", "patents_total", "patents_ai", "ai_share"]
    patent_panel = scaffold.merge(
        patent_series[patent_keep], on=["cik", "year"], how="left"
    )
    patent_panel["patents_total"] = pd.to_numeric(
        patent_panel["patents_total"], errors="coerce"
    ).fillna(0)
    patent_panel["patents_ai"] = pd.to_numeric(
        patent_panel["patents_ai"], errors="coerce"
    ).fillna(0)
    patent_panel["ai_share_patents"] = (
        patent_panel["patents_ai"] / patent_panel["patents_total"].replace(0, np.nan)
    )
    if "ai_share" in patent_panel.columns:
        patent_panel = patent_panel.drop(columns=["ai_share"])

    patent_panel = _add_calendar_patent_timing(patent_panel)
    patent_panel = patent_panel.loc[
        patent_panel["year"].between(start_year, end_year)
    ].copy()
    keep_cols = [
        "cik",
        "year",
        "patents_total",
        "patents_ai",
        "ai_share_patents",
        "patents_ai_lag1",
        "patents_ai_lag2",
        "patents_ai_lead0",
        "patents_ai_lead1",
        "patents_ai_lead2",
        "log_patents_ai_lag1",
        "log_patents_ai_lag2",
        "log_patents_ai_lead0",
        "log_patents_ai_lead1",
        "log_patents_ai_lead2",
        "any_pat_lag1",
        "any_pat_lag2",
        "any_pat_0",
        "any_pat_1",
        "any_pat_2",
    ]
    return patent_panel[keep_cols]


def _write_qc(path: Path, panel: pd.DataFrame, source_rows: int, source_firms: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    zero_talk_rows = int((panel["any_ai_talk"] == 0).sum())
    positive_talk_rows = int((panel["any_ai_talk"] == 1).sum())
    rows_with_patents = int((panel["patents_total"] > 0).sum())
    rows_with_ai_patents = int((panel["patents_ai"] > 0).sum())
    year_counts = panel.groupby("year").size().rename("rows").reset_index()
    missing_controls = (
        panel[CONTROL_COLS]
        .isna()
        .mean()
        .round(3)
        .rename("missing_share")
        .reset_index()
        .rename(columns={"index": "column"})
    )

    lines = [
        "# Ever-Speaker Annual Panel QC",
        "",
        f"- Source AI-speaking rows: **{source_rows:,}**",
        f"- Source ever-speaker firms: **{source_firms:,}**",
        f"- Output annual scaffold rows: **{len(panel):,}**",
        f"- Output annual scaffold firms: **{panel['cik'].nunique():,}**",
        f"- Zero-disclosure rows retained: **{zero_talk_rows:,}**",
        f"- Positive-disclosure rows retained: **{positive_talk_rows:,}**",
        f"- Rows with any patents: **{rows_with_patents:,}**",
        f"- Rows with AI patents: **{rows_with_ai_patents:,}**",
        "",
        "## Year Counts",
        "",
        _df_to_md(year_counts),
        "",
        "## Missingness in Controls",
        "",
        _df_to_md(missing_controls),
        "",
    ]
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--narrative", default=DEFAULT_NARRATIVE)
    parser.add_argument("--patents", default=DEFAULT_PATENTS)
    parser.add_argument("--controls", default=DEFAULT_CONTROLS)
    parser.add_argument("--lookup", default=DEFAULT_LOOKUP)
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--patent-buffer-years", type=int, default=DEFAULT_PATENT_BUFFER_YEARS)
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--qc", default=DEFAULT_QC)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    narrative = pd.read_parquet(args.narrative).copy()
    narrative["cik"] = narrative["source_cik"].apply(normalize_cik)
    narrative["year"] = pd.to_numeric(narrative["source_year"], errors="coerce").astype(int)
    narrative = narrative.loc[narrative["year"].between(args.start_year, args.end_year)].copy()
    narrative = narrative.sort_values(["cik", "year"]).drop_duplicates(["cik", "year"], keep="last")

    source_rows = len(narrative)
    source_firms = int(narrative["cik"].nunique())

    scaffold = _build_scaffold(narrative["cik"], range(args.start_year, args.end_year + 1))

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
    panel = scaffold.merge(narrative[keep_narrative], on=["cik", "year"], how="left")

    for column in NARRATIVE_COUNT_COLS:
        panel[column] = pd.to_numeric(panel[column], errors="coerce").fillna(0)
    panel["source_window_id"] = panel["source_window_id"].fillna(
        narrative["source_window_id"].dropna().mode().iloc[0]
        if "source_window_id" in narrative and narrative["source_window_id"].notna().any()
        else "annual_10k_2016_2024_clean"
    )
    panel["model_id"] = panel["model_id"].fillna(
        narrative["model_id"].dropna().mode().iloc[0]
        if "model_id" in narrative and narrative["model_id"].notna().any()
        else ""
    )
    panel = _compute_narrative_features(panel)

    patents = pd.read_csv(args.patents).copy()
    patent_panel = _prepare_patent_panel(
        patents,
        ciks=panel["cik"],
        start_year=args.start_year,
        end_year=args.end_year,
        buffer_years=args.patent_buffer_years,
    )
    panel = panel.merge(patent_panel, on=["cik", "year"], how="left")

    controls = pd.read_csv(args.controls).copy()
    controls["cik"] = controls["cik"].apply(normalize_cik)
    controls["year"] = pd.to_numeric(controls["year"], errors="coerce").astype(int)
    controls = controls.loc[controls["year"].between(args.start_year, args.end_year)].copy()
    controls = controls.sort_values(["cik", "year"]).drop_duplicates(["cik", "year"], keep="last")
    keep_controls = ["cik", "year", *[col for col in CONTROL_COLS if col in controls.columns]]
    panel = panel.merge(controls[keep_controls], on=["cik", "year"], how="left")
    if "sic" in panel.columns:
        panel["sic2"] = (pd.to_numeric(panel["sic"], errors="coerce") // 100).astype("Int64")

    lookup = pd.read_csv(args.lookup).copy()
    lookup["cik"] = lookup["cik"].apply(normalize_cik)
    lookup = lookup.sort_values("cik").drop_duplicates("cik", keep="last")
    for col in ["name", "ticker"]:
        if col not in lookup.columns:
            lookup[col] = ""
    panel = panel.merge(lookup[["cik", "name", "ticker"]], on="cik", how="left")

    preferred = [
        "cik",
        "ticker",
        "name",
        "year",
        "gvkey",
        "sic",
        "sic2",
        "doc_count",
        "n_total",
        "n_A",
        "n_S",
        "n_I",
        "ai_total",
        "any_ai_talk",
        "share_A",
        "share_S",
        "share_I",
        "ActShare",
        "SpecShare",
        "SpecMinusAct",
        "AI_Focus",
        "log_1p_A",
        "log_1p_S",
        "log_n_A",
        "log_n_S",
        "has_actionable",
        "has_spec_only",
        "CredAI",
        "A_S",
        "patents_total",
        "patents_ai",
        "ai_share_patents",
        "patents_ai_lag1",
        "patents_ai_lag2",
        "patents_ai_lead0",
        "patents_ai_lead1",
        "patents_ai_lead2",
        "log_patents_ai_lag1",
        "log_patents_ai_lag2",
        "log_patents_ai_lead0",
        "log_patents_ai_lead1",
        "log_patents_ai_lead2",
        "any_pat_lag1",
        "any_pat_lag2",
        "any_pat_0",
        "any_pat_1",
        "any_pat_2",
        "ln_assets",
        "leverage",
        "cash",
        "rd_intensity",
        "capx_at",
        "roa",
        "sales_growth",
        "emp",
        "source_window_id",
        "model_id",
    ]
    ordered_cols = [col for col in preferred if col in panel.columns] + [
        col for col in panel.columns if col not in preferred
    ]
    panel = panel[ordered_cols].sort_values(["cik", "year"]).reset_index(drop=True)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(out_path, index=False)
    _write_qc(Path(args.qc), panel, source_rows=source_rows, source_firms=source_firms)

    print(f"[ever-speaker-panel] wrote {out_path}")
    print(
        f"[ever-speaker-panel] rows={len(panel)} firms={panel['cik'].nunique()} "
        f"zero_talk_rows={(panel['any_ai_talk'] == 0).sum()} positive_talk_rows={(panel['any_ai_talk'] == 1).sum()}"
    )


if __name__ == "__main__":
    main()
