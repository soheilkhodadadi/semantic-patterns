"""Combine batch-scoped Iteration 2 sentence-pool artifacts into cumulative outputs."""

from __future__ import annotations

import argparse
import json
import hashlib
from pathlib import Path
from typing import Any

import pandas as pd


def _sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_manifest(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"manifest_id", "manifest_row_id", "cik", "quarter", "filename", "path"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Manifest {path} missing required columns: {missing}")
    frame["source_manifest_path"] = str(path)
    return frame


def _load_sentences(path: str) -> pd.DataFrame:
    frame = pd.read_parquet(path)
    required = {
        "sentence_id",
        "sentence_text_id",
        "sentence",
        "sentence_norm",
        "source_file",
        "source_year",
        "source_quarter",
        "source_form",
        "source_cik",
        "sentence_index",
        "manifest_id",
        "source_window_id",
        "token_count",
        "fragment_score",
        "integrity_flags",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Sentence parquet {path} missing required columns: {missing}")
    frame["source_sentence_batch_path"] = str(path)
    return frame


def combine_expanded_sentence_pool_batches(
    *,
    manifest_paths: list[str],
    sentence_paths: list[str],
    output_manifest_path: str,
    output_sentences_path: str,
    report_path: str,
) -> dict[str, Any]:
    if not manifest_paths or not sentence_paths:
        raise ValueError("At least one manifest and one sentence parquet are required.")
    if len(manifest_paths) != len(sentence_paths):
        raise ValueError("Manifest and sentence path counts must match.")

    manifests = pd.concat([_load_manifest(path) for path in manifest_paths], ignore_index=True)
    manifests.sort_values(["quarter", "path", "filename", "manifest_row_id"], inplace=True)
    manifests.reset_index(drop=True, inplace=True)

    duplicate_firm_mask = manifests["cik"].astype(str).duplicated(keep=False)
    duplicate_firm_count = int(duplicate_firm_mask.sum())
    if duplicate_firm_count:
        duplicate_firms = sorted(manifests.loc[duplicate_firm_mask, "cik"].astype(str).unique())
        raise ValueError(
            "Duplicate CIKs detected across expansion manifests: " + ", ".join(duplicate_firms)
        )

    sentences = pd.concat([_load_sentences(path) for path in sentence_paths], ignore_index=True)
    sentences.sort_values(["source_file", "sentence_index", "sentence_id"], inplace=True)
    sentences.reset_index(drop=True, inplace=True)

    duplicate_sentence_text_count = int(sentences["sentence_text_id"].duplicated().sum())
    sentences = sentences.drop_duplicates(subset=["sentence_text_id"], keep="first").copy()
    sentences.sort_values(["source_file", "sentence_index", "sentence_id"], inplace=True)
    sentences.reset_index(drop=True, inplace=True)

    output_manifest = Path(output_manifest_path)
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    manifests.to_csv(output_manifest, index=False)

    output_sentences = Path(output_sentences_path)
    output_sentences.parent.mkdir(parents=True, exist_ok=True)
    sentences.to_parquet(output_sentences, index=False, engine="pyarrow", compression="snappy")

    report = {
        "manifest": {
            "input_manifest_paths": [str(Path(path)) for path in manifest_paths],
            "input_sentence_paths": [str(Path(path)) for path in sentence_paths],
            "combined_filing_count": int(len(manifests)),
            "combined_batch_count": int(len(manifest_paths)),
        },
        "candidate_pool": {
            "firm_count": int(manifests["cik"].astype(str).nunique()),
            "filing_count": int(len(manifests)),
            "clean_sentence_count": int(len(sentences)),
            "quarter_counts": {
                str(int(key)): int(value)
                for key, value in manifests["quarter"]
                .astype(int)
                .value_counts()
                .sort_index()
                .items()
            },
            "ff12_known_filing_count": int(
                (
                    manifests.get("industry_metadata_source", pd.Series(dtype=str))
                    .astype(str)
                    .str.lower()
                    != "unknown"
                ).sum()
            ),
            "ff12_unknown_filing_count": int(
                (
                    manifests.get("industry_metadata_source", pd.Series(dtype=str))
                    .astype(str)
                    .str.lower()
                    == "unknown"
                ).sum()
            ),
        },
        "quality": {
            "duplicate_firm_count": duplicate_firm_count,
            "duplicate_sentence_text_count_removed": duplicate_sentence_text_count,
            "post_combine_duplicate_sentence_text_count": int(
                sentences["sentence_text_id"].duplicated().sum()
            ),
        },
        "artifacts": {
            "manifest": str(output_manifest),
            "expanded_sentence_table": str(output_sentences),
            "manifest_sha256": _sha256_file(output_manifest),
            "expanded_sentence_table_sha256": _sha256_file(output_sentences),
        },
    }

    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifests", nargs="+", required=True)
    parser.add_argument("--sentences", nargs="+", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--output-sentences", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = combine_expanded_sentence_pool_batches(
        manifest_paths=args.manifests,
        sentence_paths=args.sentences,
        output_manifest_path=args.output_manifest,
        output_sentences_path=args.output_sentences,
        report_path=args.report,
    )
    print(
        "[sentence-pool-combine] "
        f"firms={report['candidate_pool']['firm_count']} "
        f"clean_sentences={report['candidate_pool']['clean_sentence_count']}"
    )
    print(f"[sentence-pool-combine] manifest -> {args.output_manifest}")
    print(f"[sentence-pool-combine] sentences -> {args.output_sentences}")
    print(f"[sentence-pool-combine] summary -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
