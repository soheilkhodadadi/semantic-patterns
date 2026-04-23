"""Publication run driver for the classifier-risk appendix block on a high-confidence local-only subset."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd

from semantic_ai_washing.analysis.delivery_table_payloads import (
    TIMING_LOG_AI_OUTCOMES,
    _add_patent_mismatch,
    _fit_absorbed_ols,
    _fit_fe_ols,
    _mismatch_spec_variant_defs,
    fmt_num,
    load_panel,
    sig_stars,
)
from semantic_ai_washing.analysis.publication_runs.legacy_timing_table_utils import (
    build_payload_docx,
    flatten_payload_to_csv,
    write_payload_json,
    write_payload_markdown,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_ANNUAL_PANEL = (
    REPO_ROOT
    / "data/processed/panel/canonical/ever_speaker_panel_2016_2025_hybrid_api_a_conf49_v1.parquet"
)
DEFAULT_FILING_MEASURES = (
    REPO_ROOT / "data/interim/market/filing_ai_measures_hybrid_api_a_conf49_v1.csv"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/legacy_classifier_risk_highconf"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "legacy_classifier_risk_highconf"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.legacy_classifier_risk_highconf"
LOW_CONFIDENCE_THRESHOLD = 0.49


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annual-panel", type=Path, default=DEFAULT_ANNUAL_PANEL)
    parser.add_argument("--filing-measures", type=Path, default=DEFAULT_FILING_MEASURES)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _normalize_cik(value: object) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    return digits.zfill(10) if digits else ""


def _attach_high_conf_flag(panel: pd.DataFrame, filing_measures_path: Path) -> tuple[pd.DataFrame, dict[str, object]]:
    measures = pd.read_csv(filing_measures_path, low_memory=False).copy()
    measures["cik_norm"] = measures["cik"].map(_normalize_cik)
    measures["year"] = pd.to_numeric(measures["filing_year"], errors="coerce").astype("Int64")
    measures["api_a_sentence_count"] = pd.to_numeric(
        measures["api_a_sentence_count"], errors="coerce"
    ).fillna(0)
    annual = (
        measures.dropna(subset=["year"])
        .groupby(["cik_norm", "year"], as_index=False)
        .agg(
            api_a_sentence_count=("api_a_sentence_count", "sum"),
            filing_count=("filing_id", "nunique"),
        )
    )
    annual = annual.rename(columns={"year": "filing_year_int"})
    annual["all_local_year"] = annual["api_a_sentence_count"].eq(0)

    merged = panel.copy()
    merged["cik_norm"] = merged["cik"].map(_normalize_cik)
    merged["year_int"] = pd.to_numeric(merged["year"], errors="coerce").astype("Int64")
    merged = merged.merge(
        annual,
        left_on=["cik_norm", "year_int"],
        right_on=["cik_norm", "filing_year_int"],
        how="left",
    )
    merged["filing_measure_matched"] = merged["filing_count"].notna()
    merged["api_a_sentence_count"] = pd.to_numeric(
        merged["api_a_sentence_count"], errors="coerce"
    ).fillna(0)
    merged["filing_count"] = pd.to_numeric(merged["filing_count"], errors="coerce").fillna(0)
    merged["all_local_year"] = merged["filing_measure_matched"] & merged["api_a_sentence_count"].eq(0)

    talk_mask = merged["any_ai_talk"].fillna(0).astype(int).eq(1)
    summary = {
        "panel_rows_total": int(len(merged)),
        "matched_filing_years": int(merged["filing_measure_matched"].sum()),
        "all_local_year_rows": int(merged["all_local_year"].sum()),
        "all_local_row_share": float(merged["all_local_year"].mean()),
        "ai_talking_rows_total": int(talk_mask.sum()),
        "ai_talking_all_local_rows": int((talk_mask & merged["all_local_year"]).sum()),
        "ai_talking_all_local_share": float(
            (talk_mask & merged["all_local_year"]).sum() / talk_mask.sum()
        )
        if int(talk_mask.sum())
        else 0.0,
        "policy_low_confidence_threshold": LOW_CONFIDENCE_THRESHOLD,
    }
    return merged, summary


def _build_composition_payload(df: pd.DataFrame) -> dict[str, object]:
    models = [
        {"number": f"({idx})", "label": label}
        for idx, (label, _) in enumerate(TIMING_LOG_AI_OUTCOMES, start=1)
    ]
    panel_defs = [
        ("Panel A. Actionable disclosure", "Actionable disclosure (dummy)", "has_actionable"),
        (
            "Panel B. Speculative-only disclosure",
            "Speculative-only disclosure (dummy)",
            "has_spec_only",
        ),
    ]
    panels: list[dict[str, object]] = []
    for panel_index, (heading, label, rhs) in enumerate(panel_defs):
        coef_cells: list[str] = []
        se_cells: list[str] = []
        nobs_cells: list[str] = []
        adj_r2_cells: list[str] = []
        for _, dependent in TIMING_LOG_AI_OUTCOMES:
            result, _, adj_r2 = _fit_fe_ols(df, dependent=dependent, rhs_terms=[rhs])
            coef = result.params.get(rhs, float("nan"))
            se = result.bse.get(rhs, float("nan"))
            pvalue = result.pvalues.get(rhs)
            coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}")
            se_cells.append(f"({se:.3f})")
            nobs_cells.append(f"{int(result.nobs):,}")
            adj_r2_cells.append(fmt_num(adj_r2))
        panels.append(
            {
                "heading": heading,
                "label": label,
                "coef_cells": coef_cells,
                "se_cells": se_cells,
                "footer_rows": (
                    [
                        {"label": "Controls", "cells": ["Y"] * len(models)},
                        {"label": "Firm FE", "cells": ["Y"] * len(models)},
                        {"label": "Year FE", "cells": ["Y"] * len(models)},
                        {"label": "Adj. R²", "cells": adj_r2_cells},
                        {"label": "Observations", "cells": nobs_cells},
                    ]
                    if panel_index == len(panel_defs) - 1
                    else []
                ),
            }
        )
    return {
        "title": "Table C1. High-Confidence Local-Only Subset: Disclosure Composition and AI Patent Timing",
        "note": (
            "This appendix table reruns the disclosure-composition timing regressions on a conservative high-confidence subset. "
            "A firm-year enters the subset only when the hybrid conf49 policy never deferred any sentence to API-A in that filing year, "
            "so all AI sentence labels remain local high-confidence classifications. The dependent variable is `log(1 + AI patents)` "
            "measured at different calendar-time horizons relative to the disclosure year. Firm and year fixed effects are included in all columns, "
            "the baseline control set is unchanged, and standard errors are clustered at the firm level."
        ),
        "dependent_label": "Dependent variable: log(1 + AI patents)",
        "models": models,
        "panels": panels,
    }


def _build_mismatch_payload(df: pd.DataFrame) -> dict[str, object]:
    work = _add_patent_mismatch(df)
    spec_defs = _mismatch_spec_variant_defs(work)
    metrics = [("A/S ratio", "A_S"), ("A/S ratio × PatentMismatch", "AS_x_PatentMismatch")]
    models = [{"number": spec["number"], "label": spec["label"]} for spec in spec_defs]
    footer_flags = {
        key: []
        for key in ["Controls", "Firm FE", "Industry×Year FE", "Year FE", "Non-fin.", "No util."]
    }
    results_by_spec: list[tuple[dict[str, tuple[float, float, float | None]], float | None, int]] = []
    for spec in spec_defs:
        spec_df = work.loc[spec["mask"]].copy()
        metric_results: dict[str, tuple[float, float, float | None]] = {}
        result, _, adj_r2 = _fit_absorbed_ols(
            spec_df,
            dependent="log_patents_ai_lead1",
            rhs_terms=[metric for _, metric in metrics],
            absorb_col=str(spec["absorb_col"]),
            include_year=bool(spec.get("include_year", True)),
        )
        for label, term in metrics:
            coef = result.params.get(term, float("nan"))
            se = result.bse.get(term, float("nan"))
            pvalue = result.pvalues.get(term)
            metric_results[label] = (coef, se, pvalue)
        results_by_spec.append((metric_results, adj_r2, int(result.nobs)))
        for footer_key in footer_flags:
            footer_flags[footer_key].append(str(spec["footer"][footer_key]))

    body_rows: list[dict[str, object]] = []
    for label, _term in metrics:
        coef_cells: list[str] = []
        se_cells: list[str] = []
        for metric_results, _adj_r2, _nobs in results_by_spec:
            coef, se, pvalue = metric_results[label]
            coef_cells.append(f"{coef:.3f}{sig_stars(pvalue)}")
            se_cells.append(f"({se:.3f})")
        body_rows.append({"label": label, "cells": coef_cells, "kind": "coef"})
        body_rows.append({"label": "", "cells": se_cells, "kind": "se"})

    footer_rows = [
        {"label": "Controls", "cells": footer_flags["Controls"]},
        {"label": "Firm FE", "cells": footer_flags["Firm FE"]},
        {"label": "Industry×Year FE", "cells": footer_flags["Industry×Year FE"]},
        {"label": "Year FE", "cells": footer_flags["Year FE"]},
        {"label": "Non-fin.", "cells": footer_flags["Non-fin."]},
        {"label": "No util.", "cells": footer_flags["No util."]},
        {
            "label": "Adj. R²",
            "cells": [fmt_num(adj_r2) for _metric_results, adj_r2, _nobs in results_by_spec],
        },
        {
            "label": "Observations",
            "cells": [f"{nobs:,}" for _metric_results, _adj_r2, nobs in results_by_spec],
        },
    ]
    return {
        "title": "Table C2. High-Confidence Local-Only Subset: A/S Ratio, PatentMismatch, and Future AI Patenting",
        "note": (
            "This appendix table reruns the main `A/S × PatentMismatch` specification on the same conservative high-confidence subset used in Table C1. "
            "A firm-year enters only when the hybrid conf49 policy never deferred any sentence to API-A in that filing year. "
            "The dependent variable is `log(1 + AI patents)` at `t+1`, controls are unchanged, and columns vary the fixed-effects structure and sample trim."
        ),
        "dependent_label": "Dependent variable: log(1 + AI patents at t+1)",
        "models": models,
        "body_rows": body_rows,
        "footer_rows": footer_rows,
    }


def _write_table_exports(
    payload: dict[str, object],
    *,
    kind: str,
    stem: str,
    run_dir: Path,
    paper_root: Path,
    run_id: str,
) -> dict[str, str]:
    csv_path = run_dir / f"{stem}.csv"
    md_path = run_dir / f"{stem}.md"
    docx_path = run_dir / f"{stem}.docx"
    json_path = run_dir / f"{stem}_payload.json"
    write_payload_json(payload, json_path)
    flatten_payload_to_csv(payload, kind=kind, output_path=csv_path)
    write_payload_markdown(payload, kind=kind, output_path=md_path)
    build_payload_docx(payload, kind=kind, output_path=docx_path)

    exports = {
        "table_csv": paper_root / "tables" / f"{stem}_{run_id}.csv",
        "table_md": paper_root / "tables" / f"{stem}_{run_id}.md",
        "table_docx": paper_root / "docx" / f"{stem}_{run_id}.docx",
        "table_payload": paper_root / "tables" / f"{stem}_{run_id}_payload.json",
    }
    for dst in exports.values():
        dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(csv_path, exports["table_csv"])
    shutil.copy2(md_path, exports["table_md"])
    shutil.copy2(docx_path, exports["table_docx"])
    shutil.copy2(json_path, exports["table_payload"])
    return {key: str(value) for key, value in exports.items()}


def _result_notes(summary: dict[str, object], comp_payload: dict[str, object], mismatch_payload: dict[str, object]) -> str:
    comp_panels = comp_payload["panels"]  # type: ignore[assignment]
    mismatch_rows = mismatch_payload["body_rows"]  # type: ignore[assignment]
    mismatch_lookup = {
        row["label"]: row["cells"][0] for row in mismatch_rows if row.get("kind") == "coef"
    }
    return "\n".join(
        [
            "# Result Notes",
            "",
            f"- The high-confidence local-only screen keeps `{summary['all_local_year_rows']:,}` of `{summary['panel_rows_total']:,}` annual panel rows "
            f"and `{summary['ai_talking_all_local_rows']:,}` of `{summary['ai_talking_rows_total']:,}` AI-talking rows.",
            f"- In Table C1 Panel A, the `t+1` actionable coefficient is `{comp_panels[0]['coef_cells'][3]}`; in Panel B, the `t+1` speculative-only coefficient is `{comp_panels[1]['coef_cells'][3]}`.",
            f"- In Table C2, the first-spec `A/S ratio` coefficient is `{mismatch_lookup['A/S ratio']}` and `A/S ratio × PatentMismatch` is `{mismatch_lookup['A/S ratio × PatentMismatch']}`.",
            "",
        ]
    )


def _writer_packet(args: argparse.Namespace, summary: dict[str, object], comp_payload: dict[str, object], mismatch_payload: dict[str, object]) -> str:
    mismatch_rows = mismatch_payload["body_rows"]  # type: ignore[assignment]
    mismatch_lookup = {
        row["label"]: row["cells"][0] for row in mismatch_rows if row.get("kind") == "coef"
    }
    comp_panels = comp_payload["panels"]  # type: ignore[assignment]
    return "\n".join(
        [
            "# Writer Packet",
            "",
            "## Metadata",
            f"- Test id: `{TEST_ID}`",
            f"- Run id: `{args.run_id}`",
            f"- Date run: `{date.today().isoformat()}`",
            f"- Script/module path: `{MODULE_PATH}`",
            f"- Annual panel: `{args.annual_panel}`",
            f"- Filing measure input: `{args.filing_measures}`",
            "- High-confidence rule: `keep firm-years with api_a_sentence_count == 0 in the filing-year aggregate`",
            f"- Underlying selective-defer trigger: `local_confidence < {LOW_CONFIDENCE_THRESHOLD:.2f}` sent rows to API-A under the conf49 policy",
            "",
            "## Sample Block",
            f"- Panel rows retained: `{summary['all_local_year_rows']:,}` of `{summary['panel_rows_total']:,}`",
            f"- AI-talking rows retained: `{summary['ai_talking_all_local_rows']:,}` of `{summary['ai_talking_rows_total']:,}`",
            "- Unit of observation: `firm-year`",
            "",
            "## Table C1",
            "- Purpose: `composition timing robustness on all-local firm-years`",
            f"- Actionable t+1 coefficient: `{comp_panels[0]['coef_cells'][3]}`",
            f"- Speculative-only t+1 coefficient: `{comp_panels[1]['coef_cells'][3]}`",
            "",
            "## Table C2",
            "- Purpose: `main mismatch regression on all-local firm-years`",
            f"- First-spec `A/S ratio`: `{mismatch_lookup['A/S ratio']}`",
            f"- First-spec `A/S ratio × PatentMismatch`: `{mismatch_lookup['A/S ratio × PatentMismatch']}`",
            "",
            "## Interpretation",
            "- If the main signs survive on this all-local subset, the core disclosure-to-patent patterns are not being mechanically driven by low-confidence/API-routed sentence years.",
            "- Candidate use: `appendix robustness block required by Rubric 2.0`",
            "",
        ]
    )


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    full_panel = load_panel(args.annual_panel)
    merged_panel, summary = _attach_high_conf_flag(full_panel, args.filing_measures)
    subset = merged_panel.loc[merged_panel["all_local_year"]].copy()

    comp_payload = _build_composition_payload(subset)
    mismatch_payload = _build_mismatch_payload(subset)

    comp_exports = _write_table_exports(
        comp_payload,
        kind="panel_timing",
        stem="legacy_classifier_risk_highconf_composition",
        run_dir=run_dir,
        paper_root=args.paper_root,
        run_id=args.run_id,
    )
    mismatch_exports = _write_table_exports(
        mismatch_payload,
        kind="row_matrix",
        stem="legacy_classifier_risk_highconf_mismatch",
        run_dir=run_dir,
        paper_root=args.paper_root,
        run_id=args.run_id,
    )

    (run_dir / "result_notes.md").write_text(
        _result_notes(summary, comp_payload, mismatch_payload), encoding="utf-8"
    )
    (run_dir / "writer_packet.md").write_text(
        _writer_packet(args, summary, comp_payload, mismatch_payload), encoding="utf-8"
    )

    paper_snippet = args.paper_root / "snippets" / f"{TEST_ID}_{args.run_id}_result_notes.md"
    paper_writer = args.paper_root / "writer_packets" / f"{TEST_ID}_{args.run_id}.md"
    paper_snippet.parent.mkdir(parents=True, exist_ok=True)
    paper_writer.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_dir / "result_notes.md", paper_snippet)
    shutil.copy2(run_dir / "writer_packet.md", paper_writer)

    dataset_summary = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "annual_panel": str(args.annual_panel),
            "filing_measures": str(args.filing_measures),
        },
        "summary": summary,
    }
    (run_dir / "dataset_summary.json").write_text(
        json.dumps(dataset_summary, indent=2), encoding="utf-8"
    )

    manifest = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "module_path": MODULE_PATH,
        "run_dir": str(run_dir),
        "outputs": {
            "composition": comp_exports,
            "mismatch": mismatch_exports,
            "writer_packet": str(paper_writer),
            "result_notes": str(paper_snippet),
            "dataset_summary": str(run_dir / "dataset_summary.json"),
        },
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] composition table -> {comp_exports['table_docx']}")
    print(f"[{TEST_ID}] mismatch table -> {mismatch_exports['table_docx']}")


if __name__ == "__main__":
    main()
