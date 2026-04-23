"""Publication run driver for legacy Table B1: measurement audit."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd
from docx import Document

from semantic_ai_washing.analysis.publication_runs.test_03_post_filing_drift import (
    _add_note,
    _add_title,
    _build_panel_table,
    _set_document_defaults,
    _set_landscape,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_LABEL_BASE = REPO_ROOT / "data/labels/v1/labels_master.parquet"
DEFAULT_TRAINING_POOL = (
    REPO_ROOT / "data/labels/v2/labels_master_boundary_revised_v1_excluding_heldout_v4.parquet"
)
DEFAULT_HELDOUT_V4 = REPO_ROOT / "data/validation/held_out_v4/held_out_sentences_v4.csv"
DEFAULT_IRR_REPORT = REPO_ROOT / "reports/labels/irr_boundary_revised_v3_rerun_report.json"
DEFAULT_HYBRID_EVAL = (
    REPO_ROOT / "reports/evaluation/selective_defer_heldout_v4_hybrid_api_upgrade_v2.json"
)
DEFAULT_TEST_ROOT = Path(
    "/Users/soheilkhodadadi/DataWork/semantic-patterns/ai_washing/derived/test_runs/legacy_b1_measurement_audit"
)
DEFAULT_PAPER_ROOT = REPO_ROOT / "paper/generated"
DEFAULT_RUN_ID = f"{date.today():%Y%m%d}_hybrid_api_a_conf49_main_v1"
TEST_ID = "legacy_b1_measurement_audit"
MODULE_PATH = "semantic_ai_washing.analysis.publication_runs.legacy_b1_measurement_audit"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label-base", type=Path, default=DEFAULT_LABEL_BASE)
    parser.add_argument("--training-pool", type=Path, default=DEFAULT_TRAINING_POOL)
    parser.add_argument("--heldout-v4", type=Path, default=DEFAULT_HELDOUT_V4)
    parser.add_argument("--irr-report", type=Path, default=DEFAULT_IRR_REPORT)
    parser.add_argument("--hybrid-eval", type=Path, default=DEFAULT_HYBRID_EVAL)
    parser.add_argument("--test-root", type=Path, default=DEFAULT_TEST_ROOT)
    parser.add_argument("--paper-root", type=Path, default=DEFAULT_PAPER_ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    return parser.parse_args()


def _fmt_pct(value: float) -> str:
    return f"{100 * value:.1f}%"


def _fmt_kappa(value: float) -> str:
    return f"{value:.3f}"


def _load_measurement_inputs(args: argparse.Namespace) -> dict[str, object]:
    label_base_rows = len(pd.read_parquet(args.label_base))
    training_pool_rows = len(pd.read_parquet(args.training_pool))
    heldout_rows = len(pd.read_csv(args.heldout_v4))

    irr_payload = json.loads(args.irr_report.read_text(encoding="utf-8"))
    irr_summary = irr_payload["summary"]

    hybrid_payload = json.loads(args.hybrid_eval.read_text(encoding="utf-8"))
    benchmark = hybrid_payload["benchmark"]
    best_policy = hybrid_payload["best_deployable_policy"]
    local_only = next(
        policy for policy in hybrid_payload["policies"] if policy["policy_name"] == "local_only"
    )

    return {
        "label_base_rows": label_base_rows,
        "training_pool_rows": training_pool_rows,
        "heldout_rows": heldout_rows,
        "irr_summary": irr_summary,
        "hybrid_payload": hybrid_payload,
        "benchmark_rows": int(benchmark["rows"]),
        "best_policy": best_policy,
        "local_only": local_only,
    }


def _build_table_df(measurement: dict[str, object]) -> pd.DataFrame:
    irr_summary = measurement["irr_summary"]
    best_policy = measurement["best_policy"]
    local_only = measurement["local_only"]
    rows = [
        {
            "panel": "Panel A. Human labeling and validation",
            "row_label": "Adjudicated sentence base",
            "n": measurement["label_base_rows"],
            "primary_metric": "Human-reviewed labels",
            "supporting_metric": "Historical master corpus",
            "notes": "Used to seed and refine the local sentence classifier.",
        },
        {
            "panel": "Panel A. Human labeling and validation",
            "row_label": "Leakage-safe training pool",
            "n": measurement["training_pool_rows"],
            "primary_metric": "Human-reviewed labels",
            "supporting_metric": "Excludes heldout-v4 items",
            "notes": "Current training/calibration pool after removing benchmark sentences.",
        },
        {
            "panel": "Panel A. Human labeling and validation",
            "row_label": "Current adjudicated benchmark",
            "n": measurement["heldout_rows"],
            "primary_metric": "Final heldout-v4 labels",
            "supporting_metric": "Deployment benchmark",
            "notes": "Balanced benchmark used for the current hybrid evaluation posture.",
        },
        {
            "panel": "Panel A. Human labeling and validation",
            "row_label": "Human-human IRR v3 rerun",
            "n": measurement["heldout_rows"],
            "primary_metric": f"Cohen's kappa = {_fmt_kappa(irr_summary['kappa'])}",
            "supporting_metric": (
                f"{irr_summary['resolved_disagreements']}/{irr_summary['rows_disagreement']} "
                "disagreements adjudicated"
            ),
            "notes": (
                "By-class kappa: Actionable "
                f"{_fmt_kappa(irr_summary['by_class_kappa']['Actionable'])}; "
                "Speculative "
                f"{_fmt_kappa(irr_summary['by_class_kappa']['Speculative'])}; "
                "Irrelevant "
                f"{_fmt_kappa(irr_summary['by_class_kappa']['Irrelevant'])}."
            ),
        },
        {
            "panel": "Panel B. Heldout-v4 model evaluation",
            "row_label": "Local-only baseline",
            "n": measurement["benchmark_rows"],
            "primary_metric": f"Accuracy = {_fmt_pct(local_only['accuracy'])}",
            "supporting_metric": f"Macro-F1 = {_fmt_pct(local_only['macro_f1'])}",
            "notes": (
                f"Binary relevance {_fmt_pct(local_only['binary_relevance_accuracy'])}; "
                f"A/S {_fmt_pct(local_only['actionable_speculative_conditional_accuracy'])}; "
                "defer 0/120."
            ),
        },
        {
            "panel": "Panel B. Heldout-v4 model evaluation",
            "row_label": "Selected hybrid policy",
            "n": measurement["benchmark_rows"],
            "primary_metric": f"Accuracy = {_fmt_pct(best_policy['accuracy'])}",
            "supporting_metric": f"Macro-F1 = {_fmt_pct(best_policy['macro_f1'])}",
            "notes": (
                f"{best_policy['policy_name']}; binary relevance "
                f"{_fmt_pct(best_policy['binary_relevance_accuracy'])}; "
                f"A/S {_fmt_pct(best_policy['actionable_speculative_conditional_accuracy'])}; "
                f"defer {best_policy['deferred_rows']}/{measurement['benchmark_rows']}."
            ),
        },
    ]
    return pd.DataFrame(rows)


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def _escape_tex(text: str) -> str:
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )


def _render_table_outputs(table_df: pd.DataFrame) -> tuple[str, str]:
    headers = ["Item", "N", "Primary metric", "Supporting metric", "Notes"]
    md_lines = ["# Table Main", ""]
    latex_lines = [
        "\\begin{table}[!htbp]",
        "\\centering",
        "\\caption{Measurement audit of the disclosure-classification layer}",
        "\\begin{tabular}{p{2.8cm}cp{2.8cm}p{2.8cm}p{5.4cm}}",
        "\\hline",
    ]
    for panel_name in table_df["panel"].drop_duplicates():
        subset = table_df.loc[table_df["panel"].eq(panel_name)].copy()
        rendered = subset[
            ["row_label", "n", "primary_metric", "supporting_metric", "notes"]
        ].values.tolist()
        md_lines.extend([f"## {panel_name}", _markdown_table(headers, rendered), ""])
        latex_lines.append(
            f"\\multicolumn{{5}}{{l}}{{\\textit{{{_escape_tex(panel_name)}}}}} \\\\"
        )
        latex_lines.append(" & ".join(headers) + " \\\\")
        for row in rendered:
            latex_lines.append(" & ".join(_escape_tex(str(value)) for value in row) + " \\\\")
    latex_lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
    return "\n".join(md_lines), "\n".join(latex_lines) + "\n"


def _docx_panel_rows(table_df: pd.DataFrame, panel_name: str) -> list[list[tuple[str, bool]]]:
    rows = []
    subset = table_df.loc[table_df["panel"].eq(panel_name)].copy()
    for row in subset[
        ["row_label", "n", "primary_metric", "supporting_metric", "notes"]
    ].itertuples(index=False):
        rows.append(
            [
                (str(row[0]), True),
                (str(row[1]), False),
                (str(row[2]), False),
                (str(row[3]), False),
                (str(row[4]), False),
            ]
        )
    return rows


def _build_table_docx(table_df: pd.DataFrame, output_path: Path) -> None:
    document = Document()
    _set_document_defaults(document)
    _set_landscape(document)
    _add_title(document, "Table B1. Measurement Audit of the Disclosure-Classification Layer")
    _add_note(
        document,
        "This table consolidates the current human-label base, the leakage-safe training pool, "
        "the adjudicated heldout-v4 benchmark, the human-human IRR rerun, and the final heldout-v4 "
        "evaluation of the selected hybrid classifier. The IRR rerun is human-human only, uses the "
        "balanced v3 rerun benchmark, and resolves all observed disagreements through adjudication. "
        "The selected deployment posture uses the API-A deferral rule rather than the leakage-flagged "
        "local-only diagnostic that was excluded from the current audit.",
    )
    headers = ["", "N", "Primary metric", "Supporting metric", "Notes"]
    for panel_name in table_df["panel"].drop_duplicates():
        paragraph = document.add_paragraph()
        paragraph.add_run(panel_name).bold = True
        _build_panel_table(document, headers, _docx_panel_rows(table_df, panel_name))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output_path))


def _result_notes(measurement: dict[str, object]) -> str:
    irr_summary = measurement["irr_summary"]
    local_only = measurement["local_only"]
    best_policy = measurement["best_policy"]
    accuracy_gain = best_policy["accuracy"] - local_only["accuracy"]
    macro_f1_gain = best_policy["macro_f1"] - local_only["macro_f1"]
    return "\n".join(
        [
            "# Result Notes",
            "",
            f"- Human-human IRR rerun: Cohen's kappa `{_fmt_kappa(irr_summary['kappa'])}` on `{measurement['heldout_rows']}` reviewed items.",
            (
                "- By-class kappa: "
                f"Actionable `{_fmt_kappa(irr_summary['by_class_kappa']['Actionable'])}`, "
                f"Speculative `{_fmt_kappa(irr_summary['by_class_kappa']['Speculative'])}`, "
                f"Irrelevant `{_fmt_kappa(irr_summary['by_class_kappa']['Irrelevant'])}`."
            ),
            (
                f"- Selected hybrid policy reaches `{_fmt_pct(best_policy['accuracy'])}` accuracy and "
                f"`{_fmt_pct(best_policy['macro_f1'])}` macro-F1 on `{measurement['benchmark_rows']}` "
                "heldout-v4 items."
            ),
            (
                f"- Relative to the local-only baseline, the hybrid policy adds `{100 * accuracy_gain:.1f}` "
                f"percentage points of accuracy and `{100 * macro_f1_gain:.1f}` percentage points of macro-F1."
            ),
            (
                f"- Deferral footprint: `{best_policy['deferred_rows']}` rows "
                f"(`{_fmt_pct(best_policy['deferred_rate'])}` of the benchmark) routed to API-A."
            ),
            (
                "- The leakage-flagged local-only evaluation file "
                "`heldout_v4_selective_defer_conf49_v1.json` is intentionally excluded from the main audit."
            ),
            "",
        ]
    )


def _writer_packet(args: argparse.Namespace, measurement: dict[str, object]) -> str:
    irr_summary = measurement["irr_summary"]
    best_policy = measurement["best_policy"]
    return "\n".join(
        [
            "# Writer Packet",
            "",
            "## Metadata",
            f"- Test id: `{TEST_ID}`",
            f"- Run id: `{args.run_id}`",
            f"- Date run: `{date.today().isoformat()}`",
            f"- Script/module path: `{MODULE_PATH}`",
            "",
            "## Source Artifacts",
            f"- Label base: `{args.label_base}`",
            f"- Leakage-safe training pool: `{args.training_pool}`",
            f"- Heldout-v4 benchmark: `{args.heldout_v4}`",
            f"- IRR rerun report: `{args.irr_report}`",
            f"- Hybrid evaluation report: `{args.hybrid_eval}`",
            f"- Scored benchmark used by the hybrid evaluation: `{measurement['hybrid_payload']['benchmark']['path']}`",
            "",
            "## Main Numbers",
            f"- Adjudicated sentence base: `{measurement['label_base_rows']}` rows",
            f"- Leakage-safe training/calibration pool: `{measurement['training_pool_rows']}` rows",
            f"- Heldout-v4 benchmark: `{measurement['heldout_rows']}` rows",
            (
                f"- Human-human IRR rerun: kappa `{_fmt_kappa(irr_summary['kappa'])}`, "
                f"`{irr_summary['resolved_disagreements']}` resolved disagreements"
            ),
            (
                f"- Selected hybrid policy `{best_policy['policy_name']}`: accuracy "
                f"`{_fmt_pct(best_policy['accuracy'])}`, macro-F1 `{_fmt_pct(best_policy['macro_f1'])}`, "
                f"binary relevance `{_fmt_pct(best_policy['binary_relevance_accuracy'])}`, "
                f"A/S `{_fmt_pct(best_policy['actionable_speculative_conditional_accuracy'])}`"
            ),
            "",
            "## Caption Draft",
            "This appendix table summarizes the measurement audit underlying the disclosure-classification layer. It reports the size of the adjudicated sentence base, the leakage-safe training pool used for model calibration, the current adjudicated heldout-v4 benchmark, the human-human IRR rerun, and the heldout-v4 evaluation of the selected hybrid policy. The final deployment posture uses targeted API-A deferral on low-confidence rows and improves materially over the local-only baseline.",
            "",
        ]
    )


def _dataset_summary(
    args: argparse.Namespace, measurement: dict[str, object]
) -> dict[str, object]:
    return {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "inputs": {
            "label_base": str(args.label_base),
            "training_pool": str(args.training_pool),
            "heldout_v4": str(args.heldout_v4),
            "irr_report": str(args.irr_report),
            "hybrid_eval": str(args.hybrid_eval),
        },
        "measurement": measurement,
    }


def _copy_exports(run_dir: Path, paper_root: Path, run_id: str) -> dict[str, str]:
    exports = {
        "table_csv": paper_root / "tables" / f"{TEST_ID}_{run_id}.csv",
        "table_md": paper_root / "tables" / f"{TEST_ID}_{run_id}.md",
        "table_tex": paper_root / "latex" / f"{TEST_ID}_{run_id}.tex",
        "table_docx": paper_root / "docx" / f"{TEST_ID}_{run_id}.docx",
        "writer_packet": paper_root / "writer_packets" / f"{TEST_ID}_{run_id}.md",
        "result_notes": paper_root / "snippets" / f"{TEST_ID}_{run_id}_result_notes.md",
    }
    for path in exports.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    mapping = {
        run_dir / "table_main.csv": exports["table_csv"],
        run_dir / "table_main.md": exports["table_md"],
        run_dir / "table_main.tex": exports["table_tex"],
        run_dir / "table_main.docx": exports["table_docx"],
        run_dir / "writer_packet.md": exports["writer_packet"],
        run_dir / "result_notes.md": exports["result_notes"],
    }
    for src, dst in mapping.items():
        shutil.copy2(src, dst)
    return {key: str(path) for key, path in exports.items()}


def main() -> None:
    args = _parse_args()
    run_dir = args.test_root / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    measurement = _load_measurement_inputs(args)
    table_df = _build_table_df(measurement)
    table_df.to_csv(run_dir / "table_main.csv", index=False)

    table_md, table_tex = _render_table_outputs(table_df)
    (run_dir / "table_main.md").write_text(table_md, encoding="utf-8")
    (run_dir / "table_main.tex").write_text(table_tex, encoding="utf-8")
    _build_table_docx(table_df, run_dir / "table_main.docx")
    (run_dir / "result_notes.md").write_text(_result_notes(measurement), encoding="utf-8")
    (run_dir / "writer_packet.md").write_text(_writer_packet(args, measurement), encoding="utf-8")
    dataset_summary = _dataset_summary(args, measurement)
    (run_dir / "dataset_summary.json").write_text(
        json.dumps(dataset_summary, indent=2), encoding="utf-8"
    )

    paper_exports = _copy_exports(run_dir, args.paper_root, args.run_id)
    manifest = {
        "test_id": TEST_ID,
        "run_id": args.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "module_path": MODULE_PATH,
        "run_dir": str(run_dir),
        "outputs": {
            "dataset_summary": str(run_dir / "dataset_summary.json"),
            "table_csv": str(run_dir / "table_main.csv"),
            "table_md": str(run_dir / "table_main.md"),
            "table_tex": str(run_dir / "table_main.tex"),
            "table_docx": str(run_dir / "table_main.docx"),
            "writer_packet": str(run_dir / "writer_packet.md"),
            "result_notes": str(run_dir / "result_notes.md"),
        },
        "paper_exports": paper_exports,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"[{TEST_ID}] wrote run bundle to {run_dir}")
    print(f"[{TEST_ID}] paper table: {paper_exports['table_docx']}")


if __name__ == "__main__":
    main()
