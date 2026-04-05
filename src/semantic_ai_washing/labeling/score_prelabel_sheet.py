"""Score one assistive prelabel sheet against reviewed benchmark labels."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from semantic_ai_washing.labcore.runtime import dump_json, now_utc_iso


def _resolve(path: str | Path) -> Path:
    return Path(path).expanduser().resolve()


def score_prelabel_sheet(*, benchmark_csv: str, assistive_csv: str) -> dict[str, Any]:
    benchmark = pd.read_csv(_resolve(benchmark_csv))
    assistive = pd.read_csv(_resolve(assistive_csv))

    benchmark["manual_label"] = benchmark["label"].fillna("").astype(str).str.strip()
    reviewed = benchmark.loc[
        benchmark["manual_label"] != "", ["sentence_id", "manual_label"]
    ].copy()
    compare = reviewed.merge(
        assistive[
            [
                "sentence_id",
                "assistive_label",
                "assistive_confidence",
                "assistive_rationale",
                "source_section",
                "sentence",
                *(
                    ["prelabel_eligible", "skip_reason"]
                    if "prelabel_eligible" in assistive.columns
                    or "skip_reason" in assistive.columns
                    else []
                ),
            ]
        ],
        on="sentence_id",
        how="left",
    )
    compare["assistive_label"] = compare["assistive_label"].fillna("").astype(str).str.strip()
    compare["agree"] = compare["manual_label"] == compare["assistive_label"]
    if "prelabel_eligible" in compare.columns:
        eligible_mask = compare["prelabel_eligible"].fillna(True)
        eligible_mask = (
            eligible_mask.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})
        )
    else:
        eligible_mask = pd.Series(True, index=compare.index, dtype=bool)
    if "skip_reason" in compare.columns:
        eligible_mask &= (
            compare["skip_reason"].fillna("").astype(str).str.strip() != "unmatched_noise"
        )
    compare["eligible_for_gate"] = eligible_mask

    action_spec = compare[compare["manual_label"].isin(["Actionable", "Speculative"])].copy()
    eligible = compare[compare["eligible_for_gate"]].copy()
    eligible_action_spec = eligible[
        eligible["manual_label"].isin(["Actionable", "Speculative"])
    ].copy()
    mismatches = compare[~compare["agree"]].copy()
    confusion = (
        pd.crosstab(compare["manual_label"], compare["assistive_label"], dropna=False)
        .sort_index()
        .sort_index(axis=1)
    )
    eligible_confusion = (
        pd.crosstab(eligible["manual_label"], eligible["assistive_label"], dropna=False)
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
                "eligible_for_gate": bool(row.get("eligible_for_gate", True)),
                "skip_reason": str(row.get("skip_reason", "") or ""),
            }
        )

    cleaned_text_checks = {
        "table_of_contents_present": bool(
            compare["sentence"]
            .fillna("")
            .astype(str)
            .str.contains("Table of Contents", case=False)
            .any()
        ),
        "form_10k_present": bool(
            compare["sentence"]
            .fillna("")
            .astype(str)
            .str.contains(r"Form\s+10-K", case=False, regex=True)
            .any()
        ),
        "heading_prefix_present": bool(
            compare["sentence"]
            .fillna("")
            .astype(str)
            .str.contains(
                r"^(?:Our Products and Suppliers|Business Overview|Executive Summary|Data, Analytics and Artificial Intelligence)\b",
                case=False,
                regex=True,
            )
            .any()
        ),
        "glossary_fragment_present": bool(
            compare["sentence"]
            .fillna("")
            .astype(str)
            .str.contains(
                r"AI/ML\s*-\s*Artificial Intelligence/Machine Learning",
                case=False,
                regex=True,
            )
            .any()
        ),
    }

    return {
        "generated_at": now_utc_iso(),
        "benchmark_csv": str(_resolve(benchmark_csv)),
        "assistive_csv": str(_resolve(assistive_csv)),
        "score": {
            "gate_basis": "eligible",
            "overall": {"matches": int(eligible["agree"].sum()), "total": int(len(eligible))},
            "action_spec": {
                "matches": int(eligible_action_spec["agree"].sum()),
                "total": int(len(eligible_action_spec)),
            },
            "raw_overall": {"matches": int(compare["agree"].sum()), "total": int(len(compare))},
            "raw_action_spec": {
                "matches": int(action_spec["agree"].sum()),
                "total": int(len(action_spec)),
            },
            "eligible_overall": {
                "matches": int(eligible["agree"].sum()),
                "total": int(len(eligible)),
            },
            "eligible_action_spec": {
                "matches": int(eligible_action_spec["agree"].sum()),
                "total": int(len(eligible_action_spec)),
            },
            "excluded_from_gate": {
                "count": int((~compare["eligible_for_gate"]).sum()),
                "sentence_ids": compare.loc[~compare["eligible_for_gate"], "sentence_id"]
                .astype(str)
                .tolist(),
            },
            "manual_distribution": compare["manual_label"].value_counts().to_dict(),
            "assistive_distribution": compare["assistive_label"].value_counts().to_dict(),
            "confusion": confusion.to_dict(),
            "eligible_confusion": eligible_confusion.to_dict(),
            "mismatch_rows": mismatch_rows,
        },
        "cleaned_text_checks": cleaned_text_checks,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    overall = payload["score"]["overall"]
    action_spec = payload["score"]["action_spec"]
    raw_overall = payload["score"]["raw_overall"]
    raw_action_spec = payload["score"]["raw_action_spec"]
    checks = payload["cleaned_text_checks"]
    lines = [
        "# Tranche 1 Clean Slice v2.4 Check",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Benchmark labels: `{payload['benchmark_csv']}`",
        f"- Assistive labels: `{payload['assistive_csv']}`",
        f"- Gate basis: `{payload['score']['gate_basis']}`",
        f"- Eligible overall agreement: `{overall['matches']}/{overall['total']}`",
        f"- Eligible `Actionable/Speculative` agreement: `{action_spec['matches']}/{action_spec['total']}`",
        f"- Raw overall agreement: `{raw_overall['matches']}/{raw_overall['total']}`",
        f"- Raw `Actionable/Speculative` agreement: `{raw_action_spec['matches']}/{raw_action_spec['total']}`",
        f"- Excluded-from-gate rows: `{payload['score']['excluded_from_gate']['count']}`",
        "",
        "## Cleanliness Checks",
        "",
        f"- `Table of Contents` present: `{checks['table_of_contents_present']}`",
        f"- `Form 10-K` header present: `{checks['form_10k_present']}`",
        f"- Heading-prefix contamination present: `{checks['heading_prefix_present']}`",
        f"- Glossary fragment present: `{checks['glossary_fragment_present']}`",
        "",
        "## Mismatches",
        "",
    ]
    if payload["score"]["mismatch_rows"]:
        for row in payload["score"]["mismatch_rows"]:
            lines.append(
                f"- `{row['sentence_id']}` manual=`{row['manual_label']}` assistive=`{row['assistive_label']}` section=`{row['source_section']}`"
            )
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-csv", required=True)
    parser.add_argument("--assistive-csv", required=True)
    parser.add_argument("--report-json", required=True)
    parser.add_argument("--report-md", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = score_prelabel_sheet(
        benchmark_csv=args.benchmark_csv,
        assistive_csv=args.assistive_csv,
    )
    dump_json(_resolve(args.report_json), payload)
    _resolve(args.report_md).write_text(render_markdown(payload), encoding="utf-8")
    print(
        "[score-prelabel-sheet] "
        f"eligible_overall={payload['score']['overall']['matches']}/{payload['score']['overall']['total']} "
        f"eligible_action_spec={payload['score']['action_spec']['matches']}/{payload['score']['action_spec']['total']} "
        f"raw_overall={payload['score']['raw_overall']['matches']}/{payload['score']['raw_overall']['total']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
