"""Publication run driver for Test 24: science/technology appointment response."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

from docx import Document
from dotenv import dotenv_values
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2

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
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/v3_2/test_runs/test_24_scitech_appointment_response"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated/v3_2"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_aiw_v3_2_test_24_scitech_appointment_response_main_v1"
TEST_ID = "test_24_scitech_appointment_response"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.test_24_scitech_appointment_response"

VARIANT_SPECS: list[tuple[str, str]] = [
    ("PatentMismatch", "PatentMismatch"),
    ("LowCredibility", "LowCredibility"),
    ("A_S", "A/S ratio"),
]
OUTCOME_SPECS: list[tuple[str, str]] = [
    ("scitech_appoint_t1_t2", "Any science/tech appointment (t+1:t+2)"),
    ("c_level_scitech_appoint_t1_t2", "C-level science/tech appointment (t+1:t+2)"),
    ("tech_lead_appoint_t1_t2", "Technology-lead appointment (t+1:t+2)"),
]
CONTROL_SPECS = ["AI_Focus", "ln_assets", "cash", "leverage", "roa"]
TECH_LEAD_REGEX = re.compile(
    r"chief (?:technology|technical|information|digital|data|science|innovation|product) officer|"
    r"chief ai officer|chief artificial intelligence officer|"
    r"head of (?:ai|artificial intelligence|data|machine learning)|"
    r"(?:vice president|vp|senior vp|executive vp) engineering",
    re.IGNORECASE,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--dotenv-path", type=Path, default=REPO_ROOT / ".env")
    parser.add_argument(
        "--size-subset",
        choices=["all", "nonbig", "big"],
        default="all",
        help="Optional yearly-median market-cap split inside the AI-talking annual sample.",
    )
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


def _normalize_cik(value: object) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    return digits.zfill(10) if digits else ""


def _clean_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


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
    panel["cik"] = panel["cik"].map(_normalize_cik)
    panel["year"] = pd.to_numeric(panel["year"], errors="coerce").astype("Int64")
    if "sic2" not in panel.columns and "sic" in panel.columns:
        sic = pd.to_numeric(panel["sic"], errors="coerce")
        panel["sic2"] = (sic // 100).astype("Int64")
    for column in [*CONTROL_SPECS, "A_S", "PatentMismatch", "LowCredibility", "AI_Focus"]:
        if column in panel.columns:
            panel[column] = pd.to_numeric(panel[column], errors="coerce")
    panel = panel.loc[panel["year"].between(2016, 2024, inclusive="both")].copy()
    panel = panel.loc[panel["any_ai_talk"].fillna(0).astype(int).eq(1)].copy()
    return panel


def _pull_changes(panel: pd.DataFrame, *, dotenv_path: Path) -> pd.DataFrame:
    ciks = sorted({cik for cik in panel["cik"].dropna().unique().tolist() if cik})
    if not ciks:
        return pd.DataFrame()
    query = """
        select
            company_fkey,
            action,
            title_report,
            title_standard,
            is_scitech_pers,
            is_c_level,
            is_bdmem_pers,
            eff_date,
            file_date
        from audit.feed17_director_and_officer_chan
        where file_date >= date '2016-01-01'
          and company_fkey = any(%s)
          and action = 'Appointed'
    """
    conn = _wrds_connection(dotenv_path)
    try:
        frame = pd.read_sql_query(query, conn, params=(ciks,))
    finally:
        conn.close()
    return frame


def _prepare_events(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    if raw.empty:
        empty = pd.DataFrame(
            columns=[
                "cik",
                "year",
                "scitech_appoint",
                "c_level_scitech_appoint",
                "tech_lead_appoint",
                "board_scitech_appoint",
            ]
        )
        return empty, {
            "appointment_rows": 0,
            "appointment_firms": 0,
            "scitech_rows": 0,
            "c_level_scitech_rows": 0,
            "tech_lead_rows": 0,
            "board_scitech_rows": 0,
            "firm_year_any_scitech": 0,
            "firm_year_c_level_scitech": 0,
            "firm_year_tech_lead": 0,
            "firm_year_board_scitech": 0,
        }
    use = raw.copy()
    use["cik"] = use["company_fkey"].map(_normalize_cik)
    for column in ["is_scitech_pers", "is_c_level", "is_bdmem_pers"]:
        use[column] = pd.to_numeric(use[column], errors="coerce").fillna(0).astype(int)
    use["title_combo"] = (
        use["title_report"].map(_clean_text) + " " + use["title_standard"].map(_clean_text)
    ).str.strip()
    use["event_date"] = pd.to_datetime(use["eff_date"]).fillna(pd.to_datetime(use["file_date"]))
    use["year"] = use["event_date"].dt.year.astype("Int64")
    use = use.loc[use["year"].between(2016, 2026, inclusive="both")].copy()
    use["scitech_appoint"] = use["is_scitech_pers"].astype(int)
    use["c_level_scitech_appoint"] = (
        use["is_scitech_pers"].eq(1) & use["is_c_level"].eq(1)
    ).astype(int)
    use["tech_lead_appoint"] = (
        use["is_scitech_pers"].eq(1) & use["title_combo"].str.contains(TECH_LEAD_REGEX)
    ).astype(int)
    use["board_scitech_appoint"] = (
        use["is_scitech_pers"].eq(1) & use["is_bdmem_pers"].eq(1)
    ).astype(int)
    event_panel = (
        use.groupby(["cik", "year"], as_index=False)
        .agg(
            scitech_appoint=("scitech_appoint", "max"),
            c_level_scitech_appoint=("c_level_scitech_appoint", "max"),
            tech_lead_appoint=("tech_lead_appoint", "max"),
            board_scitech_appoint=("board_scitech_appoint", "max"),
        )
        .sort_values(["cik", "year"])
        .reset_index(drop=True)
    )
    summary = {
        "appointment_rows": int(len(use)),
        "appointment_firms": int(use["cik"].nunique()),
        "scitech_rows": int(use["scitech_appoint"].sum()),
        "c_level_scitech_rows": int(use["c_level_scitech_appoint"].sum()),
        "tech_lead_rows": int(use["tech_lead_appoint"].sum()),
        "board_scitech_rows": int(use["board_scitech_appoint"].sum()),
        "firm_year_any_scitech": int(event_panel["scitech_appoint"].sum()),
        "firm_year_c_level_scitech": int(event_panel["c_level_scitech_appoint"].sum()),
        "firm_year_tech_lead": int(event_panel["tech_lead_appoint"].sum()),
        "firm_year_board_scitech": int(event_panel["board_scitech_appoint"].sum()),
    }
    return event_panel, summary


def _prepare_sample(panel: pd.DataFrame, event_panel: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    sample = panel.copy()
    current = event_panel.rename(
        columns={
            "scitech_appoint": "scitech_appoint_t",
            "c_level_scitech_appoint": "c_level_scitech_appoint_t",
            "tech_lead_appoint": "tech_lead_appoint_t",
            "board_scitech_appoint": "board_scitech_appoint_t",
        }
    )
    lead1 = event_panel.rename(
        columns={
            "year": "year_plus1",
            "scitech_appoint": "scitech_appoint_lead1",
            "c_level_scitech_appoint": "c_level_scitech_appoint_lead1",
            "tech_lead_appoint": "tech_lead_appoint_lead1",
            "board_scitech_appoint": "board_scitech_appoint_lead1",
        }
    )
    lead2 = event_panel.rename(
        columns={
            "year": "year_plus2",
            "scitech_appoint": "scitech_appoint_lead2",
            "c_level_scitech_appoint": "c_level_scitech_appoint_lead2",
            "tech_lead_appoint": "tech_lead_appoint_lead2",
            "board_scitech_appoint": "board_scitech_appoint_lead2",
        }
    )
    sample["year_plus1"] = pd.to_numeric(sample["year"], errors="coerce") + 1
    sample["year_plus2"] = pd.to_numeric(sample["year"], errors="coerce") + 2
    sample = sample.merge(current, on=["cik", "year"], how="left")
    sample = sample.merge(lead1, on=["cik", "year_plus1"], how="left")
    sample = sample.merge(lead2, on=["cik", "year_plus2"], how="left")
    for base in [
        "scitech_appoint",
        "c_level_scitech_appoint",
        "tech_lead_appoint",
        "board_scitech_appoint",
    ]:
        sample[f"{base}_t1_t2"] = (
            sample[[f"{base}_lead1", f"{base}_lead2"]].fillna(0).max(axis=1).astype(float)
        )
    sample["market_cap_year_end"] = pd.to_numeric(sample.get("market_cap_year_end"), errors="coerce")
    yearly_median_market_cap = sample.groupby("year")["market_cap_year_end"].transform("median")
    sample["nonbig"] = (
        sample["market_cap_year_end"].notna()
        & yearly_median_market_cap.notna()
        & sample["market_cap_year_end"].le(yearly_median_market_cap)
    )
    summary = {
        "sample_rows": int(len(sample)),
        "unique_firms": int(sample["cik"].nunique()),
        "lead1_any_scitech": int(sample["scitech_appoint_lead1"].fillna(0).sum()),
        "lead2_any_scitech": int(sample["scitech_appoint_lead2"].fillna(0).sum()),
        "t1_t2_any_scitech": int(sample["scitech_appoint_t1_t2"].fillna(0).sum()),
        "t1_t2_c_level_scitech": int(sample["c_level_scitech_appoint_t1_t2"].fillna(0).sum()),
        "t1_t2_tech_lead": int(sample["tech_lead_appoint_t1_t2"].fillna(0).sum()),
        "t1_t2_board_scitech": int(sample["board_scitech_appoint_t1_t2"].fillna(0).sum()),
        "nonbig_rows": int(sample["nonbig"].fillna(False).sum()),
        "years": [int(sample["year"].min()), int(sample["year"].max())],
    }
    return sample, summary


def _filter_size_subset(sample: pd.DataFrame, size_subset: str) -> pd.DataFrame:
    if size_subset == "all":
        return sample.copy()
    flag = sample["nonbig"].fillna(False)
    if size_subset == "nonbig":
        return sample.loc[flag].copy()
    return sample.loc[flag.eq(False)].copy()


def _fit_model(sample: pd.DataFrame, outcome: str, variant: str) -> dict[str, object]:
    result, use, adj_r2 = _fit_absorbed_ols(
        sample,
        dependent=outcome,
        rhs_terms=[variant],
        absorb_col="cik",
        include_year=True,
        controls=CONTROL_SPECS,
    )
    return {
        "outcome": outcome,
        "variant": variant,
        "nobs": int(result.nobs),
        "adj_r2": float(adj_r2) if adj_r2 is not None else math.nan,
        "params": result.params.to_dict(),
        "bse": result.bse.to_dict(),
        "pvalues": result.pvalues.to_dict(),
        "outcome_mean": float(use[outcome].mean()),
    }


def _build_results_table(
    rows: list[dict[str, object]],
) -> tuple[pd.DataFrame, dict[tuple[str, str], dict[str, object]]]:
    keyed = {(row["outcome"], row["variant"]): row for row in rows}
    table_rows: list[dict[str, object]] = []
    for outcome, outcome_label in OUTCOME_SPECS:
        row = {"row_label": outcome_label}
        for variant, variant_label in VARIANT_SPECS:
            result = keyed[(outcome, variant)]
            row[variant_label] = _coef_cell(
                result["params"].get(variant),
                result["bse"].get(variant),
                result["pvalues"].get(variant),
            )
        base = keyed[(outcome, VARIANT_SPECS[0][0])]
        row["Outcome mean"] = f"{base['outcome_mean']:.3f}"
        row["Observations"] = str(base["nobs"])
        table_rows.append(row)
    return pd.DataFrame(table_rows), keyed


def _render_table_outputs(table_df: pd.DataFrame) -> tuple[str, str]:
    headers = ["Outcome"] + [label for _variant, label in VARIANT_SPECS] + ["Outcome mean", "Observations"]
    md_rows = [
        [
            row["row_label"],
            *[row[label] for _variant, label in VARIANT_SPECS],
            row["Outcome mean"],
            row["Observations"],
        ]
        for _, row in table_df.iterrows()
    ]
    md = to_markdown_table(headers, [[str(value) for value in row] for row in md_rows])
    latex_lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Later science and technology leadership appointments}",
        "\\begin{tabular}{lccc rr}",
        "\\hline",
        "Outcome & PatentMismatch & LowCredibility & A/S ratio & Outcome mean & Obs. \\\\",
        "\\hline",
    ]
    for _, row in table_df.iterrows():
        latex_lines.append(
            " & ".join(
                [
                    str(row["row_label"]),
                    *[str(row[label]) for _variant, label in VARIANT_SPECS],
                    str(row["Outcome mean"]),
                    str(row["Observations"]),
                ]
            )
            + " \\\\"
        )
    latex_lines.extend(
        [
            "\\hline",
            "\\end{tabular}",
            "\\begin{flushleft}",
            "\\footnotesize Notes: Outcomes measure later science/technology leadership additions from Audit Analytics officer/director change records using appointed-role events only. The broad outcome uses the provider's `is_scitech_pers` tag. The narrower cuts isolate c-level science/technology appointments and technology-lead titles such as CTO, CIO, chief digital, chief data, chief science, and senior engineering leadership. Specifications use the AI-talking annual sample, firm fixed effects, year fixed effects, current controls, and firm-clustered standard errors.",
            "\\end{flushleft}",
            "\\end{table}",
        ]
    )
    return md, "\n".join(latex_lines) + "\n"


def _write_docx(
    *,
    output_path: Path,
    table_df: pd.DataFrame,
    event_summary: dict[str, object],
    sample_summary: dict[str, object],
    subset_label: str,
) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, f"Test 24. Science and technology appointment response ({subset_label})")
    _add_note(
        document,
        (
            "This table asks whether low-credibility AI disclosure is followed by later science and "
            "technology leadership additions. The source is Audit Analytics officer/director change "
            "records, limited to appointed-role events in the ever-speaker firm universe."
        ),
    )
    _add_note(
        document,
        (
            f"Appointment rows = {event_summary['appointment_rows']:,}; appointment firms = {event_summary['appointment_firms']:,}; "
            f"subset rows = {sample_summary['subset_rows']:,}; subset firms = {sample_summary['subset_firms']:,}."
        ),
    )
    headers = ["Outcome"] + [label for _variant, label in VARIANT_SPECS] + ["Outcome mean", "Observations"]
    table_rows = [
        [
            (str(row["row_label"]), False),
            *[(str(row[label]), False) for _variant, label in VARIANT_SPECS],
            (str(row["Outcome mean"]), False),
            (str(row["Observations"]), False),
        ]
        for _, row in table_df.iterrows()
    ]
    _build_panel_table(document, headers, table_rows)
    document.save(output_path)


def _write_figure(sample: pd.DataFrame, *, png_path: Path, pdf_path: Path) -> None:
    _base_style()
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.0), sharey=False)
    mismatch = sample["PatentMismatch"].fillna(0).astype(int)
    broad = sample.groupby(mismatch)[["scitech_appoint_lead1", "scitech_appoint_lead2"]].mean().fillna(0)
    c_level = (
        sample.groupby(mismatch)[["c_level_scitech_appoint_lead1", "c_level_scitech_appoint_lead2"]]
        .mean()
        .fillna(0)
    )
    horizons = ["t+1", "t+2"]
    for ax, frame, title in [
        (axes[0], broad, "Any science/tech appointment"),
        (axes[1], c_level, "C-level science/tech appointment"),
    ]:
        for key, label, color in [(0, "Non-mismatch", "#7a8793"), (1, "Mismatch", "#1f4e79")]:
            values = frame.loc[key].tolist() if key in frame.index else [0.0, 0.0]
            ax.plot(horizons, values, marker="o", linewidth=2, label=label, color=color)
        ax.set_title(title)
        ax.set_ylabel("Raw future appointment rate")
        ax.set_ylim(bottom=0)
        ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)


def _write_writer_packet(
    *,
    output_path: Path,
    event_summary: dict[str, object],
    sample_summary: dict[str, object],
    keyed: dict[tuple[str, str], dict[str, object]],
    subset_label: str,
) -> None:
    broad = keyed[("scitech_appoint_t1_t2", "PatentMismatch")]
    c_level = keyed[("c_level_scitech_appoint_t1_t2", "PatentMismatch")]
    tech_lead = keyed[("tech_lead_appoint_t1_t2", "PatentMismatch")]
    lines = [
        "# Writer Packet: Test 24 science/technology appointment response",
        "",
        "## Setup",
        "",
        f"- Sample: AI-talking annual panel, 2016-2024 ({subset_label}).",
        "- External source: Audit Analytics `feed17_director_and_officer_chan`.",
        "- Event filter: appointed roles only.",
        "- Broad science/technology appointment uses `is_scitech_pers = 1`.",
        "- Narrower cuts isolate c-level science/technology appointments and title-based technology-lead appointments.",
        "",
        "## Density",
        "",
        f"- Appointment rows in the panel universe: `{event_summary['appointment_rows']:,}` across `{event_summary['appointment_firms']:,}` firms.",
        f"- Science/technology appointment rows: `{event_summary['scitech_rows']:,}`; c-level: `{event_summary['c_level_scitech_rows']:,}`; tech-lead: `{event_summary['tech_lead_rows']:,}`.",
        f"- Future-window incidence in the selected sample: broad `{sample_summary['subset_t1_t2_any_scitech']:,}`, c-level `{sample_summary['subset_t1_t2_c_level_scitech']:,}`, tech-lead `{sample_summary['subset_t1_t2_tech_lead']:,}`.",
        "",
        "## Main read",
        "",
        f"- PatentMismatch -> any science/tech appointment (t+1:t+2): `{broad['params'].get('PatentMismatch', math.nan):.4f}{_stars(broad['pvalues'].get('PatentMismatch'))}` with p-value `{broad['pvalues'].get('PatentMismatch', math.nan):.3f}`.",
        f"- PatentMismatch -> c-level science/tech appointment (t+1:t+2): `{c_level['params'].get('PatentMismatch', math.nan):.4f}{_stars(c_level['pvalues'].get('PatentMismatch'))}` with p-value `{c_level['pvalues'].get('PatentMismatch', math.nan):.3f}`.",
        f"- PatentMismatch -> technology-lead appointment (t+1:t+2): `{tech_lead['params'].get('PatentMismatch', math.nan):.4f}{_stars(tech_lead['pvalues'].get('PatentMismatch'))}` with p-value `{tech_lead['pvalues'].get('PatentMismatch', math.nan):.3f}`.",
        "",
        "## Placement",
        "",
        "- Main-text worthy if the appointment response is positive, coherent, and stronger for the narrower c-level / technology-lead cuts.",
        "- Best framing: delayed organizational catch-up, not clean causality.",
    ]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_result_notes(output_path: Path, keyed: dict[tuple[str, str], dict[str, object]]) -> None:
    lines = [
        "# Result Notes: Test 24 science/technology appointment response",
        "",
        "This packet asks whether mismatch firms later add science or technology leadership after making low-credibility AI claims.",
        "",
    ]
    for outcome, outcome_label in OUTCOME_SPECS:
        lines.append(f"## {outcome_label}")
        for variant, variant_label in VARIANT_SPECS:
            result = keyed[(outcome, variant)]
            coef = result["params"].get(variant, math.nan)
            se = result["bse"].get(variant, math.nan)
            p_value = result["pvalues"].get(variant, math.nan)
            if math.isfinite(coef):
                lines.append(
                    f"- {variant_label}: {coef:.4f}{_stars(p_value)} "
                    f"(SE {se:.4f}, p={p_value:.3f}, n={result['nobs']:,})."
                )
            else:
                lines.append(f"- {variant_label}: insufficient sample.")
        lines.append("")
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def main() -> None:
    args = _parse_args()
    run_root = args.test_root / args.run_id
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    args.paper_root.mkdir(parents=True, exist_ok=True)
    for subdir in ["docx", "latex", "tables", "figures", "writer_packets", "snippets"]:
        (args.paper_root / subdir).mkdir(parents=True, exist_ok=True)

    panel = _load_panel(args.annual_panel)
    raw = _pull_changes(panel, dotenv_path=args.dotenv_path)
    event_panel, event_summary = _prepare_events(raw)
    sample, sample_summary = _prepare_sample(panel, event_panel)
    sample = _filter_size_subset(sample, args.size_subset)
    subset_label = {"all": "full AI-talking sample", "nonbig": "non-big AI-talking sample", "big": "big AI-talking sample"}[args.size_subset]
    sample_summary["subset_key"] = args.size_subset
    sample_summary["subset_label"] = subset_label
    sample_summary["subset_rows"] = int(len(sample))
    sample_summary["subset_firms"] = int(sample["cik"].nunique())
    sample_summary["subset_t1_t2_any_scitech"] = int(sample["scitech_appoint_t1_t2"].fillna(0).sum())
    sample_summary["subset_t1_t2_c_level_scitech"] = int(
        sample["c_level_scitech_appoint_t1_t2"].fillna(0).sum()
    )
    sample_summary["subset_t1_t2_tech_lead"] = int(sample["tech_lead_appoint_t1_t2"].fillna(0).sum())
    rows = [_fit_model(sample, outcome, variant) for outcome, _label in OUTCOME_SPECS for variant, _vlabel in VARIANT_SPECS]
    table_df, keyed = _build_results_table(rows)
    markdown, latex = _render_table_outputs(table_df)

    stem = f"{TEST_ID}_{args.run_id}"
    docx_path = run_root / f"{stem}.docx"
    tex_path = run_root / f"{stem}.tex"
    csv_path = run_root / f"{stem}.csv"
    png_path = run_root / f"{stem}.png"
    pdf_path = run_root / f"{stem}.pdf"
    md_path = run_root / f"{stem}.md"
    writer_path = run_root / f"{stem}_writer_packet.md"
    notes_path = run_root / f"{stem}_result_notes.md"
    event_path = run_root / "appointment_event_panel.parquet"
    raw_path = run_root / "appointment_rows.parquet"
    sample_path = run_root / "appointment_sample.parquet"

    _write_docx(
        output_path=docx_path,
        table_df=table_df,
        event_summary=event_summary,
        sample_summary=sample_summary,
        subset_label=subset_label,
    )
    tex_path.write_text(latex, encoding="utf-8")
    csv_path.write_text(table_df.to_csv(index=False), encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    _write_figure(sample, png_path=png_path, pdf_path=pdf_path)
    _write_writer_packet(
        output_path=writer_path,
        event_summary=event_summary,
        sample_summary=sample_summary,
        keyed=keyed,
        subset_label=subset_label,
    )
    _write_result_notes(notes_path, keyed)
    event_panel.to_parquet(event_path, index=False)
    raw.to_parquet(raw_path, index=False)
    sample.to_parquet(sample_path, index=False)

    for subdir, path in {
        "docx": docx_path,
        "latex": tex_path,
        "tables": csv_path,
        "figures": png_path,
        "writer_packets": writer_path,
        "snippets": notes_path,
    }.items():
        shutil.copy2(path, args.paper_root / subdir / path.name)

    manifest = {
        "test_id": TEST_ID,
        "module_path": MODULE_PATH,
        "run_id": args.run_id,
        "size_subset": args.size_subset,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "event_summary": event_summary,
        "sample_summary": sample_summary,
        "outputs": {
            "docx": str(docx_path),
            "tex": str(tex_path),
            "csv": str(csv_path),
            "png": str(png_path),
            "pdf": str(pdf_path),
            "markdown": str(md_path),
            "writer_packet": str(writer_path),
            "result_notes": str(notes_path),
            "event_panel": str(event_path),
            "raw_rows": str(raw_path),
            "sample": str(sample_path),
        },
    }
    (run_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
