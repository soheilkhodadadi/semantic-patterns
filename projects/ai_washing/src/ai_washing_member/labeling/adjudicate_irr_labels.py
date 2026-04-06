"""Seed and finalize IRR adjudication artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from ai_washing_member.labeling.common import (
    ALLOWED_LABELS,
    ensure_allowed_label,
    load_table,
    write_excel,
)

SHORT = {"Actionable": "A", "Speculative": "S", "Irrelevant": "I"}
PARQUET_COLUMNS = [
    "irr_item_id",
    "sample_id",
    "batch_row_id",
    "sentence_id",
    "sentence",
    "source_cik",
    "source_year",
    "source_form",
    "source_file",
    "sentence_index",
    "ff12_code",
    "ff12_name",
    "rater1_label",
    "rater2_label",
    "disagreement_pair",
    "transition",
    "final_label",
    "adjudication_note",
    "resolved_label",
    "resolution_source",
]
SHEET_COLUMNS = [
    "irr_item_id",
    "sample_id",
    "batch_row_id",
    "sentence_id",
    "sentence",
    "source_cik",
    "source_year",
    "source_form",
    "source_file",
    "sentence_index",
    "ff12_code",
    "ff12_name",
    "rater1_label",
    "rater2_label",
    "disagreement_pair",
    "transition",
    "final_label",
    "adjudication_note",
]


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256_if_exists(path: str | Path) -> str:
    resolved = Path(path)
    if not resolved.exists():
        return ""
    hasher = hashlib.sha256()
    with open(resolved, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _disagreement_pair(a: str, b: str) -> str:
    first, second = sorted([SHORT.get(a, "?"), SHORT.get(b, "?")])
    return f"{first}_vs_{second}"


def _load_master(path: str | Path) -> pd.DataFrame:
    frame = load_table(path)
    if "irr_item_id" not in frame.columns:
        raise ValueError("Master file must include `irr_item_id`.")
    if "rater1_label" not in frame.columns and "label" in frame.columns:
        frame["rater1_label"] = frame["label"]
    if "rater1_label" not in frame.columns:
        raise ValueError("Master file must include `rater1_label` or `label`.")
    if "sample_id" not in frame.columns:
        if "batch_row_id" in frame.columns:
            frame["sample_id"] = frame["batch_row_id"]
        else:
            frame["sample_id"] = frame["irr_item_id"]
    for column in [
        "sample_id",
        "batch_row_id",
        "sentence_id",
        "sentence",
        "source_cik",
        "source_year",
        "source_form",
        "source_file",
        "sentence_index",
        "ff12_code",
        "ff12_name",
    ]:
        if column not in frame.columns:
            frame[column] = ""
        frame[column] = frame[column].fillna("").astype(str)
    frame["rater1_label"] = frame["rater1_label"].map(ensure_allowed_label)
    return frame[frame["rater1_label"].isin(ALLOWED_LABELS)].copy()


def _load_optional_labels(path: str | Path, *, label_column: str) -> pd.DataFrame | None:
    resolved = Path(path)
    if not resolved.exists():
        return None
    frame = load_table(resolved)
    if "irr_item_id" not in frame.columns or label_column not in frame.columns:
        return None
    keep = frame[["irr_item_id", label_column]].copy()
    keep[label_column] = keep[label_column].map(ensure_allowed_label)
    if "rater2_note" in frame.columns:
        keep["rater2_note"] = frame["rater2_note"].fillna("").astype(str)
    else:
        keep["rater2_note"] = ""
    if "adjudication_note" in frame.columns:
        keep["adjudication_note"] = frame["adjudication_note"].fillna("").astype(str)
    else:
        keep["adjudication_note"] = ""
    return keep


def run_adjudication(args: argparse.Namespace) -> tuple[dict, int]:
    out_sheet_csv = Path(args.output_sheet_csv)
    out_sheet_xlsx = Path(args.output_sheet_xlsx)
    out_parquet = Path(args.output_parquet)
    out_status = Path(args.output_status)
    for path in [out_sheet_csv, out_sheet_xlsx, out_parquet, out_status]:
        path.parent.mkdir(parents=True, exist_ok=True)

    master = _load_master(args.master)
    rater2 = _load_optional_labels(args.rater2, label_column="rater2_label")
    adjudication_input = _load_optional_labels(args.adjudication_input, label_column="final_label")

    combined = master.copy()
    if rater2 is None:
        combined["rater2_label"] = ""
        combined["rater2_note"] = ""
        status_name = "pending_rater2"
    else:
        combined = combined.drop(
            columns=[col for col in ["rater2_label", "rater2_note"] if col in combined.columns],
            errors="ignore",
        )
        combined = combined.merge(rater2, on="irr_item_id", how="left")
        combined["rater2_label"] = combined["rater2_label"].fillna("")
        combined["rater2_note"] = combined["rater2_note"].fillna("")
        if combined["rater2_label"].isin(ALLOWED_LABELS).sum() < len(combined):
            status_name = "pending_rater2"
        else:
            status_name = "pending_adjudication"

    combined["disagreement_pair"] = ""
    combined["transition"] = ""
    if rater2 is not None:
        disagreements_mask = combined["rater2_label"].isin(ALLOWED_LABELS) & (
            combined["rater1_label"] != combined["rater2_label"]
        )
        disagreements = combined[disagreements_mask].copy()
        if not disagreements.empty:
            combined.loc[disagreements.index, "disagreement_pair"] = disagreements.apply(
                lambda row: _disagreement_pair(row["rater1_label"], row["rater2_label"]), axis=1
            )
            combined.loc[disagreements.index, "transition"] = disagreements.apply(
                lambda row: f"{SHORT[row['rater1_label']]}->{SHORT[row['rater2_label']]}", axis=1
            )
    else:
        disagreements = combined.iloc[0:0].copy()

    combined["final_label"] = ""
    combined["adjudication_note"] = ""
    if adjudication_input is not None:
        keep = adjudication_input.rename(
            columns={
                "final_label": "final_label_input",
                "adjudication_note": "adjudication_note_input",
            }
        )
        if "adjudication_note_input" not in keep.columns:
            keep["adjudication_note_input"] = ""
        combined = combined.merge(
            keep[["irr_item_id", "final_label_input", "adjudication_note_input"]],
            on="irr_item_id",
            how="left",
        )
        combined["final_label"] = combined["final_label_input"].fillna("")
        combined["adjudication_note"] = combined["adjudication_note_input"].fillna("")
        combined = combined.drop(columns=["final_label_input", "adjudication_note_input"])

    combined["resolved_label"] = ""
    combined["resolution_source"] = ""
    agreement_mask = combined["rater2_label"].isin(ALLOWED_LABELS) & (
        combined["rater1_label"] == combined["rater2_label"]
    )
    combined.loc[agreement_mask, "resolved_label"] = combined.loc[agreement_mask, "rater1_label"]
    combined.loc[agreement_mask, "resolution_source"] = "agreement"

    third_mask = (combined["disagreement_pair"] != "") & combined["final_label"].isin(
        ALLOWED_LABELS
    )
    combined.loc[third_mask, "resolved_label"] = combined.loc[third_mask, "final_label"]
    combined.loc[third_mask, "resolution_source"] = "third_adjudicator"

    disagreement_rows = combined[combined["disagreement_pair"] != ""].copy()
    unresolved = disagreement_rows[
        ~disagreement_rows["resolved_label"].isin(ALLOWED_LABELS)
    ].copy()
    if status_name != "pending_rater2":
        status_name = "finalized" if unresolved.empty else "pending_adjudication"

    sheet = disagreement_rows[SHEET_COLUMNS].copy()
    sheet.to_csv(out_sheet_csv, index=False)
    write_excel(out_sheet_xlsx, sheet)

    combined[PARQUET_COLUMNS].to_parquet(out_parquet, index=False)

    status = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "master": args.master,
            "rater2": args.rater2,
            "adjudication_input": args.adjudication_input,
            "master_sha256": _sha256_if_exists(args.master),
            "rater2_sha256": _sha256_if_exists(args.rater2),
            "adjudication_input_sha256": _sha256_if_exists(args.adjudication_input),
        },
        "summary": {
            "status": status_name,
            "rows_master": int(len(master)),
            "rows_with_rater2": int(combined["rater2_label"].isin(ALLOWED_LABELS).sum()),
            "rows_disagreement": int(len(disagreement_rows)),
            "rows_requiring_adjudication": int(len(disagreement_rows)),
            "rows_resolved": int(combined["resolved_label"].isin(ALLOWED_LABELS).sum()),
            "rows_unresolved_disagreement": int(len(unresolved)),
        },
        "artifacts": {
            "sheet_csv": str(out_sheet_csv),
            "sheet_xlsx": str(out_sheet_xlsx),
            "adjudication_parquet": str(out_parquet),
        },
    }
    out_status.write_text(json.dumps(status, indent=2), encoding="utf-8")

    if status_name != "finalized" and not args.allow_pending:
        return status, 1
    return status, 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed and finalize IRR adjudication artifacts.")
    parser.add_argument("--master", default="data/labels/v1/irr_subset_master.csv")
    parser.add_argument("--rater2", default="data/labels/v1/irr_subset_rater2_completed.xlsx")
    parser.add_argument(
        "--adjudication-input",
        default="data/labels/v1/irr_adjudication_completed.xlsx",
    )
    parser.add_argument(
        "--output-sheet-csv",
        default="data/labels/v1/irr_adjudication_sheet.csv",
    )
    parser.add_argument(
        "--output-sheet-xlsx",
        default="data/labels/v1/irr_adjudication_sheet.xlsx",
    )
    parser.add_argument("--output-parquet", default="data/labels/v1/adjudication.parquet")
    parser.add_argument(
        "--output-status",
        default="reports/labels/irr_adjudication_status.json",
    )
    parser.add_argument("--allow-pending", action="store_true", default=True)
    parser.add_argument("--no-allow-pending", dest="allow_pending", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    status, exit_code = run_adjudication(args)
    print(
        f"[irr] adjudication_status={status['summary']['status']} "
        f"rows_disagreement={status['summary']['rows_disagreement']}"
    )
    print(f"[irr] status -> {args.output_status}")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
