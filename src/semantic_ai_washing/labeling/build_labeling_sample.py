"""Build Phase 1 labeling sample with leakage controls and stable IDs."""

from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import subprocess
from collections import Counter
from pathlib import Path

import pandas as pd

from semantic_ai_washing.labeling.common import (
    ALLOWED_LABELS,
    compute_sample_id,
    compute_sentence_id,
    ensure_allowed_label,
    length_bin_from_tokens,
    normalize_sentence,
    token_count,
)
from semantic_ai_washing.labeling.ff12_mapping import map_sic_to_ff12

_FORM_RE = re.compile(r"^\d{8}_(?P<form>[^_]+)_")
_CIK_RE = re.compile(r"edgar_data_(\d+)_")
_YEAR_PREFIX_RE = re.compile(r"^(?P<year>\d{4})")
_EDGE_CASE_RE = re.compile(
    r"\b(may|might|could|intend|plan|expect|future|transform|revolution|generative ai|risk|uncertain|aim|seek|hope)\b",
    re.I,
)

OUTPUT_COLUMNS = [
    "sample_id",
    "sentence_id",
    "sentence",
    "sentence_norm",
    "label",
    "is_uncertain",
    "uncertainty_note",
    "source_file",
    "source_year",
    "source_form",
    "source_cik",
    "sentence_index",
    "sic",
    "sic2",
    "ff12_code",
    "ff12_name",
    "token_count",
    "length_bin",
    "edge_case_flag",
]


def _parse_years_filter(years: str) -> set[str]:
    return {token.strip() for token in str(years or "").split(",") if token.strip()}


def _git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
        return out.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _normalize_cik(value: str) -> str:
    text = str(value or "").strip()
    return text.lstrip("0") or "0"


def _parse_metadata_from_file(path: str) -> tuple[str, str, str]:
    filename = os.path.basename(path)
    year = os.path.basename(os.path.dirname(path))
    if not year.isdigit() or len(year) != 4:
        year_match = _YEAR_PREFIX_RE.match(filename)
        year = year_match.group("year") if year_match else ""
    form_match = _FORM_RE.match(filename)
    form = form_match.group("form") if form_match else "unknown"
    cik_match = _CIK_RE.search(filename)
    cik = _normalize_cik(cik_match.group(1)) if cik_match else ""
    return year, form, cik


