"""Freeze a grouped train/validation split registry for adjudicated labels."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.labeling.common import (
    ALLOWED_LABELS,
    ensure_allowed_label,
    load_table,
    normalize_sentence,
)


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


def _stable_sort_key(seed: int, value: str) -> str:
    return hashlib.sha1(f"{seed}|{value}".encode("utf-8")).hexdigest()


def _load_labels_master(path: str | Path) -> pd.DataFrame:
    frame = load_table(path)
    required_columns = {
        "sentence_id",
        "sentence",
        "label",
        "source_cik",
        "manifest_id",
        "batch_row_id",
        "source_year",
    }
    missing = sorted(required_columns - set(frame.columns))
    if missing:
        raise ValueError(f"Labels master missing required columns: {missing}")
    frame = frame.copy()
    frame["label"] = frame["label"].map(ensure_allowed_label)
    invalid = frame["label"].isna().sum()
    if invalid:
        raise ValueError(f"Labels master contains {invalid} invalid or blank labels.")
    if frame["source_cik"].isna().any():
        raise ValueError("Labels master contains missing `source_cik` values.")
    if frame["manifest_id"].isna().any():
        raise ValueError("Labels master contains missing `manifest_id` values.")
    if "sentence_text_id" not in frame.columns:
        frame["sentence_text_id"] = (
            frame["sentence"]
            .map(normalize_sentence)
            .map(lambda value: hashlib.sha1(value.encode("utf-8")).hexdigest()[:16])
        )
    frame["source_cik"] = frame["source_cik"].astype(str)
    frame["manifest_id"] = frame["manifest_id"].astype(str)
    frame["batch_row_id"] = frame["batch_row_id"].astype(str)
    frame["source_year"] = frame["source_year"].astype(str)
    frame["sentence_id"] = frame["sentence_id"].astype(str)
    frame["sentence_text_id"] = frame["sentence_text_id"].astype(str)
    return frame


def _load_heldout(path: str | Path) -> tuple[set[str], int]:
    held_out = pd.read_csv(path)
    if "sentence" not in held_out.columns:
        raise ValueError("Held-out sentences file must include `sentence`.")
    normalized = {
        normalize_sentence(value)
        for value in held_out["sentence"].fillna("").astype(str)
        if normalize_sentence(value)
    }
    return normalized, int(len(held_out))


def _label_counts(frame: pd.DataFrame) -> dict[str, int]:
    return {label: int((frame["label"] == label).sum()) for label in ALLOWED_LABELS}


def _group_payload(frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    payload: dict[str, dict[str, Any]] = {}
    for source_cik, group in frame.groupby("source_cik", sort=False):
        payload[str(source_cik)] = {
            "row_count": int(len(group)),
            "label_counts": _label_counts(group),
        }
    return payload


def _zero_counts() -> dict[str, int]:
    return {label: 0 for label in ALLOWED_LABELS}


def _combine_counts(
    left: dict[str, int], right: dict[str, int], factor: int = 1
) -> dict[str, int]:
    return {label: int(left[label] + factor * right[label]) for label in ALLOWED_LABELS}


def _score(
    counts: dict[str, int],
    total_rows: int,
    *,
    label_targets: dict[str, int],
    total_target: int,
) -> tuple[int, int, int]:
    label_abs_dev = sum(abs(counts[label] - label_targets[label]) for label in ALLOWED_LABELS)
    max_label_abs_dev = max(abs(counts[label] - label_targets[label]) for label in ALLOWED_LABELS)
    total_abs_dev = abs(total_rows - total_target)
    return (label_abs_dev, max_label_abs_dev, total_abs_dev)


def _search_validation_groups(
    group_stats: dict[str, dict[str, Any]],
    *,
    label_targets: dict[str, int],
    total_target: int,
    seed: int,
) -> tuple[set[str], dict[str, int], int]:
    group_order = sorted(group_stats, key=lambda value: _stable_sort_key(seed, value))
    selected: set[str] = set()
    counts = _zero_counts()
    total_rows = 0
    current_score = _score(
        counts,
        total_rows,
        label_targets=label_targets,
        total_target=total_target,
    )

    for source_cik in group_order:
        candidate_counts = _combine_counts(counts, group_stats[source_cik]["label_counts"])
        candidate_total = total_rows + int(group_stats[source_cik]["row_count"])
        candidate_score = _score(
            candidate_counts,
            candidate_total,
            label_targets=label_targets,
            total_target=total_target,
        )
        if candidate_score < current_score:
            selected.add(source_cik)
            counts = candidate_counts
            total_rows = candidate_total
            current_score = candidate_score

    improved = True
    while improved:
        improved = False
        best_score = current_score
        best_move: tuple[str, str | None, str | None] | None = None

        for source_cik in group_order:
            if source_cik in selected:
                continue
            candidate_counts = _combine_counts(counts, group_stats[source_cik]["label_counts"])
            candidate_total = total_rows + int(group_stats[source_cik]["row_count"])
            candidate_score = _score(
                candidate_counts,
                candidate_total,
                label_targets=label_targets,
                total_target=total_target,
            )
            if candidate_score < best_score:
                best_score = candidate_score
                best_move = ("add", source_cik, None)

        for source_cik in group_order:
            if source_cik not in selected:
                continue
            candidate_counts = _combine_counts(
                counts, group_stats[source_cik]["label_counts"], factor=-1
            )
            candidate_total = total_rows - int(group_stats[source_cik]["row_count"])
            candidate_score = _score(
                candidate_counts,
                candidate_total,
                label_targets=label_targets,
                total_target=total_target,
            )
            if candidate_score < best_score:
                best_score = candidate_score
                best_move = ("remove", source_cik, None)

        selected_order = [source_cik for source_cik in group_order if source_cik in selected]
        unselected_order = [source_cik for source_cik in group_order if source_cik not in selected]
        for source_cik_out in selected_order:
            removed_counts = _combine_counts(
                counts,
                group_stats[source_cik_out]["label_counts"],
                factor=-1,
            )
            removed_total = total_rows - int(group_stats[source_cik_out]["row_count"])
            for source_cik_in in unselected_order:
                candidate_counts = _combine_counts(
                    removed_counts,
                    group_stats[source_cik_in]["label_counts"],
                )
                candidate_total = removed_total + int(group_stats[source_cik_in]["row_count"])
                candidate_score = _score(
                    candidate_counts,
                    candidate_total,
                    label_targets=label_targets,
                    total_target=total_target,
                )
                if candidate_score < best_score:
                    best_score = candidate_score
                    best_move = ("swap", source_cik_out, source_cik_in)

        if best_move is None:
            break

        operation, left_key, right_key = best_move
        if operation == "add":
            assert left_key is not None
            selected.add(left_key)
            counts = _combine_counts(counts, group_stats[left_key]["label_counts"])
            total_rows += int(group_stats[left_key]["row_count"])
        elif operation == "remove":
            assert left_key is not None
            selected.remove(left_key)
            counts = _combine_counts(counts, group_stats[left_key]["label_counts"], factor=-1)
            total_rows -= int(group_stats[left_key]["row_count"])
        else:
            assert left_key is not None and right_key is not None
            selected.remove(left_key)
            selected.add(right_key)
            counts = _combine_counts(counts, group_stats[left_key]["label_counts"], factor=-1)
            counts = _combine_counts(counts, group_stats[right_key]["label_counts"])
            total_rows -= int(group_stats[left_key]["row_count"])
            total_rows += int(group_stats[right_key]["row_count"])

        current_score = best_score
        improved = True

    return selected, counts, total_rows


def _build_registry(
    frame: pd.DataFrame,
    *,
    validation_groups: set[str],
    split_version: str,
    seed: int,
) -> pd.DataFrame:
    registry = frame[
        [
            "sentence_id",
            "source_cik",
            "label",
            "batch_row_id",
            "sentence_text_id",
            "source_year",
            "manifest_id",
        ]
    ].copy()
    registry["split"] = registry["source_cik"].map(
        lambda source_cik: "validation" if str(source_cik) in validation_groups else "train"
    )
    registry["split_version"] = split_version
    registry["assignment_reason"] = "grouped_source_cik_stratified_80_20_v1"
    registry["seed"] = int(seed)
    registry["source_manifest_id"] = registry["manifest_id"]
    return registry[
        [
            "sentence_id",
            "split",
            "split_version",
            "assignment_reason",
            "seed",
            "source_manifest_id",
            "source_cik",
            "label",
            "batch_row_id",
            "sentence_text_id",
            "source_year",
        ]
    ]


def _cross_split_count(registry: pd.DataFrame, column: str) -> int:
    if column not in registry.columns:
        return 0
    split_counts = registry.groupby(column)["split"].nunique()
    return int((split_counts > 1).sum())


def _write_failure_json(
    output_json: Path,
    *,
    reason: str,
    summary: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "failed",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "failure_reason": reason,
        "inputs": {
            "labels_master": args.labels_master,
            "held_out": args.held_out,
            "labels_master_sha256": _sha256_if_exists(args.labels_master),
            "held_out_sha256": _sha256_if_exists(args.held_out),
        },
        "summary": summary,
    }
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_freeze(args: argparse.Namespace) -> dict[str, Any]:
    output_csv = Path(args.output_csv)
    output_json = Path(args.output_json)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    labels_master = _load_labels_master(args.labels_master)
    heldout_norms, heldout_row_count = _load_heldout(args.held_out)
    group_stats = _group_payload(labels_master)

    label_counts_total = _label_counts(labels_master)
    label_targets = {
        label: int(round(float(args.validation_frac) * label_counts_total[label]))
        for label in ALLOWED_LABELS
    }
    total_target = int(sum(label_targets.values()))
    default_min = max(0, total_target - 10)
    default_max = total_target + 10
    min_validation_rows = (
        int(args.min_validation_rows) if args.min_validation_rows is not None else default_min
    )
    max_validation_rows = (
        int(args.max_validation_rows) if args.max_validation_rows is not None else default_max
    )

    validation_groups, label_actuals, validation_rows = _search_validation_groups(
        group_stats,
        label_targets=label_targets,
        total_target=total_target,
        seed=int(args.seed),
    )
    registry = _build_registry(
        labels_master,
        validation_groups=validation_groups,
        split_version=args.split_version,
        seed=int(args.seed),
    )

    label_deviation = {
        label: int(label_actuals[label] - label_targets[label]) for label in ALLOWED_LABELS
    }
    sentence_id_unique = bool(registry["sentence_id"].is_unique)
    source_cik_cross_split_count = _cross_split_count(registry, "source_cik")
    sentence_text_id_cross_split_count = _cross_split_count(registry, "sentence_text_id")
    heldout_overlap_count = int(
        labels_master["sentence"]
        .fillna("")
        .astype(str)
        .map(normalize_sentence)
        .isin(heldout_norms)
        .sum()
    )

    rows_by_split = {key: int(value) for key, value in registry["split"].value_counts().items()}
    rows_by_split_and_label = (
        registry.groupby(["split", "label"])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=list(ALLOWED_LABELS), fill_value=0)
    )
    rows_by_split_and_label_payload = {
        split: {label: int(rows_by_split_and_label.loc[split, label]) for label in ALLOWED_LABELS}
        for split in rows_by_split_and_label.index
    }
    unique_firms_by_split = {
        split: int(frame["source_cik"].nunique()) for split, frame in registry.groupby("split")
    }

    summary = {
        "rows_total": int(len(registry)),
        "rows_target_validation": total_target,
        "rows_by_split": rows_by_split,
        "rows_by_split_and_label": rows_by_split_and_label_payload,
        "unique_firms_by_split": unique_firms_by_split,
        "label_targets_validation": label_targets,
        "label_actuals_validation": label_actuals,
        "label_deviation_validation": label_deviation,
        "sentence_id_unique": sentence_id_unique,
        "source_cik_cross_split_count": source_cik_cross_split_count,
        "sentence_text_id_cross_split_count": sentence_text_id_cross_split_count,
        "heldout_external": True,
        "heldout_row_count": heldout_row_count,
        "heldout_overlap_count": heldout_overlap_count,
        "validation_groups_selected": int(len(validation_groups)),
        "validation_row_count": validation_rows,
        "validation_row_bounds": {
            "min": min_validation_rows,
            "max": max_validation_rows,
        },
        "max_class_deviation": int(args.max_class_deviation),
    }

    within_tolerance = all(
        abs(label_deviation[label]) <= int(args.max_class_deviation) for label in ALLOWED_LABELS
    )
    registry_valid = (
        len(registry) == len(labels_master)
        and set(registry["split"].unique()) <= {"train", "validation"}
        and sentence_id_unique
        and source_cik_cross_split_count == 0
        and sentence_text_id_cross_split_count == 0
        and min_validation_rows <= validation_rows <= max_validation_rows
        and within_tolerance
        and heldout_overlap_count == 0
    )

    if not registry_valid:
        if output_csv.exists():
            output_csv.unlink()
        reason = (
            "Grouped source_cik split could not satisfy validation size, class-deviation, "
            "or leakage tolerances."
        )
        _write_failure_json(output_json, reason=reason, summary=summary, args=args)
        raise SystemExit(reason)

    registry.to_csv(output_csv, index=False)
    summary["status"] = "frozen"
    summary["assignment_method"] = "grouped_source_cik_stratified_80_20_v1"
    summary["split_version"] = args.split_version
    summary["seed"] = int(args.seed)

    payload = {
        "status": "frozen",
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "labels_master": args.labels_master,
            "held_out": args.held_out,
            "labels_master_sha256": _sha256_if_exists(args.labels_master),
            "held_out_sha256": _sha256_if_exists(args.held_out),
        },
        "outputs": {
            "split_registry_csv": str(output_csv),
            "split_registry_csv_sha256": _sha256_if_exists(output_csv),
            "split_registry_json": str(output_json),
        },
        "summary": summary,
    }
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels-master", default="data/labels/v1/labels_master.parquet")
    parser.add_argument("--held-out", default="data/validation/held_out_sentences.csv")
    parser.add_argument("--output-csv", default="data/metadata/splits/split_registry_v1.csv")
    parser.add_argument("--output-json", default="data/metadata/splits/split_registry_v1.json")
    parser.add_argument("--split-version", default="v1")
    parser.add_argument("--seed", type=int, default=20260315)
    parser.add_argument("--validation-frac", type=float, default=0.20)
    parser.add_argument("--max-class-deviation", type=int, default=5)
    parser.add_argument("--min-validation-rows", type=int, default=None)
    parser.add_argument("--max-validation-rows", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_freeze(args)
    summary = payload["summary"]
    print(
        "[split] frozen "
        f"rows={summary['rows_total']} validation_rows={summary['validation_row_count']} "
        f"firms_validation={summary['unique_firms_by_split'].get('validation', 0)}"
    )
    print(f"[split] csv -> {args.output_csv}")
    print(f"[split] json -> {args.output_json}")


if __name__ == "__main__":
    main()
