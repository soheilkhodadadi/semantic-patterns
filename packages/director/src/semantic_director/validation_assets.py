"""Generate a canonical registry for current validation assets."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.labeling.common import normalize_sentence, row_sha256
from semantic_labcore.runtime import dump_json, git_info, now_utc_iso, sha256_file

DEFAULT_HELD_OUT = "data/validation/held_out_sentences.csv"
DEFAULT_COLLECTED = "data/validation/CollectedAiSentencesClassifiedCleaned.csv"
DEFAULT_HAND_LABELED = "data/validation/hand_labeled_ai_sentences_with_embeddings_revised.csv"
DEFAULT_HELD_OUT_V2 = "data/validation/held_out_sentences_v2.csv"
DEFAULT_IRR_BOUNDARY = "data/validation/irr_boundary_benchmark_v1.csv"
DEFAULT_OUTPUT = "reports/validation/validation_asset_registry.json"


def _resolve(path: str | Path) -> Path:
    return Path(path).resolve()


def _mtime_iso(path: Path) -> str:
    return pd.Timestamp(path.stat().st_mtime, unit="s", tz="UTC").isoformat()


def _load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _normalized_pairs(df: pd.DataFrame) -> list[str]:
    if "sentence" not in df.columns or "label" not in df.columns:
        return []
    pairs = []
    for row in df[["sentence", "label"]].fillna("").itertuples(index=False):
        sentence_norm = normalize_sentence(row.sentence)
        label = str(row.label).strip()
        pairs.append(f"{sentence_norm}\t{label}")
    return sorted(pairs)


def _sentence_norms(df: pd.DataFrame) -> list[str]:
    if "sentence" not in df.columns:
        return []
    return [normalize_sentence(value) for value in df["sentence"].fillna("").astype(str)]


def _asset_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "sha256": "",
            "size_bytes": 0,
            "modified_at": "",
            "row_count": 0,
            "columns": [],
            "label_distribution": {},
            "normalized_sentence_count": 0,
            "unique_normalized_sentence_count": 0,
            "normalized_pair_digest": "",
        }
    df = _load_dataset(path)
    sentence_norms = _sentence_norms(df)
    pair_rows = _normalized_pairs(df)
    label_distribution = (
        df["label"].fillna("<missing>").astype(str).value_counts(dropna=False).to_dict()
        if "label" in df.columns
        else {}
    )
    return {
        "path": str(path),
        "exists": True,
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "modified_at": _mtime_iso(path),
        "row_count": int(len(df)),
        "columns": df.columns.tolist(),
        "label_distribution": label_distribution,
        "normalized_sentence_count": int(sum(1 for item in sentence_norms if item)),
        "unique_normalized_sentence_count": int(len({item for item in sentence_norms if item})),
        "normalized_pair_digest": row_sha256(pair_rows),
    }


def classify_dataset_relationship(
    base_df: pd.DataFrame, candidate_df: pd.DataFrame
) -> dict[str, Any]:
    base_pairs = _normalized_pairs(base_df)
    candidate_pairs = _normalized_pairs(candidate_df)
    base_sentences = set(_sentence_norms(base_df))
    candidate_sentences = set(_sentence_norms(candidate_df))

    base_sentences.discard("")
    candidate_sentences.discard("")

    overlap_sentences = base_sentences & candidate_sentences
    exact_sentence_label_match = base_pairs == candidate_pairs
    exact_sentence_match = base_sentences == candidate_sentences and len(base_df) == len(
        candidate_df
    )

    if exact_sentence_label_match:
        relationship = "historical_duplicate"
    elif exact_sentence_match:
        relationship = "label_variant_duplicate"
    elif overlap_sentences:
        relationship = "partial_overlap"
    else:
        relationship = "distinct"

    return {
        "relationship": relationship,
        "exact_sentence_label_match": exact_sentence_label_match,
        "exact_sentence_match": exact_sentence_match,
        "base_row_count": int(len(base_df)),
        "candidate_row_count": int(len(candidate_df)),
        "normalized_sentence_overlap_count": int(len(overlap_sentences)),
        "normalized_sentence_overlap_ratio": float(
            len(overlap_sentences) / max(len(base_sentences), 1)
        ),
    }


def build_validation_asset_registry(
    held_out_path: str = DEFAULT_HELD_OUT,
    collected_path: str = DEFAULT_COLLECTED,
    hand_labeled_path: str = DEFAULT_HAND_LABELED,
    output_path: str = DEFAULT_OUTPUT,
    held_out_v2_path: str = DEFAULT_HELD_OUT_V2,
    irr_boundary_path: str = DEFAULT_IRR_BOUNDARY,
) -> dict[str, Any]:
    held_out = _resolve(held_out_path)
    collected = _resolve(collected_path)
    hand_labeled = _resolve(hand_labeled_path)
    held_out_v2 = _resolve(held_out_v2_path)
    irr_boundary = _resolve(irr_boundary_path)

    held_out_df = _load_dataset(held_out)
    collected_df = _load_dataset(collected)
    hand_labeled_df = _load_dataset(hand_labeled)

    heldout_vs_collected = classify_dataset_relationship(held_out_df, collected_df)
    heldout_vs_hand = classify_dataset_relationship(held_out_df, hand_labeled_df)

    collected_role = {
        "historical_duplicate": "historical_duplicate_of_held_out",
        "label_variant_duplicate": "held_out_variant_candidate",
        "partial_overlap": "partial_overlap_candidate",
        "distinct": "distinct_validation_asset",
    }[heldout_vs_collected["relationship"]]

    has_v2 = held_out_v2.exists()
    has_boundary = irr_boundary.exists()
    held_out_role = "historical_benchmark_v1" if has_v2 else "canonical_frozen_evaluation_set"

    payload = {
        "generated_at": now_utc_iso(),
        "git": git_info(),
        "canonical_current_rubric_evaluation_asset": str(held_out_v2) if has_v2 else "",
        "historical_benchmark_asset": str(held_out),
        "boundary_benchmark_asset": str(irr_boundary) if has_boundary else "",
        "assets": {
            "held_out_sentences": {
                "role": held_out_role,
                **_asset_summary(held_out),
            },
            "held_out_sentences_v2": {
                "role": (
                    "canonical_current_rubric_evaluation_set"
                    if has_v2
                    else "planned_canonical_current_rubric_evaluation_set"
                ),
                **_asset_summary(held_out_v2),
            },
            "irr_boundary_benchmark_v1": {
                "role": "boundary_benchmark_v1"
                if has_boundary
                else "planned_boundary_benchmark_v1",
                **_asset_summary(irr_boundary),
            },
            "collected_ai_sentences_classified_cleaned": {
                "role": collected_role,
                **_asset_summary(collected),
            },
            "hand_labeled_with_embeddings_revised": {
                "role": "historical_training_seed_with_embeddings",
                **_asset_summary(hand_labeled),
            },
        },
        "relationships": {
            "held_out_vs_collected_cleaned": heldout_vs_collected,
            "held_out_vs_hand_labeled": heldout_vs_hand,
        },
        "decisions": {
            "held_out_sentences.csv": (
                "preserve as historical_benchmark_v1 once held_out_sentences_v2 is frozen"
                if has_v2
                else "freeze as evaluation-only canonical asset"
            ),
            "held_out_sentences_v2.csv": (
                "treat as canonical current-rubric evaluation asset"
                if has_v2
                else "planned current-rubric evaluation asset pending review and freeze"
            ),
            "irr_boundary_benchmark_v1.csv": (
                "retain as diagnostic-only boundary benchmark"
                if has_boundary
                else "planned diagnostic-only boundary benchmark pending publication"
            ),
            "CollectedAiSentencesClassifiedCleaned.csv": (
                f"classify as {collected_role} relative to held_out_sentences.csv"
            ),
            "hand_labeled_ai_sentences_with_embeddings_revised.csv": (
                "retain as historical training seed with embeddings; do not treat as held-out"
            ),
        },
    }

    if has_v2:
        held_out_v2_df = _load_dataset(held_out_v2)
        payload["relationships"]["held_out_v2_vs_historical_held_out"] = (
            classify_dataset_relationship(
                held_out_v2_df,
                held_out_df,
            )
        )
        if has_boundary:
            irr_boundary_df = _load_dataset(irr_boundary)
            payload["relationships"]["held_out_v2_vs_irr_boundary_benchmark"] = (
                classify_dataset_relationship(held_out_v2_df, irr_boundary_df)
            )
    elif has_boundary:
        irr_boundary_df = _load_dataset(irr_boundary)
        payload["relationships"]["historical_held_out_vs_irr_boundary_benchmark"] = (
            classify_dataset_relationship(held_out_df, irr_boundary_df)
        )

    dump_json(output_path, payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--held-out", default=DEFAULT_HELD_OUT)
    parser.add_argument("--collected", default=DEFAULT_COLLECTED)
    parser.add_argument("--hand-labeled", default=DEFAULT_HAND_LABELED)
    parser.add_argument("--held-out-v2", default=DEFAULT_HELD_OUT_V2)
    parser.add_argument("--irr-boundary", default=DEFAULT_IRR_BOUNDARY)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_validation_asset_registry(
        held_out_path=args.held_out,
        collected_path=args.collected,
        hand_labeled_path=args.hand_labeled,
        held_out_v2_path=args.held_out_v2,
        irr_boundary_path=args.irr_boundary,
        output_path=args.output,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
