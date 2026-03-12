"""Benchmark prompt variants on a fixed tranche calibration slice."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from semantic_ai_washing.director.core.utils import dump_json, now_utc_iso
from semantic_ai_washing.labeling.assistive_prelabel_batch import (
    ASSISTIVE_COLUMNS,
    generate_assistive_prelabels,
)
from semantic_ai_washing.labeling.initialize_review_sheet import initialize_review_sheet

DEFAULT_INPUT = "data/labels/v1/labeling_batch_v1_reextracted_v2_2_slice40.csv"
DEFAULT_BENCHMARK = "data/labels/v1/labeling_batch_v1_filled_v2_1_slice40.csv"
DEFAULT_POLICY = "director/config/api_assistive_policy.yaml"
DEFAULT_VARIANTS = "director/config/prompt_variants/tranche1_v2_4.yaml"
DEFAULT_COST_POLICY = "director/config/cost_policy.yaml"
DEFAULT_REPORT_JSON = "reports/labels/tranche1_prompt_benchmark_v2_4.json"
DEFAULT_REPORT_MD = "reports/labels/tranche1_prompt_benchmark_v2_4.md"
DEFAULT_FULL_INPUT = "data/labels/v1/labeling_batch_v1.csv"
DEFAULT_FULL_OUTPUT = "data/labels/v1/labeling_batch_v1_prelabeled_v2_4.csv"
DEFAULT_FULL_FILLED = "data/labels/v1/labeling_batch_v1_filled_v2_4.csv"
DEFAULT_FULL_REPORT = "reports/labels/assistive_prelabel_tranche1_v2_4_summary.json"
DEFAULT_VERSION = "v2_4"
REQUIRED_GATE_OVERALL = (35, 40)
REQUIRED_GATE_ACTION_SPEC = (10, 12)


def _resolve(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def _load_yaml(path: str | Path) -> dict[str, Any]:
    payload = yaml.safe_load(_resolve(path).read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {path}")
    return payload


def _sanitize_input(input_csv: str | Path, output_csv: str | Path) -> Path:
    frame = pd.read_csv(_resolve(input_csv))
    for column in ASSISTIVE_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
        frame[column] = ""
    frame.to_csv(output_csv, index=False)
    return Path(output_csv)


def _variant_paths(variant_id: str) -> tuple[Path, Path]:
    output_csv = _resolve(f"data/labels/v1/labeling_batch_v1_prelabeled_{variant_id}_slice40.csv")
    report_json = _resolve(
        f"reports/labels/assistive_prelabel_tranche1_{variant_id}_slice40_summary.json"
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    return output_csv, report_json


def _write_variant_policy(
    *,
    base_policy_path: str | Path,
    system_prompt: str,
    user_prompt_template: str,
    temp_dir: str | Path,
    variant_id: str,
) -> Path:
    payload = _load_yaml(base_policy_path)
    payload.setdefault("prompt_spec", {})
    payload["prompt_spec"]["system_prompt"] = system_prompt
    payload["prompt_spec"]["user_prompt_template"] = user_prompt_template
    out = Path(temp_dir) / f"{variant_id}_policy.yaml"
    out.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    return out


def _load_variants(path: str | Path) -> list[dict[str, Any]]:
    payload = _load_yaml(path)
    variants = payload.get("variants", [])
    if not isinstance(variants, list) or not variants:
        raise ValueError(f"No prompt variants found in {path}")
    return variants


def _score_variant(
    *,
    benchmark_csv: str | Path,
    variant_csv: str | Path,
) -> dict[str, Any]:
    benchmark = pd.read_csv(_resolve(benchmark_csv))
    variant = pd.read_csv(_resolve(variant_csv))

    benchmark["manual_label"] = benchmark["label"].fillna("").astype(str).str.strip()
    reviewed = benchmark.loc[
        benchmark["manual_label"] != "", ["sentence_id", "manual_label"]
    ].copy()
    if "sentence_id" not in reviewed.columns or "sentence_id" not in variant.columns:
        raise ValueError("Both benchmark and variant outputs must contain sentence_id")

    compare = reviewed.merge(
        variant[
            [
                "sentence_id",
                "assistive_label",
                "assistive_confidence",
                "assistive_rationale",
                "source_section",
                "sentence",
            ]
        ],
        on="sentence_id",
        how="left",
    )
    compare["assistive_label"] = compare["assistive_label"].fillna("").astype(str).str.strip()
    compare["agree"] = compare["manual_label"] == compare["assistive_label"]

    action_spec = compare[compare["manual_label"].isin(["Actionable", "Speculative"])].copy()
    mismatches = compare[~compare["agree"]].copy()

    confusion = (
        pd.crosstab(compare["manual_label"], compare["assistive_label"], dropna=False)
        .sort_index()
        .sort_index(axis=1)
    )
    mismatch_rows = []
    for _, row in mismatches.iterrows():
        mismatch_rows.append(
            {
                "sentence_id": str(row["sentence_id"]),
                "manual_label": str(row["manual_label"]),
                "assistive_label": str(row["assistive_label"]),
                "source_section": str(row.get("source_section", "") or ""),
                "assistive_confidence": str(row.get("assistive_confidence", "") or ""),
                "assistive_rationale": str(row.get("assistive_rationale", "") or ""),
                "sentence": str(row.get("sentence", "") or ""),
            }
        )

    actionable_to_speculative_misses = sum(
        1
        for row in mismatch_rows
        if row["manual_label"] == "Actionable" and row["assistive_label"] == "Speculative"
    )
    actionable_to_irrelevant_misses = sum(
        1
        for row in mismatch_rows
        if row["manual_label"] == "Actionable" and row["assistive_label"] == "Irrelevant"
    )

    return {
        "overall": {
            "matches": int(compare["agree"].sum()),
            "total": int(len(compare)),
        },
        "action_spec": {
            "matches": int(action_spec["agree"].sum()),
            "total": int(len(action_spec)),
        },
        "manual_distribution": compare["manual_label"].value_counts().to_dict(),
        "assistive_distribution": compare["assistive_label"].value_counts().to_dict(),
        "confusion": confusion.to_dict(),
        "mismatch_rows": mismatch_rows,
        "actionable_to_speculative_misses": int(actionable_to_speculative_misses),
        "actionable_to_irrelevant_misses": int(actionable_to_irrelevant_misses),
    }


def _is_eligible(score: dict[str, Any]) -> bool:
    return score["overall"]["matches"] >= REQUIRED_GATE_OVERALL[0]


def _passes_gate(score: dict[str, Any]) -> bool:
    return _is_eligible(score) and score["action_spec"]["matches"] >= REQUIRED_GATE_ACTION_SPEC[0]


def _winner_sort_key(record: dict[str, Any]) -> tuple[int, int, int, int]:
    score = record["score"]
    return (
        int(score["action_spec"]["matches"]),
        -int(score["actionable_to_speculative_misses"]),
        -int(score["actionable_to_irrelevant_misses"]),
        int(score["overall"]["matches"]),
    )


def _render_report_markdown(payload: dict[str, Any]) -> str:
    lines = ["# Tranche 1 Prompt Benchmark v2.4", ""]
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Generated at: `{payload['generated_at']}`")
    lines.append(f"- Input slice: `{payload['input_csv']}`")
    lines.append(f"- Benchmark labels: `{payload['benchmark_csv']}`")
    lines.append(
        f"- Acceptance gate: overall `>= {REQUIRED_GATE_OVERALL[0]}/{REQUIRED_GATE_OVERALL[1]}`, "
        f"`Actionable/Speculative >= {REQUIRED_GATE_ACTION_SPEC[0]}/{REQUIRED_GATE_ACTION_SPEC[1]}`"
    )
    winner = payload.get("winner")
    if winner:
        lines.append(f"- Winner: `{winner['variant_id']}`")
        lines.append(f"- Winner gate passed: `{winner['gate_passed']}`")
    else:
        lines.append("- Winner: `none`")
        lines.append("- Winner gate passed: `false`")
    lines.append("")
    lines.append("## Variant Scores")
    lines.append("")
    for record in payload["variants"]:
        score = record["score"]
        lines.append(f"### `{record['variant_id']}` — {record['label']}")
        lines.append(
            f"- Overall agreement: `{score['overall']['matches']}/{score['overall']['total']}`"
        )
        lines.append(
            f"- `Actionable/Speculative` agreement: `{score['action_spec']['matches']}/{score['action_spec']['total']}`"
        )
        lines.append(
            f"- `Actionable -> Speculative` misses: `{score['actionable_to_speculative_misses']}`"
        )
        lines.append(
            f"- `Actionable -> Irrelevant` misses: `{score['actionable_to_irrelevant_misses']}`"
        )
        lines.append(f"- Eligible: `{record['eligible']}`")
        lines.append(f"- Gate passed: `{record['gate_passed']}`")
        lines.append("")
    lines.append("## Decision")
    lines.append("")
    if winner and winner["gate_passed"]:
        lines.append(f"- Proceed to full tranche regeneration under `{winner['variant_id']}`.")
    else:
        lines.append("- No prompt variant passed the gate.")
        lines.append("- Do not regenerate the full `240` tranche.")
        lines.append("- Next patch should be extraction-only on the noisiest `5–10` rows.")
    lines.append("")
    return "\n".join(lines) + "\n"


def benchmark_prompt_variants(
    *,
    input_csv: str = DEFAULT_INPUT,
    benchmark_csv: str = DEFAULT_BENCHMARK,
    base_policy_path: str = DEFAULT_POLICY,
    variants_path: str = DEFAULT_VARIANTS,
    cost_policy_path: str = DEFAULT_COST_POLICY,
    report_json: str = DEFAULT_REPORT_JSON,
    report_md: str = DEFAULT_REPORT_MD,
    full_input_csv: str = DEFAULT_FULL_INPUT,
    full_output_csv: str = DEFAULT_FULL_OUTPUT,
    full_filled_csv: str = DEFAULT_FULL_FILLED,
    full_report_json: str = DEFAULT_FULL_REPORT,
    regenerate_full_on_success: bool = True,
) -> dict[str, Any]:
    variants = _load_variants(variants_path)
    variant_lookup = {str(variant["variant_id"]): variant for variant in variants}
    report_payload: dict[str, Any] = {
        "generated_at": now_utc_iso(),
        "input_csv": str(_resolve(input_csv)),
        "benchmark_csv": str(_resolve(benchmark_csv)),
        "base_policy_path": str(_resolve(base_policy_path)),
        "variants_path": str(_resolve(variants_path)),
        "variants": [],
        "winner": None,
        "full_tranche": {"attempted": False, "generated": False, "variant_id": ""},
    }

    with tempfile.TemporaryDirectory(prefix="prompt-benchmark-") as temp_dir:
        for variant in variants:
            variant_id = str(variant["variant_id"])
            output_csv, summary_json = _variant_paths(variant_id)
            if output_csv.exists():
                output_csv.unlink()
            if summary_json.exists():
                summary_json.unlink()

            sanitized_input = Path(temp_dir) / f"{variant_id}_input.csv"
            _sanitize_input(input_csv, sanitized_input)
            variant_policy = _write_variant_policy(
                base_policy_path=base_policy_path,
                system_prompt=str(variant["system_prompt"]),
                user_prompt_template=str(variant["user_prompt_template"]),
                temp_dir=temp_dir,
                variant_id=variant_id,
            )
            summary, exit_code = generate_assistive_prelabels(
                input_csv=str(sanitized_input),
                output_csv=str(output_csv),
                report_path=str(summary_json),
                policy_path=str(variant_policy),
                cost_policy_path=cost_policy_path,
                mode="live",
                checkpoint_every=10,
            )
            score = _score_variant(benchmark_csv=benchmark_csv, variant_csv=output_csv)
            report_payload["variants"].append(
                {
                    "variant_id": variant_id,
                    "label": str(variant.get("label", "")),
                    "description": str(variant.get("description", "")),
                    "policy_path": str(variant_policy),
                    "output_csv": str(output_csv),
                    "summary_json": str(summary_json),
                    "exit_code": int(exit_code),
                    "summary_status": summary.get("status", ""),
                    "usage": summary.get("usage", {}),
                    "score": score,
                    "eligible": _is_eligible(score),
                    "gate_passed": _passes_gate(score),
                }
            )

    eligible = [record for record in report_payload["variants"] if record["eligible"]]
    if eligible:
        winner = sorted(eligible, key=_winner_sort_key, reverse=True)[0]
        report_payload["winner"] = {
            "variant_id": winner["variant_id"],
            "label": winner["label"],
            "gate_passed": winner["gate_passed"],
            "score": winner["score"],
        }
    else:
        report_payload["winner"] = None

    if (
        regenerate_full_on_success
        and report_payload["winner"]
        and report_payload["winner"]["gate_passed"]
    ):
        winner_id = str(report_payload["winner"]["variant_id"])
        winner_variant = variant_lookup[winner_id]
        with tempfile.TemporaryDirectory(prefix="prompt-benchmark-full-") as temp_dir:
            sanitized_input = Path(temp_dir) / f"{winner_id}_full_input.csv"
            _sanitize_input(full_input_csv, sanitized_input)
            full_policy = _write_variant_policy(
                base_policy_path=base_policy_path,
                system_prompt=str(winner_variant["system_prompt"]),
                user_prompt_template=str(winner_variant["user_prompt_template"]),
                temp_dir=temp_dir,
                variant_id=f"{winner_id}_full",
            )
            summary, exit_code = generate_assistive_prelabels(
                input_csv=str(sanitized_input),
                output_csv=full_output_csv,
                report_path=full_report_json,
                policy_path=str(full_policy),
                cost_policy_path=cost_policy_path,
                mode="live",
                checkpoint_every=10,
            )
        initialize_review_sheet(
            input_csv=full_output_csv,
            output_csv=full_filled_csv,
        )
        report_payload["full_tranche"] = {
            "attempted": True,
            "generated": int(exit_code) == 0 and summary.get("status") == "passed",
            "variant_id": winner_id,
            "output_csv": str(_resolve(full_output_csv)),
            "filled_csv": str(_resolve(full_filled_csv)),
            "summary_json": str(_resolve(full_report_json)),
        }

    report_json_path = _resolve(report_json)
    report_json_path.parent.mkdir(parents=True, exist_ok=True)
    dump_json(report_json_path, report_payload)

    report_md_path = _resolve(report_md)
    report_md_path.parent.mkdir(parents=True, exist_ok=True)
    report_md_path.write_text(_render_report_markdown(report_payload), encoding="utf-8")
    return report_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", default=DEFAULT_INPUT)
    parser.add_argument("--benchmark-csv", default=DEFAULT_BENCHMARK)
    parser.add_argument("--base-policy", default=DEFAULT_POLICY)
    parser.add_argument("--variants", default=DEFAULT_VARIANTS)
    parser.add_argument("--cost-policy", default=DEFAULT_COST_POLICY)
    parser.add_argument("--report-json", default=DEFAULT_REPORT_JSON)
    parser.add_argument("--report-md", default=DEFAULT_REPORT_MD)
    parser.add_argument("--full-input-csv", default=DEFAULT_FULL_INPUT)
    parser.add_argument("--full-output-csv", default=DEFAULT_FULL_OUTPUT)
    parser.add_argument("--full-filled-csv", default=DEFAULT_FULL_FILLED)
    parser.add_argument("--full-report-json", default=DEFAULT_FULL_REPORT)
    parser.add_argument(
        "--no-regenerate-full",
        action="store_true",
        help="Do not regenerate the full tranche even if a variant passes the gate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = benchmark_prompt_variants(
        input_csv=args.input_csv,
        benchmark_csv=args.benchmark_csv,
        base_policy_path=args.base_policy,
        variants_path=args.variants,
        cost_policy_path=args.cost_policy,
        report_json=args.report_json,
        report_md=args.report_md,
        full_input_csv=args.full_input_csv,
        full_output_csv=args.full_output_csv,
        full_filled_csv=args.full_filled_csv,
        full_report_json=args.full_report_json,
        regenerate_full_on_success=not args.no_regenerate_full,
    )
    winner = payload.get("winner")
    if winner and winner.get("gate_passed"):
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
