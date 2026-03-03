"""Create adjudication artifacts and optionally merge final IRR labels."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import ALLOWED_LABELS, ensure_allowed_label

SHORT = {"Actionable": "A", "Speculative": "S", "Irrelevant": "I"}

ADJ_COLUMNS = [
    "irr_item_id",
    "sample_id",
    "sentence_id",
    "sentence",
    "source_year",
    "ff12_code",
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


def _sha256_if_exists(path: str) -> str:
    if not os.path.exists(path):
        return ""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _disagreement_pair(a: str, b: str) -> str:
    first, second = sorted([SHORT.get(a, "?"), SHORT.get(b, "?")])
    return f"{first}_vs_{second}"


def _load_master(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "irr_item_id" not in df.columns:
        raise ValueError("Master file must include `irr_item_id`.")
    if "rater1_label" not in df.columns and "label" in df.columns:
        df["rater1_label"] = df["label"]
    if "rater1_label" not in df.columns:
        raise ValueError("Master file must include `rater1_label`.")

    out = df.copy()
    out["rater1_label"] = out["rater1_label"].map(ensure_allowed_label)
    out = out[out["rater1_label"].isin(ALLOWED_LABELS)].copy()
    for col in ["sample_id", "sentence_id", "sentence", "source_year", "ff12_code"]:
        if col not in out.columns:
            out[col] = ""
        out[col] = out[col].fillna("").astype(str)
    return out


def _load_rater2(path: str) -> pd.DataFrame | None:
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    if "irr_item_id" not in df.columns or "rater2_label" not in df.columns:
        return None
    out = df[["irr_item_id", "rater2_label"]].copy()
    out["rater2_label"] = out["rater2_label"].map(ensure_allowed_label)
    if "rater2_note" in df.columns:
        out["rater2_note"] = df["rater2_note"].fillna("").astype(str)
    else:
        out["rater2_note"] = ""
    return out


def run_adjudication(args: argparse.Namespace) -> tuple[dict, int]:
    out_disagreements = Path(args.output_disagreements)
    out_adjudication = Path(args.output_adjudication)
    out_status = Path(args.output_status)
    out_final = Path(args.final_output)
    out_disagreements.parent.mkdir(parents=True, exist_ok=True)
    out_adjudication.parent.mkdir(parents=True, exist_ok=True)
    out_status.parent.mkdir(parents=True, exist_ok=True)
    out_final.parent.mkdir(parents=True, exist_ok=True)

    master = _load_master(args.master)
    r2 = _load_rater2(args.rater2)

    if r2 is None:
        combined = master.copy()
        combined["rater2_label"] = ""
        combined["rater2_note"] = ""
        combined["disagreement_pair"] = ""
        combined["transition"] = ""
        disagreements = combined.iloc[0:0].copy()
        rows_with_rater2 = 0
        status_name = "pending_rater2"
    else:
        combined = master.merge(r2, on="irr_item_id", how="left")
        rows_with_rater2 = int(combined["rater2_label"].isin(ALLOWED_LABELS).sum())
        combined["rater2_label"] = combined["rater2_label"].fillna("")
        combined["rater2_note"] = combined["rater2_note"].fillna("")
        disagreements = combined[
            combined["rater2_label"].isin(ALLOWED_LABELS)
            & (combined["rater1_label"] != combined["rater2_label"])
        ].copy()
        disagreements["disagreement_pair"] = disagreements.apply(
            lambda row: _disagreement_pair(row["rater1_label"], row["rater2_label"]),
            axis=1,
        )
        disagreements["transition"] = disagreements.apply(
            lambda row: f"{SHORT[row['rater1_label']]}->{SHORT[row['rater2_label']]}",
            axis=1,
        )
        status_name = "pending_adjudication"

    adjudication = combined.copy()
    adjudication["disagreement_pair"] = ""
    adjudication["transition"] = ""
    if not disagreements.empty:
        pair_map = disagreements.set_index("irr_item_id")["disagreement_pair"].to_dict()
        transition_map = disagreements.set_index("irr_item_id")["transition"].to_dict()
        adjudication["disagreement_pair"] = adjudication["irr_item_id"].map(pair_map).fillna("")
        adjudication["transition"] = adjudication["irr_item_id"].map(transition_map).fillna("")
    adjudication["final_label"] = ""
    adjudication["adjudication_note"] = ""

    if out_adjudication.exists():
        existing = pd.read_csv(out_adjudication)
        if "irr_item_id" in existing.columns:
            keep = existing[["irr_item_id"]].copy()
            keep["final_label"] = (
                existing.get("final_label", "").fillna("").map(ensure_allowed_label)
            )
            keep["adjudication_note"] = (
                existing.get("adjudication_note", "").fillna("").astype(str)
            )
            adjudication = adjudication.merge(
                keep,
                on="irr_item_id",
                how="left",
                suffixes=("", "_existing"),
            )
            adjudication["final_label"] = adjudication["final_label_existing"].fillna(
                adjudication["final_label"]
            )
            adjudication["adjudication_note"] = adjudication["adjudication_note_existing"].fillna(
                adjudication["adjudication_note"]
            )
            adjudication = adjudication.drop(
                columns=["final_label_existing", "adjudication_note_existing"]
            )

    disagreements_out = disagreements.copy()
    if disagreements_out.empty:
        pd.DataFrame(columns=ADJ_COLUMNS).to_csv(out_disagreements, index=False)
    else:
        disagreements_out["final_label"] = ""
        disagreements_out["adjudication_note"] = ""
        disagreements_out[ADJ_COLUMNS].to_csv(out_disagreements, index=False)

    adjudication[ADJ_COLUMNS].to_csv(out_adjudication, index=False)

    final_written = False
    rows_requiring_adjudication = int(
        (adjudication["disagreement_pair"] != "").sum()
        + (~adjudication["rater2_label"].isin(ALLOWED_LABELS)).sum()
    )
    rows_adjudicated = int(adjudication["final_label"].isin(ALLOWED_LABELS).sum())

    if rows_requiring_adjudication == 0:
        status_name = "finalized"
    elif rows_adjudicated >= rows_requiring_adjudication and rows_requiring_adjudication > 0:
        status_name = "finalized"

    if status_name == "finalized":
        label_map = {}
        for _, row in adjudication.iterrows():
            final_label = ensure_allowed_label(row["final_label"])
            if final_label:
                label_map[row["sample_id"]] = final_label
            elif row["rater2_label"] and row["rater1_label"] == row["rater2_label"]:
                label_map[row["sample_id"]] = row["rater1_label"]
            else:
                label_map[row["sample_id"]] = row["rater1_label"]

        source_df = pd.read_csv(args.source_dataset)
        if "sample_id" not in source_df.columns or "label" not in source_df.columns:
            raise ValueError("Source dataset must contain `sample_id` and `label`.")
        updated = source_df.copy()
        updated["sample_id"] = updated["sample_id"].fillna("").astype(str)
        updated["label"] = updated["sample_id"].map(label_map).fillna(updated["label"])
        updated.to_csv(out_final, index=False)
        final_written = True

    status = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "master": args.master,
            "rater2": args.rater2,
            "source_dataset": args.source_dataset,
            "master_sha256": _sha256_if_exists(args.master),
            "rater2_sha256": _sha256_if_exists(args.rater2),
            "source_sha256": _sha256_if_exists(args.source_dataset),
        },
        "summary": {
            "status": status_name,
            "rows_master": int(len(master)),
            "rows_with_rater2": int(rows_with_rater2),
            "rows_disagreement": int(len(disagreements)),
            "rows_requiring_adjudication": int(rows_requiring_adjudication),
            "rows_adjudicated": int(rows_adjudicated),
            "final_output_written": bool(final_written),
        },
        "artifacts": {
            "disagreements": str(out_disagreements),
            "adjudication_sheet": str(out_adjudication),
            "final_output": str(out_final),
        },
    }
    out_status.write_text(json.dumps(status, indent=2), encoding="utf-8")

    if status_name != "finalized" and not args.allow_pending:
        return status, 1
    return status, 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare IRR adjudication artifacts and final labels."
    )
    parser.add_argument("--master", default="data/labels/iteration1/irr/irr_subset_master.csv")
    parser.add_argument(
        "--rater2",
        default="data/labels/iteration1/irr/irr_subset_rater2_completed.csv",
    )
    parser.add_argument(
        "--output-disagreements",
        default="data/labels/iteration1/irr/irr_disagreements.csv",
    )
    parser.add_argument(
        "--output-adjudication",
        default="data/labels/iteration1/irr/irr_adjudication_sheet.csv",
    )
    parser.add_argument(
        "--source-dataset",
        default="data/labels/iteration1/recovery/expanded_labeled_sentences_preqa.csv",
    )
    parser.add_argument(
        "--final-output",
        default="data/labels/iteration1/irr/final_labeled_sentences_recovery_adjudicated.csv",
    )
    parser.add_argument(
        "--output-status",
        default="reports/iteration1/phase2_irr/adjudication_status.json",
    )
    parser.add_argument("--allow-pending", action="store_true", default=True)
    parser.add_argument("--no-allow-pending", dest="allow_pending", action="store_false")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    status, exit_code = run_adjudication(args)
    print(
        f"[irr] adjudication_status={status['summary']['status']} "
        f"rows_disagreement={status['summary']['rows_disagreement']} "
        f"final_output_written={status['summary']['final_output_written']}"
    )
    print(f"[irr] status -> {args.output_status}")
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
