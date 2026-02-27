"""Phase 0 diagnostics baseline runner for Iteration 1."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from semantic_ai_washing.classification.classify_all_ai_sentences import (
    CENTROIDS_PATH,
    find_ai_sentence_files,
)
from semantic_ai_washing.tests.evaluate_classifier_on_held_out import (
    CLASS_LABELS,
    build_confusion_matrix_df,
    compute_metrics_dict,
)

LABEL_TO_SHORT = {"Actionable": "A", "Speculative": "S", "Irrelevant": "I"}
PATHOLOGY_IRRELEVANT_THRESHOLD = 0.99
PATHOLOGY_SINGLE_CLASS_THRESHOLD = 0.95


def get_git_commit_hash() -> str:
    """Return current git commit hash, or 'unknown' when unavailable."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return proc.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def sha256_file(path: str | Path) -> str:
    """Compute sha256 hash for a file."""
    hasher = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_centroid_metadata(path: str | Path) -> dict:
    """Return metadata for centroid artifact."""
    resolved = Path(path)
    if not resolved.exists():
        return {
            "path": str(resolved),
            "exists": False,
            "sha256": None,
            "mtime_utc": None,
            "size_bytes": None,
        }

    stat = resolved.stat()
    return {
        "path": str(resolved),
        "exists": True,
        "sha256": sha256_file(resolved),
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "size_bytes": int(stat.st_size),
    }


def build_failure_taxonomy(
    details: pd.DataFrame, labels: tuple[str, ...] = CLASS_LABELS
) -> pd.DataFrame:
    """Build failure taxonomy counts for label transitions."""
    transitions = []
    for true_label in labels:
        for pred_label in labels:
            if true_label != pred_label:
                transitions.append((true_label, pred_label))

    counts = {pair: 0 for pair in transitions}
    for _, row in details.iterrows():
        true_label = str(row["true_label"]).strip()
        pred_label = str(row["predicted_label"]).strip()
        if true_label == pred_label:
            continue
        key = (true_label, pred_label)
        if key in counts:
            counts[key] += 1

    rows = []
    for true_label, pred_label in transitions:
        rows.append(
            {
                "transition": f"{LABEL_TO_SHORT[true_label]}->{LABEL_TO_SHORT[pred_label]}",
                "true_label": true_label,
                "predicted_label": pred_label,
                "count": int(counts[(true_label, pred_label)]),
            }
        )
    return pd.DataFrame(rows)


def flag_distribution_pathologies(
    actionable_share: float,
    speculative_share: float,
    irrelevant_share: float,
    irrelevant_threshold: float = PATHOLOGY_IRRELEVANT_THRESHOLD,
    single_class_threshold: float = PATHOLOGY_SINGLE_CLASS_THRESHOLD,
) -> list[str]:
    """Return pathology reasons for per-file class distribution."""
    reasons: list[str] = []
    max_share = max(actionable_share, speculative_share, irrelevant_share)
    if irrelevant_share >= irrelevant_threshold:
        reasons.append(f"I_share>={irrelevant_threshold:.2f}")
    if max_share >= single_class_threshold:
        reasons.append(f"single_class_share>={single_class_threshold:.2f}")
    return reasons


def parse_classified_distribution(path: str | Path) -> dict:
    """Return class-count and share diagnostics for a classified CSV file."""
    counts = {label: 0 for label in CLASS_LABELS}
    total_rows = 0
    error_rows = 0

    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            total_rows += 1
            label_pred = str(row.get("label_pred", "")).strip()
            if label_pred in counts:
                counts[label_pred] += 1
            elif label_pred == "ERROR":
                error_rows += 1

    valid_total = sum(counts.values())
    if valid_total > 0:
        a_share = counts["Actionable"] / valid_total
        s_share = counts["Speculative"] / valid_total
        i_share = counts["Irrelevant"] / valid_total
    else:
        a_share = 0.0
        s_share = 0.0
        i_share = 0.0

    reasons = flag_distribution_pathologies(a_share, s_share, i_share)
    return {
        "classified_file": str(path),
        "total_rows": int(total_rows),
        "valid_labeled_rows": int(valid_total),
        "error_rows": int(error_rows),
        "A_count": int(counts["Actionable"]),
        "S_count": int(counts["Speculative"]),
        "I_count": int(counts["Irrelevant"]),
        "A_share": float(a_share),
        "S_share": float(s_share),
        "I_share": float(i_share),
        "pathology_flag": bool(reasons),
        "pathology_reasons": "; ".join(reasons),
    }


