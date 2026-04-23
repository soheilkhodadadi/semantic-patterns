"""Publication run driver for Test 28: public SEC 13F institutional discernment."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
import zipfile

from docx import Document
from dotenv import dotenv_values
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg2
import requests

from semantic_ai_washing.analysis.delivery_table_payloads import _fit_absorbed_ols, to_markdown_table
from semantic_ai_washing.analysis.publication_runs.test_03_post_filing_drift import (
    _add_note,
    _add_title,
    _build_panel_table,
    _set_document_defaults,
    _set_landscape,
)
from semantic_ai_washing.analysis.publication_runs.test_16_construct_variant_screen import (
    _add_construct_variants,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_28_public_13f_institutional_discernment"
)
DEFAULT_PUBLIC_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/public_inputs/sec_13f"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_28_public_13f_institutional_discernment_main_v1"
TEST_ID = "test_28_public_13f_institutional_discernment"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_28_public_13f_institutional_discernment"
SEC_13F_PAGE = "https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets"
SEC_BASE = "https://www.sec.gov"
SEC_HEADERS = {"User-Agent": "semantic-patterns research bot"}
YEARS = list(range(2016, 2026))
SUBSET_SPECS: list[tuple[str, str]] = [
    ("all", "Panel A. Matched 13F sample"),
    ("big", "Panel B. Big-firm 13F sample"),
    ("post", "Panel C. Post-ChatGPT 13F sample"),
]
PREDICTOR_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch", "PatentMismatch"),
    ("LowCredibility", "LowCredibility"),
    ("A_S", "A/S ratio"),
]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("io_share_13f_t1", "13F ownership share (t+1)"),
    ("delta_io_share_13f_t1", "Change in 13F ownership share (t:t+1)"),
    ("log_13f_holders_t1", "Log(1+13F holders) (t+1)"),
    ("hhi_13f_t1", "13F holder concentration HHI (t+1)"),
]
CONTROL_SPECS = ["AI_Focus", "ln_assets", "cash", "leverage", "roa"]
Q4_LINK_RE = re.compile(r'<a[^>]+href="([^"]+\.zip)"[^>]*>(.*?)</a>', flags=re.I | re.S)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--public-root", type=Path, default=DEFAULT_PUBLIC_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--dotenv-path", type=Path, default=REPO_ROOT / ".env")
    return parser.parse_args()


def _base_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 8,
        }
    )


def _stars(p_value: float | None) -> str:
    if p_value is None or not math.isfinite(p_value):
        return ""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def _coef_cell(coef: float | None, se: float | None, p_value: float | None) -> str:
    if coef is None or se is None or not math.isfinite(coef) or not math.isfinite(se):
        return ""
    return f"{coef:.4f}{_stars(p_value)} ({se:.4f})"


def _wrds_connection(dotenv_path: Path) -> psycopg2.extensions.connection:
    values = dotenv_values(dotenv_path)
    return psycopg2.connect(
        dbname="wrds",
        user=values["WRDS_USER"],
        password=values["WRDS_PASS"],
        host=values["WRDS_DB_HOST"],
        port=int(values["WRDS_DB_PORT"]),
        connect_timeout=15,
    )


def _load_panel(path: Path) -> pd.DataFrame:
    panel = pd.read_parquet(path).copy()
    panel = _add_construct_variants(panel)
    panel["ticker"] = panel["ticker"].astype(str).str.upper().str.strip()
    panel["gvkey"] = panel["gvkey"].astype(str).str.strip()
    panel["permno"] = pd.to_numeric(panel["permno"], errors="coerce").astype("Int64")
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")
    panel["year_end_market_date"] = pd.to_datetime(panel["year_end_market_date"], errors="coerce")
    for column in [*CONTROL_SPECS, "A_S", "PatentMismatch", "LowCredibility", "AI_Focus", "market_cap_year_end", "shrout"]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    panel = panel.loc[panel["year"].between(2016, 2024, inclusive="both")].copy()
    panel = panel.loc[panel["any_ai_talk"].fillna(0).astype(int).eq(1)].copy()
    yearly_median_market_cap = panel.groupby("year")["market_cap_year_end"].transform("median")
    panel["big"] = (
        panel["market_cap_year_end"].notna()
        & yearly_median_market_cap.notna()
        & panel["market_cap_year_end"].gt(yearly_median_market_cap)
    )
    panel["post_chatgpt"] = panel["year"].ge(2023).astype(int)
    return panel


def _pull_year_end_cusips(dotenv_path: Path, permnos: list[int]) -> pd.DataFrame:
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(
            """
            select
                permno,
                namedt,
                nameenddt,
                ticker,
                ncusip,
                cusip
            from crsp.stocknames
            where permno = any(%s)
            """,
            conn,
            params=(permnos,),
        )
    finally:
        conn.close()
    return frame


def _link_panel_to_cusip(panel: pd.DataFrame, stocknames: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    names = stocknames.copy()
    names["permno"] = pd.to_numeric(names["permno"], errors="coerce").astype("Int64")
    names["namedt"] = pd.to_datetime(names["namedt"], errors="coerce")
    names["nameenddt"] = pd.to_datetime(names["nameenddt"], errors="coerce")
    names["ncusip8"] = names["ncusip"].astype(str).str.replace(r"\W", "", regex=True).str[:8]
    merged = panel.merge(names[["permno", "namedt", "nameenddt", "ncusip8"]], on="permno", how="left")
    merged = merged.loc[
        merged["year_end_market_date"].notna()
        & merged["namedt"].notna()
        & merged["nameenddt"].notna()
        & merged["year_end_market_date"].ge(merged["namedt"])
        & merged["year_end_market_date"].le(merged["nameenddt"])
    ].copy()
    merged = merged.sort_values(["gvkey", "year", "namedt", "nameenddt"]).drop_duplicates(["gvkey", "year"], keep="last")
    summary = {
        "panel_rows": int(len(panel)),
        "linked_rows": int(len(merged)),
        "linked_firms": int(merged["gvkey"].nunique()),
        "linked_cusips": int(merged["ncusip8"].nunique()),
    }
    return merged, summary


def _fetch_q4_urls() -> dict[int, str]:
    response = requests.get(SEC_13F_PAGE, headers=SEC_HEADERS, timeout=60)
    response.raise_for_status()
    html = response.text
    year_map: dict[int, str] = {}
    for href, text_html in Q4_LINK_RE.findall(html):
        text = " ".join(re.sub(r"<[^>]+>", " ", text_html).split())
        m = re.match(r"^(\d{4})\s+", text)
        if not m:
            continue
        year = int(m.group(1))
        if ("Q4" in text) or ("December" in text):
            year_map[year] = SEC_BASE + href
    missing = [year for year in YEARS if year not in year_map]
    if missing:
        raise RuntimeError(f"Missing Q4 13F URLs for years: {missing}")
    return year_map


def _download_cached(url: str, dest: Path) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, headers=SEC_HEADERS, stream=True, timeout=120) as response:
        response.raise_for_status()
        with dest.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)


def _read_submission_map(zf: zipfile.ZipFile) -> pd.DataFrame:
    with zf.open("SUBMISSION.tsv") as handle:
        sub = pd.read_csv(
            handle,
            sep="\t",
            dtype={"ACCESSION_NUMBER": str, "SUBMISSIONTYPE": str, "CIK": str},
            usecols=["ACCESSION_NUMBER", "FILING_DATE", "SUBMISSIONTYPE", "CIK", "PERIODOFREPORT"],
        )
    sub = sub.loc[sub["SUBMISSIONTYPE"].isin(["13F-HR", "13F-HR/A"])].copy()
    sub["FILING_DATE"] = pd.to_datetime(sub["FILING_DATE"], format="%d-%b-%Y", errors="coerce")
    sub["PERIODOFREPORT"] = pd.to_datetime(sub["PERIODOFREPORT"], format="%d-%b-%Y", errors="coerce")
    sub = sub.sort_values(["CIK", "PERIODOFREPORT", "FILING_DATE", "ACCESSION_NUMBER"])
    sub = sub.drop_duplicates(["CIK", "PERIODOFREPORT"], keep="last")
    return sub[["ACCESSION_NUMBER", "CIK", "PERIODOFREPORT", "FILING_DATE"]].copy()


def _aggregate_q4_metrics(zip_path: Path, year: int, relevant_cusips: set[str]) -> tuple[pd.DataFrame, dict[str, object]]:
    with zipfile.ZipFile(zip_path) as zf:
        submission_map = _read_submission_map(zf)
        valid_accessions = set(submission_map["ACCESSION_NUMBER"].tolist())
        chunks: list[pd.DataFrame] = []
        rows_scanned = 0
        matched_rows = 0
        with zf.open("INFOTABLE.tsv") as handle:
            for chunk in pd.read_csv(
                handle,
                sep="\t",
                dtype={
                    "ACCESSION_NUMBER": str,
                    "CUSIP": str,
                    "SSHPRNAMTTYPE": str,
                },
                usecols=["ACCESSION_NUMBER", "CUSIP", "SSHPRNAMT", "SSHPRNAMTTYPE"],
                chunksize=750_000,
            ):
                rows_scanned += len(chunk)
                chunk["cusip8"] = chunk["CUSIP"].astype(str).str.replace(r"\W", "", regex=True).str[:8]
                chunk = chunk.loc[
                    chunk["SSHPRNAMTTYPE"].eq("SH")
                    & chunk["ACCESSION_NUMBER"].isin(valid_accessions)
                    & chunk["cusip8"].isin(relevant_cusips)
                ].copy()
                if chunk.empty:
                    continue
                chunk["SSHPRNAMT"] = pd.to_numeric(chunk["SSHPRNAMT"], errors="coerce")
                chunk = chunk.dropna(subset=["SSHPRNAMT"])
                if chunk.empty:
                    continue
                matched_rows += len(chunk)
                chunks.append(chunk[["ACCESSION_NUMBER", "cusip8", "SSHPRNAMT"]])
    if not chunks:
        empty = pd.DataFrame(columns=["year", "cusip8", "total_13f_shares", "n_13f_holders", "hhi_13f", "top1_holder_share"])
        return empty, {
            "year": year,
            "zip_path": str(zip_path),
            "submission_count": int(len(submission_map)),
            "rows_scanned": int(rows_scanned),
            "matched_rows": 0,
            "issuer_matches": 0,
        }
    holdings = pd.concat(chunks, ignore_index=True).merge(submission_map[["ACCESSION_NUMBER", "CIK"]], on="ACCESSION_NUMBER", how="left")
    holdings = holdings.dropna(subset=["CIK"]).copy()
    manager_issuer = holdings.groupby(["cusip8", "CIK"], as_index=False)["SSHPRNAMT"].sum()
    manager_issuer["total_by_cusip"] = manager_issuer.groupby("cusip8")["SSHPRNAMT"].transform("sum")
    manager_issuer["holder_share"] = manager_issuer["SSHPRNAMT"] / manager_issuer["total_by_cusip"]
    issuer = manager_issuer.groupby("cusip8", as_index=False).agg(
        total_13f_shares=("SSHPRNAMT", "sum"),
        n_13f_holders=("CIK", "nunique"),
        hhi_13f=("holder_share", lambda s: float(np.square(s).sum())),
        top1_holder_share=("holder_share", "max"),
    )
    issuer["year"] = year
    summary = {
        "year": year,
        "zip_path": str(zip_path),
        "submission_count": int(len(submission_map)),
        "rows_scanned": int(rows_scanned),
        "matched_rows": int(matched_rows),
        "issuer_matches": int(len(issuer)),
        "holder_pairs": int(len(manager_issuer)),
    }
    return issuer, summary


def _build_q4_issuer_metrics(
    public_root: Path,
    relevant_cusips_by_year: dict[int, set[str]],
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    url_map = _fetch_q4_urls()
    raw_dir = public_root / "raw_zips"
    agg_dir = public_root / "annual_q4_issuer_metrics"
    raw_dir.mkdir(parents=True, exist_ok=True)
    agg_dir.mkdir(parents=True, exist_ok=True)
    frames: list[pd.DataFrame] = []
    summaries: list[dict[str, object]] = []
    for year in YEARS:
        zip_url = url_map[year]
        zip_name = zip_url.rsplit("/", 1)[-1]
        zip_path = raw_dir / zip_name
        aggregate_path = agg_dir / f"q4_issuer_metrics_{year}.parquet"
        summary_path = agg_dir / f"q4_issuer_metrics_{year}_summary.json"
        _download_cached(zip_url, zip_path)
        if aggregate_path.exists() and summary_path.exists():
            issuer = pd.read_parquet(aggregate_path)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        else:
            issuer, summary = _aggregate_q4_metrics(zip_path, year, relevant_cusips_by_year.get(year, set()))
            issuer.to_parquet(aggregate_path, index=False)
            summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        frames.append(issuer)
        summaries.append(summary)
    nonempty_frames = [frame for frame in frames if not frame.empty]
    if not nonempty_frames:
        empty = pd.DataFrame(
            columns=["year", "cusip8", "total_13f_shares", "n_13f_holders", "hhi_13f", "top1_holder_share"]
        )
        return empty, summaries
    return pd.concat(nonempty_frames, ignore_index=True), summaries


def _prepare_ownership_panel(
    linked_panel: pd.DataFrame,
    q4_metrics: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, object]]:
    features = linked_panel[["gvkey", "permno", "ticker", "year", "ncusip8", "shrout"]].drop_duplicates().copy()
    features = features.merge(q4_metrics, on=["year", "ncusip8"], how="left")
    features["shrout_shares"] = features["shrout"] * 1000.0
    features["io_share_13f_q4"] = features["total_13f_shares"] / features["shrout_shares"].where(features["shrout_shares"].gt(0))
    features["io_share_13f_q4"] = features["io_share_13f_q4"].clip(lower=0, upper=2)
    features["n_13f_holders"] = pd.to_numeric(features["n_13f_holders"], errors="coerce")
    features["log_13f_holders_q4"] = np.log1p(features["n_13f_holders"].fillna(0.0))
    features["hhi_13f_q4"] = features["hhi_13f"].clip(lower=0, upper=1)
    lead = features[["gvkey", "year", "io_share_13f_q4", "log_13f_holders_q4", "hhi_13f_q4"]].copy()
    lead["year"] = lead["year"] - 1
    lead = lead.rename(
        columns={
            "io_share_13f_q4": "io_share_13f_t1",
            "log_13f_holders_q4": "log_13f_holders_t1",
            "hhi_13f_q4": "hhi_13f_t1",
        }
    )
    panel = linked_panel.merge(features[["gvkey", "year", "io_share_13f_q4", "log_13f_holders_q4", "hhi_13f_q4"]], on=["gvkey", "year"], how="left")
    panel = panel.merge(lead, on=["gvkey", "year"], how="left")
    panel["delta_io_share_13f_t1"] = panel["io_share_13f_t1"] - panel["io_share_13f_q4"]
    summary = {
        "ownership_current_rows": int(panel["io_share_13f_q4"].notna().sum()),
        "ownership_t1_rows": int(panel["io_share_13f_t1"].notna().sum()),
        "ownership_t1_firms": int(panel.loc[panel["io_share_13f_t1"].notna(), "gvkey"].nunique()),
        "holder_t1_rows": int(panel["log_13f_holders_t1"].notna().sum()),
        "concentration_t1_rows": int(panel["hhi_13f_t1"].notna().sum()),
    }
    return panel, summary


def _subset_sample(sample: pd.DataFrame, subset_key: str) -> pd.DataFrame:
    matched = sample.loc[sample["io_share_13f_t1"].notna()].copy()
    if subset_key == "big":
        return matched.loc[matched["big"].fillna(False)].copy()
    if subset_key == "post":
        return matched.loc[matched["post_chatgpt"].eq(1)].copy()
    return matched


def _fit_rows(sample: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for subset_key, subset_label in SUBSET_SPECS:
        subset = _subset_sample(sample, subset_key)
        for outcome, outcome_label in OUTCOME_SPECS:
            for predictor, predictor_label in PREDICTOR_SPECS:
                needed = [outcome, predictor, "gvkey", "year", *CONTROL_SPECS]
                use = subset.dropna(subset=needed).copy()
                if use.empty:
                    rows.append(
                        {
                            "subset_key": subset_key,
                            "subset_label": subset_label,
                            "outcome": outcome,
                            "outcome_label": outcome_label,
                            "predictor": predictor,
                            "predictor_label": predictor_label,
                            "nobs": 0,
                            "outcome_mean": math.nan,
                            "params": {},
                            "bse": {},
                            "pvalues": {},
                        }
                    )
                    continue
                within_firm_nunique = use.groupby("gvkey")[predictor].nunique(dropna=True)
                if not (within_firm_nunique > 1).any():
                    rows.append(
                        {
                            "subset_key": subset_key,
                            "subset_label": subset_label,
                            "outcome": outcome,
                            "outcome_label": outcome_label,
                            "predictor": predictor,
                            "predictor_label": predictor_label,
                            "nobs": 0,
                            "outcome_mean": math.nan,
                            "params": {},
                            "bse": {},
                            "pvalues": {},
                        }
                    )
                    continue
                result, est_sample, _adj_r2 = _fit_absorbed_ols(
                    use,
                    dependent=outcome,
                    rhs_terms=[predictor],
                    absorb_col="gvkey",
                    include_year=True,
                    controls=CONTROL_SPECS,
                )
                rows.append(
                    {
                        "subset_key": subset_key,
                        "subset_label": subset_label,
                        "outcome": outcome,
                        "outcome_label": outcome_label,
                        "predictor": predictor,
                        "predictor_label": predictor_label,
                        "nobs": int(result.nobs),
                        "outcome_mean": float(est_sample[outcome].mean()),
                        "params": result.params.to_dict(),
                        "bse": result.bse.to_dict(),
                        "pvalues": result.pvalues.to_dict(),
                    }
                )
    return rows


def _build_table(rows: list[dict[str, object]]) -> tuple[pd.DataFrame, dict[tuple[str, str, str], dict[str, object]]]:
    keyed = {(row["subset_key"], row["outcome"], row["predictor"]): row for row in rows}
    table_rows: list[dict[str, object]] = []
    for subset_key, subset_label in SUBSET_SPECS:
        table_rows.append(
            {
                "Panel": subset_label,
                "Outcome": "",
                "PatentMismatch": "",
                "LowCredibility": "",
                "A/S ratio": "",
                "Outcome mean": "",
                "Observations": "",
            }
        )
        for outcome, outcome_label in OUTCOME_SPECS:
            row = {"Panel": "", "Outcome": outcome_label}
            for predictor, predictor_label in PREDICTOR_SPECS:
                result = keyed[(subset_key, outcome, predictor)]
                row[predictor_label] = _coef_cell(
                    result["params"].get(predictor),
                    result["bse"].get(predictor),
                    result["pvalues"].get(predictor),
                )
            base = keyed[(subset_key, outcome, PREDICTOR_SPECS[0][0])]
            row["Outcome mean"] = f"{base['outcome_mean']:.3f}" if math.isfinite(base["outcome_mean"]) else ""
            row["Observations"] = str(base["nobs"])
            table_rows.append(row)
    return pd.DataFrame(table_rows), keyed


def _render_markdown(table_df: pd.DataFrame) -> str:
    headers = table_df.columns.tolist()
    rows = [[str(value) for value in row] for row in table_df.values.tolist()]
    return to_markdown_table(headers, rows)


def _render_latex(table_df: pd.DataFrame) -> str:
    lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Public SEC 13F institutional discernment and low-credibility AI disclosure}",
        "\\small",
        "\\begin{tabular}{llcccrr}",
        "\\hline",
        "Panel & Outcome & PatentMismatch & LowCredibility & A/S ratio & Outcome mean & Obs. \\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        if row["Panel"]:
            lines.append("\\multicolumn{7}{l}{\\textit{" + str(row["Panel"]).replace("&", "\\&") + "}} \\")
            continue
        lines.append(
            " & ".join(
                [
                    "",
                    str(row["Outcome"]).replace("_", "\\_"),
                    str(row["PatentMismatch"]),
                    str(row["LowCredibility"]),
                    str(row["A/S ratio"]),
                    str(row["Outcome mean"]),
                    str(row["Observations"]),
                ]
            )
            + " \\")
    lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: Outcomes use public SEC Form 13F year-end holdings built from the official SEC structured data sets and linked to the annual panel through CRSP year-end CUSIP history. Ownership share is aggregate 13F shares divided by CRSP shares outstanding. Holder breadth is log one plus the number of reporting managers, and concentration is the issuer-level HHI of manager shares. Specifications absorb firm and year fixed effects, include current controls, and cluster standard errors by firm.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines) + "\n"


def _write_docx(
    path: Path,
    table_df: pd.DataFrame,
    linkage_summary: dict[str, object],
    ownership_summary: dict[str, object],
    sec_summaries: list[dict[str, object]],
) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Test 28. Public SEC 13F institutional discernment")
    _add_note(
        document,
        (
            "This table asks whether public 13F institutional ownership is lower, shrinking, or more concentrated "
            "among low-credibility AI disclosers. The ownership inputs come from the official SEC structured Form 13F data sets."
        ),
    )
    _add_note(
        document,
        (
            f"CRSP-linked panel rows = {linkage_summary['linked_rows']:,} across {linkage_summary['linked_firms']:,} firms; "
            f"t+1 ownership-linked rows = {ownership_summary['ownership_t1_rows']:,} across {ownership_summary['ownership_t1_firms']:,} firms."
        ),
    )
    _add_note(
        document,
        (
            f"Q4 SEC data years processed = {len(sec_summaries):,}; total issuer matches across annual aggregates = "
            f"{sum(item['issuer_matches'] for item in sec_summaries):,}."
        ),
    )
    headers = table_df.columns.tolist()
    rows = [[(str(value), False) for value in row] for row in table_df.values.tolist()]
    _build_panel_table(document, headers, rows)
    document.save(path)


def _write_figure(rows: list[dict[str, object]], *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(1, 4, figsize=(12.8, 3.8), sharey=False)
    subset_order = [label for _key, label in SUBSET_SPECS]
    for ax, (outcome, outcome_label) in zip(axes, OUTCOME_SPECS, strict=True):
        subset_rows = [
            row for row in rows if row["outcome"] == outcome and row["predictor"] == "PatentMismatch"
        ]
        subset_rows = sorted(subset_rows, key=lambda row: subset_order.index(row["subset_label"]))
        x = list(range(len(subset_rows)))
        coef = [row["params"].get("PatentMismatch", math.nan) for row in subset_rows]
        err = [1.96 * row["bse"].get("PatentMismatch", math.nan) for row in subset_rows]
        ax.errorbar(x, coef, yerr=err, fmt="o", capsize=3, color="#1f4e79")
        ax.axhline(0, color="black", linewidth=0.9, linestyle="--")
        ax.set_xticks(x, [row["subset_label"].replace("Panel ", "") for row in subset_rows], rotation=20, ha="right")
        ax.set_title(outcome_label)
        ax.set_ylabel("PatentMismatch coefficient")
    fig.tight_layout()
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)


def _write_writer_packet(
    path: Path,
    ownership_summary: dict[str, object],
    sec_summaries: list[dict[str, object]],
    keyed: dict[tuple[str, str, str], dict[str, object]],
) -> None:
    all_share = keyed[("all", "io_share_13f_t1", "PatentMismatch")]
    all_delta = keyed[("all", "delta_io_share_13f_t1", "PatentMismatch")]
    all_breadth = keyed[("all", "log_13f_holders_t1", "PatentMismatch")]
    lines = [
        "# Writer Packet: Test 28 public SEC 13F institutional discernment",
        "",
        "## Setup",
        "",
        "- Source: official SEC Form 13F structured data sets.",
        "- Frequency choice: year-end Q4 holdings snapshots, linked to the annual panel through CRSP historical CUSIP mapping.",
        "- Outcomes: next-year 13F ownership share, change in ownership share, next-year holder breadth, and next-year holder concentration.",
        "",
        "## Density",
        "",
        f"- Q4 years processed: `{len(sec_summaries):,}`.",
        f"- Total t+1 ownership-linked rows: `{ownership_summary['ownership_t1_rows']:,}` across `{ownership_summary['ownership_t1_firms']:,}` firms.",
        f"- Holder breadth rows: `{ownership_summary['holder_t1_rows']:,}`; concentration rows: `{ownership_summary['concentration_t1_rows']:,}`.",
        "",
        "## Main read",
        "",
        f"- All-sample next-year 13F ownership share on `PatentMismatch`: `{all_share['params'].get('PatentMismatch', math.nan):.4f}{_stars(all_share['pvalues'].get('PatentMismatch'))}` (p=`{all_share['pvalues'].get('PatentMismatch', math.nan):.3f}`).",
        f"- All-sample change in 13F ownership share on `PatentMismatch`: `{all_delta['params'].get('PatentMismatch', math.nan):.4f}{_stars(all_delta['pvalues'].get('PatentMismatch'))}` (p=`{all_delta['pvalues'].get('PatentMismatch', math.nan):.3f}`).",
        f"- All-sample next-year holder breadth on `PatentMismatch`: `{all_breadth['params'].get('PatentMismatch', math.nan):.4f}{_stars(all_breadth['pvalues'].get('PatentMismatch'))}` (p=`{all_breadth['pvalues'].get('PatentMismatch', math.nan):.3f}`).",
        "",
        "## Placement",
        "",
        "- Best use: public-ownership appendix or main-text support table if institutional discernment is clear.",
        "- Caveat to state explicitly: SEC 13F covers only reporting managers and does not equal total institutional ownership.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(path: Path, rows: list[dict[str, object]]) -> None:
    lines = [
        "# Result Notes: Test 28 public SEC 13F institutional discernment",
        "",
        "This packet links public SEC 13F year-end ownership measures to later low-credibility AI disclosure outcomes in the AI-talking annual panel.",
        "",
    ]
    for subset_key, subset_label in SUBSET_SPECS:
        lines.append(f"## {subset_label}")
        for outcome, outcome_label in OUTCOME_SPECS:
            lines.append(f"### {outcome_label}")
            for predictor, predictor_label in PREDICTOR_SPECS:
                row = next(
                    item
                    for item in rows
                    if item["subset_key"] == subset_key and item["outcome"] == outcome and item["predictor"] == predictor
                )
                coef = row["params"].get(predictor, math.nan)
                se = row["bse"].get(predictor, math.nan)
                p_value = row["pvalues"].get(predictor, math.nan)
                if math.isfinite(coef):
                    lines.append(
                        f"- {predictor_label}: {coef:.4f}{_stars(p_value)} "
                        f"(SE {se:.4f}, p={p_value:.3f}, n={row['nobs']:,})."
                    )
                else:
                    lines.append(f"- {predictor_label}: insufficient sample.")
            lines.append("")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    args = _parse_args()
    run_root = args.test_root / args.run_id
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    args.paper_root.mkdir(parents=True, exist_ok=True)
    args.public_root.mkdir(parents=True, exist_ok=True)
    for subdir in ["docx", "latex", "tables", "figures", "writer_packets", "snippets"]:
        (args.paper_root / subdir).mkdir(parents=True, exist_ok=True)

    panel = _load_panel(args.annual_panel)
    permnos = sorted(panel["permno"].dropna().astype(int).unique().tolist())
    stocknames = _pull_year_end_cusips(args.dotenv_path, permnos)
    linked_panel, linkage_summary = _link_panel_to_cusip(panel, stocknames)
    relevant_cusips_by_year = {
        int(year): set(group["ncusip8"].dropna().astype(str).tolist())
        for year, group in linked_panel.groupby("year")
    }
    q4_metrics = _build_q4_issuer_metrics(args.public_root, relevant_cusips_by_year)
    issuer_metrics, sec_summaries = q4_metrics
    issuer_metrics = issuer_metrics.rename(columns={"cusip8": "ncusip8"})
    sample, ownership_summary = _prepare_ownership_panel(linked_panel, issuer_metrics)
    rows = _fit_rows(sample)
    table_df, keyed = _build_table(rows)
    markdown = _render_markdown(table_df)
    latex = _render_latex(table_df)

    stem = f"{TEST_ID}_{args.run_id}"
    docx_path = run_root / f"{stem}.docx"
    tex_path = run_root / f"{stem}.tex"
    csv_path = run_root / f"{stem}.csv"
    png_path = run_root / f"{stem}.png"
    pdf_path = run_root / f"{stem}.pdf"
    md_path = run_root / f"{stem}.md"
    writer_path = run_root / f"{stem}_writer_packet.md"
    notes_path = run_root / f"{stem}_result_notes.md"

    _write_docx(docx_path, table_df, linkage_summary, ownership_summary, sec_summaries)
    _write_figure(rows, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(writer_path, ownership_summary, sec_summaries, keyed)
    _write_result_notes(notes_path, rows)
    tex_path.write_text(latex, encoding="utf-8")
    csv_path.write_text(table_df.to_csv(index=False), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")

    for source_path, subdir in [
        (docx_path, "docx"),
        (tex_path, "latex"),
        (csv_path, "tables"),
        (png_path, "figures"),
        (writer_path, "writer_packets"),
        (notes_path, "snippets"),
    ]:
        shutil.copy2(source_path, args.paper_root / subdir / source_path.name)

    manifest = {
        "test_id": TEST_ID,
        "module_path": MODULE_PATH,
        "run_id": args.run_id,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "annual_panel": str(args.annual_panel),
            "public_root": str(args.public_root),
            "sec_13f_page": SEC_13F_PAGE,
            "crsp_source": "crsp.stocknames",
        },
        "linkage_summary": linkage_summary,
        "ownership_summary": ownership_summary,
        "sec_year_summaries": sec_summaries,
        "outputs": {
            "docx": str(docx_path),
            "latex": str(tex_path),
            "csv": str(csv_path),
            "figure_png": str(png_path),
            "figure_pdf": str(pdf_path),
            "writer_packet": str(writer_path),
            "result_notes": str(notes_path),
        },
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
