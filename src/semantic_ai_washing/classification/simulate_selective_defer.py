"""Simulate selective-defer classifier variants on a reviewed benchmark."""

from __future__ import annotations

import argparse
import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.classification.benchmark_utils import compute_metrics
from ai_washing_member.classification.preliminary_pipeline import embed_sentences
def _resolve(path: str | Path) -> Path:
    return Path(path).resolve()


def _load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(_resolve(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return payload


def _load_pickle(path: str | Path) -> Any:
    with _resolve(path).open("rb") as handle:
        return pickle.load(handle)


@dataclass(frozen=True)
class PolicySpec:
    name: str
    description: str
    low_confidence_threshold: float | None = None
    low_as_margin_threshold: float | None = None
    require_component_disagreement: bool = False
    require_local_logreg_disagreement: bool = False
    oracle_error_only: bool = False
    api_b_majority: bool = False
    deployable: bool = True


def _conditional_as_probs(row: pd.Series) -> tuple[float, float, float]:
    a_raw = float(row["logreg_prob_actionable"])
    s_raw = float(row["logreg_prob_speculative"])
    as_mass = a_raw + s_raw
    if as_mass <= 0:
        return 0.5, 0.5, 0.0
    return a_raw / as_mass, s_raw / as_mass, as_mass


def _binary_top_label(p_irrelevant: float, p_non_irrelevant: float) -> str:
    return "Irrelevant" if p_irrelevant >= p_non_irrelevant else "Non-Irrelevant"


def _majority_vote(local_label: str, api_a_label: str, api_b_label: str | None) -> str:
    if not api_b_label:
        return api_a_label
    if local_label == api_a_label or local_label == api_b_label:
        return local_label
    if api_a_label == api_b_label:
        return api_a_label
    return api_b_label


def _should_defer(row: pd.Series, policy: PolicySpec) -> bool:
    if policy.oracle_error_only:
        return bool(row["local_label"] != row["label"])

    triggers: list[bool] = []
    if policy.low_confidence_threshold is not None:
        triggers.append(float(row["local_confidence"]) < policy.low_confidence_threshold)
    if policy.low_as_margin_threshold is not None:
        if str(row["local_label"]) == "Irrelevant":
            triggers.append(False)
        else:
            triggers.append(float(row["conditional_as_margin"]) < policy.low_as_margin_threshold)
    if policy.require_component_disagreement:
        triggers.append(bool(row["binary_logreg_relevance_disagreement"]))
    if policy.require_local_logreg_disagreement:
        triggers.append(str(row["local_label"]) != str(row["logreg_label"]))
    return any(triggers)


def build_local_prediction_frame(
    *,
    benchmark_csv: str | Path,
    binary_metadata: str | Path,
    logreg_metadata: str | Path,
) -> pd.DataFrame:
    frame = pd.read_csv(benchmark_csv).copy()
    required = {"sentence_id", "sentence", "label", "assistive_label"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Benchmark file missing required columns: {missing}")

    binary_meta = _load_json(binary_metadata)
    logreg_meta = _load_json(logreg_metadata)
    binary_runtime = dict(binary_meta.get("runtime", {}))
    logreg_runtime = dict(logreg_meta.get("runtime", {}))
    shared_keys = ("embedding_backend", "model_name", "hash_dim", "batch_size")
    for key in shared_keys:
        if binary_runtime.get(key) != logreg_runtime.get(key):
            raise ValueError(f"Binary/logreg embedding configuration mismatch on {key}")

    embeddings = embed_sentences(
        frame["sentence"].fillna("").astype(str).tolist(),
        backend=str(binary_runtime.get("embedding_backend", "sentence_transformers")),
        model_name=str(binary_runtime.get("model_name", "sentence-transformers/all-mpnet-base-v2")),
        batch_size=int(binary_runtime.get("batch_size", 32)),
        hash_dim=int(binary_runtime.get("hash_dim", 64)),
    )

    rel_model = _load_pickle(binary_runtime["relevance_model_pickle"])["model"]
    rel_classes = [str(value) for value in rel_model.classes_.tolist()]
    rel_probs = rel_model.predict_proba(embeddings)
    rel_index = {label: idx for idx, label in enumerate(rel_classes)}

    logreg_model = _load_pickle(logreg_runtime["model_pickle"])["model"]
    logreg_classes = [str(value) for value in logreg_model.classes_.tolist()]
    logreg_probs = logreg_model.predict_proba(embeddings)
    logreg_index = {label: idx for idx, label in enumerate(logreg_classes)}

    local_rows: list[dict[str, Any]] = []
    for record, rel_row, logreg_row in zip(
        frame.to_dict(orient="records"), rel_probs, logreg_probs, strict=True
    ):
        p_irrelevant = float(rel_row[rel_index["Irrelevant"]])
        p_non_irrelevant = float(rel_row[rel_index["Non-Irrelevant"]])
        p_logreg_actionable = float(logreg_row[logreg_index["Actionable"]])
        p_logreg_speculative = float(logreg_row[logreg_index["Speculative"]])
        p_logreg_irrelevant = float(logreg_row[logreg_index["Irrelevant"]])
        cond_a, cond_s, as_mass = _conditional_as_probs(
            pd.Series(
                {
                    "logreg_prob_actionable": p_logreg_actionable,
                    "logreg_prob_speculative": p_logreg_speculative,
                }
            )
        )
        p_actionable = p_non_irrelevant * cond_a
        p_speculative = p_non_irrelevant * cond_s
        local_scores = {
            "Actionable": p_actionable,
            "Speculative": p_speculative,
            "Irrelevant": p_irrelevant,
        }
        local_label = max(local_scores.items(), key=lambda item: item[1])[0]
        local_confidence = max(local_scores.values())
        binary_label = _binary_top_label(p_irrelevant, p_non_irrelevant)
        logreg_scores = {
            "Actionable": p_logreg_actionable,
            "Speculative": p_logreg_speculative,
            "Irrelevant": p_logreg_irrelevant,
        }
        logreg_label = max(logreg_scores.items(), key=lambda item: item[1])[0]
        local_rows.append(
            {
                **record,
                "binary_prob_irrelevant": p_irrelevant,
                "binary_prob_non_irrelevant": p_non_irrelevant,
                "binary_label": binary_label,
                "logreg_prob_actionable": p_logreg_actionable,
                "logreg_prob_speculative": p_logreg_speculative,
                "logreg_prob_irrelevant": p_logreg_irrelevant,
                "logreg_label": logreg_label,
                "local_prob_actionable": p_actionable,
                "local_prob_speculative": p_speculative,
                "local_prob_irrelevant": p_irrelevant,
                "local_label": local_label,
                "local_confidence": local_confidence,
                "conditional_as_prob_actionable": cond_a,
                "conditional_as_prob_speculative": cond_s,
                "conditional_as_margin": abs(cond_a - cond_s),
                "binary_logreg_relevance_disagreement": (
                    (binary_label == "Irrelevant") != (logreg_label == "Irrelevant")
                ),
            }
        )
    result = pd.DataFrame(local_rows)
    result["api_a_label"] = result["assistive_label"].fillna("").astype(str)
    if "api_b_label" not in result.columns:
        result["api_b_label"] = ""
    return result


def _policy_specs() -> list[PolicySpec]:
    return [
        PolicySpec(name="local_only", description="No deferral."),
        PolicySpec(
            name="api_a_low_conf_060",
            description="Defer rows with local top-score confidence below 0.60.",
            low_confidence_threshold=0.60,
        ),
        PolicySpec(
            name="api_a_low_as_margin_015",
            description="Defer non-irrelevant rows with conditional A/S margin below 0.15.",
            low_as_margin_threshold=0.15,
        ),
        PolicySpec(
            name="api_a_component_disagreement",
            description="Defer rows where binary relevance and logreg disagree on irrelevance.",
            require_component_disagreement=True,
        ),
        PolicySpec(
            name="api_a_conf_or_margin",
            description="Defer rows with low confidence or narrow A/S margin.",
            low_confidence_threshold=0.60,
            low_as_margin_threshold=0.15,
        ),
        PolicySpec(
            name="api_a_conf_or_margin_or_disagreement",
            description="Defer rows with low confidence, narrow A/S margin, or local component disagreement.",
            low_confidence_threshold=0.60,
            low_as_margin_threshold=0.15,
            require_component_disagreement=True,
        ),
        PolicySpec(
            name="oracle_error_only",
            description="Upper-bound diagnostic: defer only rows the local model gets wrong.",
            oracle_error_only=True,
            deployable=False,
        ),
    ]


def simulate_policies(
    prediction_frame: pd.DataFrame,
    *,
    api_b_available: bool = False,
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    rows = prediction_frame.copy()
    summaries: list[dict[str, Any]] = []
    for policy in _policy_specs():
        deferred_mask = rows.apply(lambda row: _should_defer(row, policy), axis=1)
        final_labels: list[str] = []
        for row, defer in zip(rows.to_dict(orient="records"), deferred_mask.tolist(), strict=True):
            if not defer:
                final_labels.append(str(row["local_label"]))
                continue
            api_a_label = str(row.get("api_a_label", "")).strip()
            api_b_label = str(row.get("api_b_label", "")).strip() if api_b_available else ""
            if not api_a_label:
                final_labels.append(str(row["local_label"]))
                continue
            if policy.api_b_majority and api_b_label:
                final_labels.append(_majority_vote(str(row["local_label"]), api_a_label, api_b_label))
            else:
                final_labels.append(api_a_label)

        metrics = compute_metrics(rows["label"].astype(str).tolist(), final_labels)
        local_correct = rows["local_label"].astype(str).eq(rows["label"].astype(str))
        final_correct = pd.Series(final_labels, index=rows.index).astype(str).eq(
            rows["label"].astype(str)
        )
        deferred_errors_captured = int((deferred_mask & ~local_correct & final_correct).sum())
        deferred_rows = int(deferred_mask.sum())
        summary = {
            "policy_name": policy.name,
            "description": policy.description,
            "deployable": policy.deployable,
            "accuracy": metrics["accuracy"],
            "macro_f1": metrics["macro_f1"],
            "binary_relevance_accuracy": metrics["binary_relevance_accuracy"],
            "actionable_speculative_conditional_accuracy": metrics[
                "actionable_speculative_conditional_accuracy"
            ],
            "deferred_rows": deferred_rows,
            "deferred_rate": deferred_rows / len(rows) if len(rows) else 0.0,
            "deferred_errors_captured": deferred_errors_captured,
            "api_b_majority": bool(policy.api_b_majority and api_b_available),
        }
        summaries.append(summary)
        rows[f"deferred__{policy.name}"] = deferred_mask.astype(bool)
        rows[f"final_label__{policy.name}"] = final_labels

    summaries.sort(
        key=lambda item: (
            0 if bool(item["deployable"]) else 1,
            -float(item["accuracy"]),
            -float(item["macro_f1"]),
            float(item["deferred_rate"]),
            item["policy_name"],
        )
    )
    return summaries, rows


def _markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Selective-Defer Simulation",
        "",
        f"- Benchmark: `{payload['benchmark']['path']}`",
        f"- Rows: `{payload['benchmark']['rows']}`",
        f"- Local base: `{payload['local_base_model_id']}`",
        f"- API A column: `{payload['api_a_column']}`",
        f"- API B available: `{payload['api_b_available']}`",
        "",
        "| Policy | Accuracy | Macro F1 | Binary Relevance Acc | A/S Acc | Deferred Rows | Deferred Rate | Errors Captured |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["policies"]:
        lines.append(
            "| {policy} | {acc:.4f} | {macro:.4f} | {bin_acc:.4f} | {as_acc:.4f} | {deferred} | {rate:.4f} | {captured} |".format(
                policy=row["policy_name"],
                acc=row["accuracy"],
                macro=row["macro_f1"],
                bin_acc=row["binary_relevance_accuracy"],
                as_acc=row["actionable_speculative_conditional_accuracy"],
                deferred=row["deferred_rows"],
                rate=row["deferred_rate"],
                captured=row["deferred_errors_captured"],
            )
        )
    return "\n".join(lines) + "\n"


def run_simulation(args: argparse.Namespace) -> dict[str, Any]:
    frame = build_local_prediction_frame(
        benchmark_csv=args.benchmark_csv,
        binary_metadata=args.binary_metadata,
        logreg_metadata=args.logreg_metadata,
    )
    api_b_available = bool(
        args.api_b_column and args.api_b_column in frame.columns and frame[args.api_b_column].fillna("").astype(str).str.strip().ne("").any()
    )
    if args.api_b_column and args.api_b_column in frame.columns:
        frame["api_b_label"] = frame[args.api_b_column].fillna("").astype(str)

    summaries, detailed = simulate_policies(frame, api_b_available=api_b_available)

    output_json = _resolve(args.output_json)
    output_md = _resolve(args.output_md)
    output_rows = _resolve(args.output_rows)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_rows.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "benchmark": {
            "path": str(_resolve(args.benchmark_csv)),
            "rows": int(len(frame)),
        },
        "local_base_model_id": "layered_binary_relevance_logreg_as_v1",
        "api_a_column": "assistive_label",
        "api_b_available": api_b_available,
        "policies": summaries,
    }
    best_deployable = next((row for row in summaries if row["deployable"]), summaries[0])
    payload["best_deployable_policy"] = best_deployable
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    output_md.write_text(_markdown_report(payload), encoding="utf-8")
    detailed.to_csv(output_rows, index=False)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-csv", required=True)
    parser.add_argument("--binary-metadata", required=True)
    parser.add_argument("--logreg-metadata", required=True)
    parser.add_argument("--api-b-column", default="")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--output-rows", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_simulation(args)
    best = payload["best_deployable_policy"]
    print(
        "[selective-defer] best="
        f"{best['policy_name']} accuracy={best['accuracy']:.4f} deferred_rate={best['deferred_rate']:.4f}"
    )


if __name__ == "__main__":
    main()