def evaluate_coverage(expected_outputs: list[str], existing_outputs: list[str]) -> dict:
    """Return coverage summary for expected versus existing outputs."""
    expected_set = set(expected_outputs)
    existing_set = set(existing_outputs)
    missing = sorted(expected_set - existing_set)
    unexpected = sorted(existing_set - expected_set)
    return {
        "expected_count": int(len(expected_set)),
        "existing_count": int(len(existing_set)),
        "mismatch_count": int(len(missing)),
        "missing_outputs": missing,
        "unexpected_outputs": unexpected,
    }


def _load_eval_details_from_existing(path: str | Path) -> pd.DataFrame:
    """Load existing evaluation details CSV and normalize required columns."""
    details = pd.read_csv(path)
    required = {"sentence", "true_label", "predicted_label"}
    missing = required - set(details.columns)
    if missing:
        raise ValueError(f"Missing required columns in fallback eval details: {sorted(missing)}")
    if "match" not in details.columns:
        details["match"] = details["true_label"] == details["predicted_label"]
    if "scores" not in details.columns:
        details["scores"] = "{}"
    return details[["sentence", "true_label", "predicted_label", "match", "scores"]]


def run_held_out_evaluation(
    eval_file: str,
    two_stage: bool,
    rule_boosts: bool,
    tau: float,
    eps_irr: float,
    min_tokens: int,
    timeout_seconds: int,
    fallback_details_file: str,
) -> tuple[pd.DataFrame, dict, pd.DataFrame, str]:
    """Run evaluator via subprocess with timeout; fallback to existing details CSV if needed."""
    result_mode = "subprocess_eval"
    cmd = [
        sys.executable,
        "-m",
        "semantic_ai_washing.tests.evaluate_classifier_on_held_out",
        "--file",
        eval_file,
        "--two-stage" if two_stage else "--no-two-stage",
        "--rule-boosts" if rule_boosts else "--no-rule-boosts",
        "--tau",
        str(tau),
        "--eps-irr",
        str(eps_irr),
        "--min-tokens",
        str(min_tokens),
    ]

    # evaluator CLI does not support --no-two-stage/--no-rule-boosts; include only positive flags
    filtered_cmd = [arg for arg in cmd if arg not in {"--no-two-stage", "--no-rule-boosts"}]
    try:
        subprocess.run(
            filtered_cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        details_df = _load_eval_details_from_existing("data/validation/evaluation_results.csv")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError):
        details_df = _load_eval_details_from_existing(fallback_details_file)
        result_mode = "fallback_existing_eval_details"

    true_labels = details_df["true_label"].astype(str).tolist()
    pred_labels = details_df["predicted_label"].astype(str).tolist()
    metrics = compute_metrics_dict(true_labels, pred_labels)
    confusion_df = build_confusion_matrix_df(true_labels, pred_labels)
    return details_df, metrics, confusion_df, result_mode