def _load_sic_maps(
    controls_path: str, crosswalk_path: str
) -> tuple[dict[tuple[str, str], str], dict[str, str]]:
    by_cik_year: dict[tuple[str, str], str] = {}
    by_cik: dict[str, str] = {}

    if os.path.exists(controls_path):
        with open(controls_path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cik = _normalize_cik(row.get("cik", ""))
                year = str(row.get("year", "")).strip()
                sic = str(row.get("sic", "")).strip()
                if cik and year and sic:
                    by_cik_year[(cik, year)] = sic
                    by_cik.setdefault(cik, sic)

    if os.path.exists(crosswalk_path):
        with open(crosswalk_path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cik = _normalize_cik(row.get("cik", ""))
                sic = str(row.get("sic", "")).strip()
                if cik and sic and cik not in by_cik:
                    by_cik[cik] = sic
    return by_cik_year, by_cik


def _load_heldout_norms(path: str) -> set[str]:
    heldout: set[str] = set()
    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            norm = normalize_sentence(row.get("sentence", ""))
            if norm:
                heldout.add(norm)
    return heldout


def _coerce_sic2(sic: str) -> str:
    if not sic:
        return ""
    try:
        return str(int(float(sic)) // 100)
    except (TypeError, ValueError):
        return ""


def _load_label_suggestions(ai_file: str, sentences: list[str]) -> list[str]:
    allowed = set(ALLOWED_LABELS)
    suggestions = [""] * len(sentences)
    by_norm: dict[str, str] = {}

    csv_path = ai_file.replace("_ai_sentences.txt", "_classified.csv")
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        for idx, row in enumerate(rows):
            label = ensure_allowed_label(row.get("label_pred", "")) or ensure_allowed_label(
                row.get("label", "")
            )
            sent = row.get("sentence", "")
            if label in allowed and idx < len(suggestions):
                suggestions[idx] = label
            norm = normalize_sentence(sent)
            if norm and label in allowed and norm not in by_norm:
                by_norm[norm] = label

    txt_path = ai_file.replace("_ai_sentences.txt", "_classified.txt")
    if os.path.exists(txt_path):
        with open(txt_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if " | Label: " not in line:
                    continue
                sent_part, label_part = line.split(" | Label: ", 1)
                label = ensure_allowed_label(label_part.split(" |", 1)[0].strip())
                norm = normalize_sentence(sent_part)
                if norm and label in allowed and norm not in by_norm:
                    by_norm[norm] = label

    for idx, sentence in enumerate(sentences):
        if suggestions[idx]:
            continue
        norm = normalize_sentence(sentence)
        if norm in by_norm:
            suggestions[idx] = by_norm[norm]
    return suggestions


def _length_priority_map(df: pd.DataFrame) -> dict[str, int]:
    counts = Counter(df["length_bin"].tolist())
    order = sorted(counts, key=lambda k: (counts[k], k))
    return {key: idx for idx, key in enumerate(order)}


def _allocate_year_quotas(year_availability: dict[str, int], total_target: int) -> dict[str, int]:
    years = sorted(year_availability)
    quotas = {year: 0 for year in years}
    if not years or total_target <= 0:
        return quotas

    base = total_target // len(years)
    remainder = total_target % len(years)
    for idx, year in enumerate(years):
        desired = base + (1 if idx < remainder else 0)
        quotas[year] = min(desired, year_availability[year])

    assigned = sum(quotas.values())
    while assigned < total_target:
        progressed = False
        candidates = sorted(
            years,
            key=lambda y: (year_availability[y] - quotas[y], y),
            reverse=True,
        )
        for year in candidates:
            if quotas[year] < year_availability[year]:
                quotas[year] += 1
                assigned += 1
                progressed = True
                if assigned == total_target:
                    break
        if not progressed:
            break
    return quotas


def _priority_key(
    row: dict,
    year_quotas: dict[str, int],
    year_counts: Counter,
    label_counts: Counter,
    min_class_target: int,
    length_priority: dict[str, int],
) -> tuple:
    year = row["source_year"]
    year_deficit = year_quotas.get(year, 0) - year_counts.get(year, 0)
    label = row.get("label_suggested", "")
    label_deficit = max(0, min_class_target - label_counts.get(label, 0)) if label else 0
    return (
        0 if year_deficit > 0 else 1,
        -year_deficit,
        0 if row.get("has_suggested") else 1,
        0 if row.get("edge_case_flag") else 1,
        -label_deficit,
        length_priority.get(row.get("length_bin", ""), 99),
        row.get("rand", 0.0),
        row.get("sample_id", ""),
    )


def _sample_candidates(
    candidates_df: pd.DataFrame,
    new_target: int,
    seed: int,
    base_class_counts: Counter,
    min_class_target: int,
) -> tuple[pd.DataFrame, dict]:
    if new_target <= 0 or candidates_df.empty:
        return candidates_df.head(0).copy(), {
            "new_target": new_target,
            "selected_count": 0,
            "year_quotas": {},
            "ff12_floor": 0,
            "ff12_floor_feasible": True,
        }

    rng = random.Random(seed)
    pool = candidates_df.copy().reset_index(drop=True)
    pool["rand"] = [rng.random() for _ in range(len(pool))]
    pool["has_suggested"] = pool["label_suggested"].isin(ALLOWED_LABELS)

    # Prefer rows with suggested labels first (manual workflow can overwrite later).
    pool = pool.sort_values(
        by=["has_suggested", "edge_case_flag", "token_count", "rand"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)
    if len(pool) < new_target:
        new_target = len(pool)

    year_availability = {
        year: int(count) for year, count in pool["source_year"].value_counts().to_dict().items()
    }
    year_quotas = _allocate_year_quotas(year_availability, new_target)
    year_counts: Counter = Counter()
    label_counts: Counter = Counter(base_class_counts)
    selected_indices: list[int] = []
    remaining = set(pool.index.tolist())
    length_priority = _length_priority_map(pool)

    ff12_groups = sorted(pool["ff12_code"].astype(str).unique().tolist())
    ff12_bucket_count = len(ff12_groups)
    ff12_floor_feasible = ff12_bucket_count * 12 <= new_target if ff12_bucket_count else True
    ff12_floor = 12 if ff12_floor_feasible else (new_target // max(ff12_bucket_count, 1))
    ff12_floor = min(ff12_floor, 12)

    for ff12 in ff12_groups:
        if len(selected_indices) >= new_target or ff12_floor == 0:
            break
        ff_indices = [
            idx
            for idx in pool.index.tolist()
            if idx in remaining and str(pool.at[idx, "ff12_code"]) == str(ff12)
        ]
        picks = min(ff12_floor, len(ff_indices), new_target - len(selected_indices))
        for _ in range(picks):
            if not ff_indices:
                break
            best = min(
                ff_indices,
                key=lambda idx: _priority_key(
                    pool.loc[idx].to_dict(),
                    year_quotas,
                    year_counts,
                    label_counts,
                    min_class_target,
                    length_priority,
                ),
            )
            selected_indices.append(best)
            remaining.discard(best)
            ff_indices.remove(best)
            year_counts[pool.at[best, "source_year"]] += 1
            label = pool.at[best, "label_suggested"]
            if label in ALLOWED_LABELS:
                label_counts[label] += 1

    while len(selected_indices) < new_target and remaining:
        years_with_capacity = [
            year
            for year in year_quotas
            if any(idx in remaining and pool.at[idx, "source_year"] == year for idx in remaining)
        ]
        if years_with_capacity:
            target_year = max(
                years_with_capacity,
                key=lambda year: (
                    year_quotas.get(year, 0) - year_counts.get(year, 0),
                    year_availability.get(year, 0),
                    year,
                ),
            )
            candidates = [idx for idx in remaining if pool.at[idx, "source_year"] == target_year]
            if not candidates:
                candidates = list(remaining)
        else:
            candidates = list(remaining)

        best = min(
            candidates,
            key=lambda idx: _priority_key(
                pool.loc[idx].to_dict(),
                year_quotas,
                year_counts,
                label_counts,
                min_class_target,
                length_priority,
            ),
        )
        selected_indices.append(best)
        remaining.discard(best)
        year_counts[pool.at[best, "source_year"]] += 1
        label = pool.at[best, "label_suggested"]
        if label in ALLOWED_LABELS:
            label_counts[label] += 1

    sampled = pool.loc[selected_indices].copy()
    sampled = sampled.sort_values(
        by=["source_year", "source_file", "sentence_index", "sample_id"]
    ).reset_index(drop=True)

    summary = {
        "new_target": int(new_target),
        "selected_count": int(len(sampled)),
        "year_quotas": {k: int(v) for k, v in year_quotas.items()},
        "year_selected": {k: int(v) for k, v in year_counts.items()},
        "ff12_floor": int(ff12_floor),
        "ff12_floor_feasible": bool(ff12_floor_feasible),
        "selected_label_suggested_counts": sampled["label_suggested"].value_counts().to_dict(),
        "selected_ff12_counts": sampled["ff12_code"].astype(str).value_counts().to_dict(),
        "selected_length_counts": sampled["length_bin"].value_counts().to_dict(),
        "selected_edge_case_count": int(sampled["edge_case_flag"].astype(int).sum()),
    }
    return sampled, summary


def run_build(args: argparse.Namespace) -> dict:
    output_dir = Path(args.output_dir)
    report_dir = Path(args.report_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    heldout_norms = _load_heldout_norms(args.held_out)
    base_raw = pd.read_csv(args.base_labeled)
    if "sentence" not in base_raw.columns or "label" not in base_raw.columns:
        raise ValueError("Base labeled file must contain `sentence` and `label` columns.")

    base_raw["sentence"] = base_raw["sentence"].astype(str)
    base_raw["label"] = base_raw["label"].map(ensure_allowed_label)
    base_raw["sentence_norm"] = base_raw["sentence"].map(normalize_sentence)
    base_raw = base_raw[base_raw["sentence_norm"] != ""].copy()
    base_raw = base_raw[base_raw["label"].notnull()].copy()

    before_base = len(base_raw)
    base_exact_removed = int(base_raw["sentence_norm"].duplicated().sum())
    base_raw = base_raw.drop_duplicates(subset=["sentence_norm"], keep="first").copy()
    base_overlap_mask = base_raw["sentence_norm"].isin(heldout_norms)
    base_overlap_removed = int(base_overlap_mask.sum())
    base_nonleaky = base_raw[~base_overlap_mask].copy().reset_index(drop=True)

    base_rows: list[dict] = []
    for idx, row in base_nonleaky.iterrows():
        sentence = row["sentence"]
        sentence_norm = row["sentence_norm"]
        tokens = token_count(sentence)
        ff_bucket = map_sic_to_ff12("")
        base_rows.append(
            {
                "sample_id": compute_sample_id("base_labeled", idx + 1, sentence_norm),
                "sentence_id": compute_sentence_id(sentence_norm),
                "sentence": sentence,
                "sentence_norm": sentence_norm,
                "label": row["label"],
                "is_uncertain": 0,
                "uncertainty_note": "",
                "source_file": "base_labeled",
                "source_year": "",
                "source_form": "",
                "source_cik": "",
                "sentence_index": idx + 1,
                "sic": "",
                "sic2": "",
                "ff12_code": ff_bucket.code,
                "ff12_name": ff_bucket.name,
                "token_count": tokens,
                "length_bin": length_bin_from_tokens(tokens),
                "edge_case_flag": bool(_EDGE_CASE_RE.search(sentence)),
                "label_suggested": row["label"],
            }
        )

    base_df = pd.DataFrame(base_rows)
    base_output = output_dir / "base_labeled_nonleaky.csv"
    base_df[OUTPUT_COLUMNS].to_csv(base_output, index=False)

    by_cik_year, by_cik = _load_sic_maps(args.controls, args.crosswalk)

    candidate_records: list[dict] = []
    years_filter = _parse_years_filter(getattr(args, "years", ""))
    max_ai_files = int(getattr(args, "max_ai_files", 0) or 0)
    ai_files_all = sorted(Path(args.input_dir).rglob("*_ai_sentences.txt"))
    ai_files_considered = len(ai_files_all)
    ai_files_skipped_by_year_filter = 0
    if years_filter:
        ai_files_filtered: list[Path] = []
        for ai_file in ai_files_all:
            source_year, _, _ = _parse_metadata_from_file(str(ai_file))
            if source_year in years_filter:
                ai_files_filtered.append(ai_file)
            else:
                ai_files_skipped_by_year_filter += 1
        ai_files = ai_files_filtered
    else:
        ai_files = ai_files_all
    if max_ai_files > 0:
        ai_files = ai_files[:max_ai_files]
    ai_files_processed = len(ai_files)

    for ai_file in ai_files:
        source_year, source_form, source_cik = _parse_metadata_from_file(str(ai_file))
        sic = by_cik_year.get((source_cik, source_year), by_cik.get(source_cik, ""))
        sic2 = _coerce_sic2(sic)
        ff_bucket = map_sic_to_ff12(sic)

        with ai_file.open("r", encoding="utf-8", errors="ignore") as f:
            sentences = [line.strip() for line in f if line.strip()]
        if not sentences:
            continue
        suggestions = _load_label_suggestions(str(ai_file), sentences)

        for idx, sentence in enumerate(sentences, start=1):
            sentence_norm = normalize_sentence(sentence)
            if not sentence_norm:
                continue
            tokens = token_count(sentence)
            label_suggested = ensure_allowed_label(suggestions[idx - 1]) or ""
            candidate_records.append(
                {
                    "sample_id": compute_sample_id(str(ai_file), idx, sentence_norm),
                    "sentence_id": compute_sentence_id(sentence_norm),
                    "sentence": sentence,
                    "sentence_norm": sentence_norm,
                    "label": "",
                    "is_uncertain": "",
                    "uncertainty_note": "",
                    "source_file": str(ai_file),
                    "source_year": source_year,
                    "source_form": source_form,
                    "source_cik": source_cik,
                    "sentence_index": idx,
                    "sic": sic,
                    "sic2": sic2,
                    "ff12_code": ff_bucket.code,
                    "ff12_name": ff_bucket.name,
                    "token_count": tokens,
                    "length_bin": length_bin_from_tokens(tokens),
                    "edge_case_flag": bool(_EDGE_CASE_RE.search(sentence)),
                    "label_suggested": label_suggested,
                }
            )

    candidates = pd.DataFrame(candidate_records)
    if candidates.empty:
        raise RuntimeError("No candidate AI sentences found for sampling.")

    total_candidates = len(candidates)
    candidates = candidates[candidates["token_count"] >= args.min_tokens].copy()
    token_filtered_out = total_candidates - len(candidates)

    base_norms = set(base_df["sentence_norm"].tolist())
    overlap_mask = candidates["sentence_norm"].isin(heldout_norms | base_norms)
    overlap_removed = int(overlap_mask.sum())
    candidates = candidates[~overlap_mask].copy()

    pre_dedupe_count = len(candidates)
    candidates = candidates.sort_values(
        by=["source_year", "source_file", "sentence_index", "sample_id"]
    ).drop_duplicates(subset=["sentence_norm"], keep="first")
    candidate_deduped_removed = pre_dedupe_count - len(candidates)
    candidates = candidates.reset_index(drop=True)

    base_non_uncertain_count = int((base_df["is_uncertain"].astype(int) == 0).sum())
    new_target = max(0, args.target_total - base_non_uncertain_count)
    sampled_df, sample_summary = _sample_candidates(
        candidates_df=candidates,
        new_target=new_target,
        seed=args.seed,
        base_class_counts=Counter(base_df["label"].tolist()),
        min_class_target=args.min_class_target,
    )

    manual_df = sampled_df.copy()
    manual_df["label"] = ""
    manual_df["is_uncertain"] = ""
    manual_df["uncertainty_note"] = ""
    manual_path = output_dir / "labeling_sheet_for_manual.csv"
    manual_cols = OUTPUT_COLUMNS + ["label_suggested"]
    manual_df[manual_cols].to_csv(manual_path, index=False)

    # Convenience template: label suggestions pre-filled (can be edited manually).
    completed_df = sampled_df.copy()
    completed_df["label"] = completed_df["label_suggested"]
    completed_df["is_uncertain"] = completed_df["label"].eq("").map({True: 1, False: 0})
    completed_df["uncertainty_note"] = (
        completed_df["label"].eq("").map({True: "missing_label_suggestion", False: ""})
    )
    completed_path = output_dir / "labeling_sheet_completed.csv"
    completed_df[manual_cols].to_csv(completed_path, index=False)

    summary = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "inputs": {
            "base_labeled": args.base_labeled,
            "held_out": args.held_out,
            "input_dir": args.input_dir,
            "controls": args.controls,
            "crosswalk": args.crosswalk,
        },
        "parameters": {
            "target_total": args.target_total,
            "new_target": new_target,
            "seed": args.seed,
            "min_tokens": args.min_tokens,
            "min_class_target": args.min_class_target,
            "years_filter": sorted(years_filter),
            "max_ai_files": max_ai_files,
        },
        "base_stats": {
            "rows_before_cleaning": before_base,
            "exact_or_canonical_duplicates_removed": base_exact_removed,
            "heldout_overlap_removed": base_overlap_removed,
            "rows_after_cleaning": int(len(base_df)),
            "class_counts": base_df["label"].value_counts().to_dict(),
        },
        "candidate_stats": {
            "ai_files_considered": int(ai_files_considered),
            "ai_files_processed": int(ai_files_processed),
            "ai_files_skipped_by_year_filter": int(ai_files_skipped_by_year_filter),
            "rows_total": int(total_candidates),
            "removed_below_min_tokens": int(token_filtered_out),
            "removed_leakage_overlap": int(overlap_removed),
            "removed_exact_or_canonical_duplicates": int(candidate_deduped_removed),
            "rows_after_filters": int(len(candidates)),
        },
        "sampling": sample_summary,
        "artifacts": {
            "base_nonleaky": str(base_output),
            "labeling_sheet_for_manual": str(manual_path),
            "labeling_sheet_completed_template": str(completed_path),
        },
    }
    summary_path = report_dir / "sampling_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Phase 1 labeling sample.")
    parser.add_argument("--target-total", type=int, default=400)
    parser.add_argument(
        "--held-out",
        default="data/validation/held_out_sentences.csv",
        help="Canonical held-out sentences file to exclude from training pool.",
    )
    parser.add_argument(
        "--base-labeled",
        default="data/validation/hand_labeled_ai_sentences_labeled_cleaned_revised.csv",
    )
    parser.add_argument("--input-dir", default="data/processed/sec")
    parser.add_argument("--controls", default="data/interim/controls/controls_by_firm_year.csv")
    parser.add_argument("--crosswalk", default="data/externals/crosswalks/cik_gvkey.csv")
    parser.add_argument(
        "--years",
        default="",
        help="Optional comma-separated years filter for *_ai_sentences inputs (e.g., 2023,2024).",
    )
    parser.add_argument(
        "--max-ai-files",
        type=int,
        default=0,
        help="Optional cap on number of *_ai_sentences files processed after filtering.",
    )
    parser.add_argument("--output-dir", default="data/labels/iteration1")
    parser.add_argument("--report-dir", default="reports/iteration1/phase1")
    parser.add_argument("--seed", type=int, default=20260227)
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--min-class-target", type=int, default=60)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = run_build(args)
    print(
        f"[phase1] base_nonleaky={summary['base_stats']['rows_after_cleaning']} "
        f"new_target={summary['parameters']['new_target']} "
        f"sampled={summary['sampling']['selected_count']}"
    )
    print(f"[phase1] sampling summary -> {Path(args.report_dir) / 'sampling_summary.json'}")


if __name__ == "__main__":
    main()