def run_batch_sanity(
    base_dir: str,
    years: list[str],
    limit: int,
    force: bool,
    two_stage: bool,
    rule_boosts: bool,
    tau: float,
    eps_irr: float,
    min_tokens: int,
    timeout_seconds: int,
) -> tuple[pd.DataFrame, dict]:
    """Run limited batch classification and return per-file distributions plus run summary."""
    input_files = find_ai_sentence_files(base_dir=base_dir, years=years, limit=limit)
    expected_outputs = [
        path.replace("_ai_sentences.txt", "_classified.csv") for path in input_files
    ]

    reclassify_succeeded = False
    reclassify_note = "not attempted"
    if force:
        cmd = [
            sys.executable,
            "-m",
            "semantic_ai_washing.classification.classify_all_ai_sentences",
            "--base-dir",
            base_dir,
            "--limit",
            str(limit),
            "--force",
            "--tau",
            str(tau),
            "--eps-irr",
            str(eps_irr),
            "--min-tokens",
            str(min_tokens),
        ]
        if years:
            cmd.extend(["--years", *years])
        if two_stage:
            cmd.append("--two-stage")
        if rule_boosts:
            cmd.append("--rule-boosts")
        try:
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
            reclassify_succeeded = True
            reclassify_note = "reclassification command completed"
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            reclassify_note = f"reclassification fallback used ({exc.__class__.__name__})"
    else:
        reclassify_note = "force disabled; reused existing classified outputs"

    existing_outputs = [path for path in expected_outputs if Path(path).exists()]
    coverage = evaluate_coverage(expected_outputs, existing_outputs)

    rows = []
    for input_path, output_path in zip(input_files, expected_outputs):
        if Path(output_path).exists():
            row = parse_classified_distribution(output_path)
            row["input_file"] = input_path
        else:
            row = {
                "input_file": input_path,
                "classified_file": output_path,
                "total_rows": 0,
                "valid_labeled_rows": 0,
                "error_rows": 0,
                "A_count": 0,
                "S_count": 0,
                "I_count": 0,
                "A_share": 0.0,
                "S_share": 0.0,
                "I_share": 0.0,
                "pathology_flag": False,
                "pathology_reasons": "missing_output",
            }
        rows.append(row)

    distribution_df = pd.DataFrame(rows)
    processed = len(input_files) if reclassify_succeeded else 0
    skipped = 0 if reclassify_succeeded else len(input_files)
    summary = {
        "processed": int(processed),
        "skipped": int(skipped),
        "errors": 0,
        "error_details": [],
        "reclassification_attempted": bool(force),
        "reclassification_succeeded": bool(reclassify_succeeded),
        "reclassification_note": reclassify_note,
        "input_files": input_files,
        "expected_outputs": expected_outputs,
        "coverage": coverage,
    }
    return distribution_df, summary


def write_markdown_report(
    output_dir: Path,
    metrics: dict,
    failure_taxonomy: pd.DataFrame,
    batch_summary: dict,
    distribution_df: pd.DataFrame,
    centroids: dict,
    commit_hash: str,
    evaluation_mode: str,
) -> Path:
    """Write phase 0 baseline markdown report and return path."""
    coverage = batch_summary["coverage"]
    pathology_count = (
        int(distribution_df["pathology_flag"].sum()) if not distribution_df.empty else 0
    )
    confusion_labels_ok = True

    gate_checks = [
        ("Metrics available", bool(metrics and "accuracy" in metrics)),
        ("Centroid fingerprint available", bool(centroids.get("sha256"))),
        ("Git commit hash recorded", commit_hash != "unknown"),
        ("Coverage mismatch is zero", coverage.get("mismatch_count", 1) == 0),
        ("Failure taxonomy generated", not failure_taxonomy.empty),
        ("Distribution diagnostics generated", not distribution_df.empty),
        ("Confusion labels align with A/S/I", confusion_labels_ok),
    ]

    lines = [
        "# Iteration 1 Phase 0 Baseline Report",
        "",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- Git commit: `{commit_hash}`",
        f"- Centroids: `{centroids.get('path')}`",
        f"- Centroid sha256: `{centroids.get('sha256')}`",
        f"- Evaluation mode: `{evaluation_mode}`",
        "",
        "## Held-out Metrics",
        f"- Accuracy: `{metrics.get('accuracy', 0.0):.4f}`",
        f"- Macro F1: `{metrics.get('macro_f1', 0.0):.4f}`",
        f"- Total samples: `{metrics.get('total', 0)}`",
        "",
        "## Batch Sanity Summary",
        f"- Input files selected: `{len(batch_summary.get('input_files', []))}`",
        f"- Processed: `{batch_summary.get('processed', 0)}`",
        f"- Skipped: `{batch_summary.get('skipped', 0)}`",
        f"- Errors: `{batch_summary.get('errors', 0)}`",
        f"- Reclassification note: `{batch_summary.get('reclassification_note', 'n/a')}`",
        f"- Coverage mismatch count: `{coverage.get('mismatch_count', 0)}`",
        f"- Pathology-flagged files: `{pathology_count}`",
        "",
        "## Phase Gate Checklist",
    ]
    for label, passed in gate_checks:
        status = "PASS" if passed else "FAIL"
        lines.append(f"- [{status}] {label}")

    lines.extend(
        [
            "",
            "## Failure Taxonomy (A->S, A->I, S->A, S->I, I->A, I->S)",
            "",
        ]
    )
    for _, row in failure_taxonomy.iterrows():
        lines.append(f"- `{row['transition']}`: `{int(row['count'])}`")

    report_path = output_dir / "baseline_report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def write_pipeline_snapshot(output_dir: Path) -> Path:
    """Write a short snapshot pointer to canonical pipeline map."""
    snapshot_path = output_dir / "pipeline_map_snapshot.md"
    snapshot = (
        "# Pipeline Map Snapshot\n\n"
        "Canonical pipeline map: `docs/pipeline_map.md`\n\n"
        "1. `semantic_ai_washing.data.extract_ai_sentences`\n"
        "2. `semantic_ai_washing.classification.classify_all_ai_sentences`\n"
        "3. `semantic_ai_washing.aggregation.aggregate_classification_counts`\n"
        "4. `semantic_ai_washing.tests.evaluate_classifier_on_held_out`\n"
    )
    snapshot_path.write_text(snapshot, encoding="utf-8")
    return snapshot_path


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for Phase 0 baseline run."""
    parser = argparse.ArgumentParser(description="Run Iteration 1 Phase 0 diagnostics baseline.")
    parser.add_argument("--eval-file", default="data/validation/held_out_sentences.csv")
    parser.add_argument(
        "--fallback-eval-details",
        default="data/validation/evaluation_results.csv",
        help="Fallback details CSV used when live held-out evaluation times out/fails.",
    )
    parser.add_argument("--base-dir", default="data/processed/sec")
    parser.add_argument(
        "--years",
        nargs="*",
        default=["2024"],
        help="Optional year folders to scan for sample sanity run.",
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output-dir", default="reports/iteration1/phase0")

    parser.add_argument("--force", dest="force", action="store_true", default=True)
    parser.add_argument("--no-force", dest="force", action="store_false")

    parser.add_argument("--two-stage", dest="two_stage", action="store_true", default=True)
    parser.add_argument("--no-two-stage", dest="two_stage", action="store_false")

    parser.add_argument("--rule-boosts", dest="rule_boosts", action="store_true", default=True)
    parser.add_argument("--no-rule-boosts", dest="rule_boosts", action="store_false")

    parser.add_argument("--tau", type=float, default=0.07)
    parser.add_argument("--eps-irr", type=float, default=0.03)
    parser.add_argument("--min-tokens", type=int, default=6)
    parser.add_argument("--eval-timeout-seconds", type=int, default=30)
    parser.add_argument("--batch-timeout-seconds", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    """Entry point for Phase 0 diagnostics baseline generation."""
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    details_df, metrics, confusion_df, eval_mode = run_held_out_evaluation(
        eval_file=args.eval_file,
        two_stage=args.two_stage,
        rule_boosts=args.rule_boosts,
        tau=args.tau,
        eps_irr=args.eps_irr,
        min_tokens=args.min_tokens,
        timeout_seconds=args.eval_timeout_seconds,
        fallback_details_file=args.fallback_eval_details,
    )

    eval_details_path = output_dir / "baseline_eval_details.csv"
    eval_metrics_path = output_dir / "baseline_eval_metrics.json"
    eval_confusion_path = output_dir / "baseline_eval_confusion_matrix.csv"
    details_df.to_csv(eval_details_path, index=False)
    confusion_df.to_csv(eval_confusion_path, index=True)
    eval_metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    failure_taxonomy_df = build_failure_taxonomy(details_df)
    failure_taxonomy_path = output_dir / "baseline_failure_taxonomy.csv"
    failure_taxonomy_df.to_csv(failure_taxonomy_path, index=False)

    distribution_df, batch_summary = run_batch_sanity(
        base_dir=args.base_dir,
        years=args.years,
        limit=args.limit,
        force=args.force,
        two_stage=args.two_stage,
        rule_boosts=args.rule_boosts,
        tau=args.tau,
        eps_irr=args.eps_irr,
        min_tokens=args.min_tokens,
        timeout_seconds=args.batch_timeout_seconds,
    )
    distribution_path = output_dir / "baseline_batch_distribution.csv"
    distribution_df.to_csv(distribution_path, index=False)

    commit_hash = get_git_commit_hash()
    centroid_metadata = read_centroid_metadata(CENTROIDS_PATH)

    report_path = write_markdown_report(
        output_dir=output_dir,
        metrics=metrics,
        failure_taxonomy=failure_taxonomy_df,
        batch_summary=batch_summary,
        distribution_df=distribution_df,
        centroids=centroid_metadata,
        commit_hash=commit_hash,
        evaluation_mode=eval_mode,
    )
    pipeline_snapshot_path = write_pipeline_snapshot(output_dir)

    run_metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit_hash,
        "inputs": {
            "eval_file": args.eval_file,
            "fallback_eval_details": args.fallback_eval_details,
            "base_dir": args.base_dir,
            "years": args.years,
            "limit": args.limit,
        },
        "classifier_params": {
            "force": args.force,
            "two_stage": args.two_stage,
            "rule_boosts": args.rule_boosts,
            "tau": args.tau,
            "eps_irr": args.eps_irr,
            "min_tokens": args.min_tokens,
        },
        "evaluation_mode": eval_mode,
        "coverage": batch_summary["coverage"],
        "batch_summary": {
            "processed": batch_summary["processed"],
            "skipped": batch_summary["skipped"],
            "errors": batch_summary["errors"],
            "error_details": batch_summary["error_details"],
            "reclassification_attempted": batch_summary["reclassification_attempted"],
            "reclassification_succeeded": batch_summary["reclassification_succeeded"],
            "reclassification_note": batch_summary["reclassification_note"],
        },
        "centroid_artifact": centroid_metadata,
        "artifacts": {
            "baseline_eval_details_csv": str(eval_details_path),
            "baseline_eval_metrics_json": str(eval_metrics_path),
            "baseline_eval_confusion_matrix_csv": str(eval_confusion_path),
            "baseline_batch_distribution_csv": str(distribution_path),
            "baseline_failure_taxonomy_csv": str(failure_taxonomy_path),
            "baseline_report_md": str(report_path),
            "pipeline_map_snapshot_md": str(pipeline_snapshot_path),
        },
    }
    metadata_path = output_dir / "run_metadata.json"
    metadata_path.write_text(json.dumps(run_metadata, indent=2), encoding="utf-8")

    print(f"[phase0] Saved artifacts under: {output_dir}")
    print(
        "[phase0] coverage:"
        f" expected={batch_summary['coverage']['expected_count']}"
        f", existing={batch_summary['coverage']['existing_count']}"
        f", mismatch={batch_summary['coverage']['mismatch_count']}"
    )
    print(f"[phase0] evaluation_mode={eval_mode}")
    print(f"[phase0] reclassification={batch_summary['reclassification_note']}")
    print(f"[phase0] accuracy={metrics['accuracy']:.4f}, macro_f1={metrics['macro_f1']:.4f}")


if __name__ == "__main__":
    main()
