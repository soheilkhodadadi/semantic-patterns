"""Restartable assistive-only prelabel runner for bounded review sheets."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

from ai_washing_member.labeling.assistive_prelabel_batch import (
    ASSISTIVE_COLUMNS,
    generate_assistive_prelabels,
)


def _now_utc() -> str:
    return pd.Timestamp.utcnow().isoformat()


def _dump_json(path: str | Path, payload: dict[str, Any]) -> None:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _to_bool_series(series: pd.Series) -> pd.Series:
    return (
        series.fillna(True)
        .map(lambda value: str(value).strip().lower() not in {"false", "0", "no", "n", ""})
        .astype(bool)
    )


def _summarize_frame(input_csv: str | Path, output_csv: str | Path) -> dict[str, int]:
    source_path = Path(output_csv)
    if not source_path.exists():
        source_path = Path(input_csv)
    frame = pd.read_csv(source_path, low_memory=False)

    canonical_mask = frame["label"].fillna("").astype(str).map(str.strip).ne("")
    if "prelabel_eligible" in frame.columns:
        eligible_mask = _to_bool_series(frame["prelabel_eligible"])
    else:
        eligible_mask = pd.Series(True, index=frame.index, dtype=bool)
    sentence_blank_mask = frame["sentence"].fillna("").astype(str).map(str.strip).eq("")

    assistive_mask = pd.Series(False, index=frame.index, dtype=bool)
    for column in ASSISTIVE_COLUMNS:
        if column not in frame.columns:
            continue
        if column == "assistive_label":
            assistive_mask = (
                frame[column].fillna("").astype(str).map(str.strip).ne("") | assistive_mask
            )

    pending_mask = ~canonical_mask & ~assistive_mask & eligible_mask & ~sentence_blank_mask
    return {
        "input_rows": int(len(frame)),
        "canonical_labeled_rows": int(canonical_mask.sum()),
        "assistive_labeled_rows": int(assistive_mask.sum()),
        "pending_rows": int(pending_mask.sum()),
    }


def _write_progress(
    *,
    path: str | Path,
    status: str,
    input_csv: str,
    output_csv: str,
    report_path: str,
    iterations_completed: int,
    max_requests: int,
    total_estimated_cost_usd: float,
    last_run_status: str,
    counts: dict[str, int],
    last_error: dict[str, Any] | None = None,
) -> None:
    payload = {
        "status": status,
        "generated_at_utc": _now_utc(),
        "inputs": {
            "input_csv": str(Path(input_csv).resolve()),
            "output_csv": str(Path(output_csv).resolve()),
            "report_path": str(Path(report_path).resolve()),
        },
        "summary": {
            "iterations_completed": int(iterations_completed),
            "max_requests": int(max_requests),
            "total_estimated_cost_usd": round(float(total_estimated_cost_usd), 6),
            "last_run_status": last_run_status,
        },
        "counts": counts,
        "last_error": last_error,
    }
    _dump_json(path, payload)


def run_restartable_prelabel(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    iterations_completed = 0
    total_estimated_cost_usd = 0.0
    last_report: dict[str, Any] = {}
    last_error: dict[str, Any] | None = None

    counts = _summarize_frame(args.input_csv, args.output_csv)
    _write_progress(
        path=args.progress_report,
        status="starting",
        input_csv=args.input_csv,
        output_csv=args.output_csv,
        report_path=args.report,
        iterations_completed=iterations_completed,
        max_requests=args.max_requests,
        total_estimated_cost_usd=total_estimated_cost_usd,
        last_run_status="not_started",
        counts=counts,
    )

    if args.mode == "dry-run":
        report, exit_code = generate_assistive_prelabels(
            input_csv=args.input_csv,
            output_csv=args.output_csv,
            report_path=args.report,
            policy_path=args.policy,
            cost_policy_path=args.cost_policy,
            mode="dry-run",
            max_rows=int(args.max_rows_per_call),
            sleep_seconds=0.0,
            checkpoint_every=1,
        )
        counts = _summarize_frame(args.input_csv, args.output_csv)
        _write_progress(
            path=args.progress_report,
            status="dry_run",
            input_csv=args.input_csv,
            output_csv=args.output_csv,
            report_path=args.report,
            iterations_completed=0,
            max_requests=args.max_requests,
            total_estimated_cost_usd=0.0,
            last_run_status=str(report.get("status", "dry_run")),
            counts=counts,
            last_error=(report.get("errors") or [None])[-1],
        )
        return report, exit_code

    while True:
        counts = _summarize_frame(args.input_csv, args.output_csv)
        if counts["pending_rows"] == 0:
            _write_progress(
                path=args.progress_report,
                status="passed",
                input_csv=args.input_csv,
                output_csv=args.output_csv,
                report_path=args.report,
                iterations_completed=iterations_completed,
                max_requests=args.max_requests,
                total_estimated_cost_usd=total_estimated_cost_usd,
                last_run_status=str(last_report.get("status", "passed")),
                counts=counts,
                last_error=last_error,
            )
            return last_report or {"status": "passed", "counts": counts}, 0

        if args.max_requests > 0 and iterations_completed >= int(args.max_requests):
            _write_progress(
                path=args.progress_report,
                status="paused_max_requests_reached",
                input_csv=args.input_csv,
                output_csv=args.output_csv,
                report_path=args.report,
                iterations_completed=iterations_completed,
                max_requests=args.max_requests,
                total_estimated_cost_usd=total_estimated_cost_usd,
                last_run_status=str(last_report.get("status", "not_started")),
                counts=counts,
                last_error=last_error,
            )
            return last_report or {"status": "paused_max_requests_reached", "counts": counts}, 0

        report, exit_code = generate_assistive_prelabels(
            input_csv=args.input_csv,
            output_csv=args.output_csv,
            report_path=args.report,
            policy_path=args.policy,
            cost_policy_path=args.cost_policy,
            mode="live",
            max_rows=int(args.max_rows_per_call),
            sleep_seconds=0.0,
            checkpoint_every=1,
        )
        iterations_completed += 1
        total_estimated_cost_usd += float(report.get("usage", {}).get("estimated_cost_usd", 0.0))
        last_report = report
        last_error = (report.get("errors") or [None])[-1]
        counts = _summarize_frame(args.input_csv, args.output_csv)

        if args.max_total_cost_usd > 0 and total_estimated_cost_usd > float(
            args.max_total_cost_usd
        ):
            _write_progress(
                path=args.progress_report,
                status="paused_budget_reached",
                input_csv=args.input_csv,
                output_csv=args.output_csv,
                report_path=args.report,
                iterations_completed=iterations_completed,
                max_requests=args.max_requests,
                total_estimated_cost_usd=total_estimated_cost_usd,
                last_run_status=str(report.get("status", "unknown")),
                counts=counts,
                last_error=last_error,
            )
            return report, 0

        if exit_code != 0 or str(report.get("status", "")) in {"missing_key", "request_failed"}:
            _write_progress(
                path=args.progress_report,
                status="failed",
                input_csv=args.input_csv,
                output_csv=args.output_csv,
                report_path=args.report,
                iterations_completed=iterations_completed,
                max_requests=args.max_requests,
                total_estimated_cost_usd=total_estimated_cost_usd,
                last_run_status=str(report.get("status", "failed")),
                counts=counts,
                last_error=last_error,
            )
            return report, 1

        _write_progress(
            path=args.progress_report,
            status="running",
            input_csv=args.input_csv,
            output_csv=args.output_csv,
            report_path=args.report,
            iterations_completed=iterations_completed,
            max_requests=args.max_requests,
            total_estimated_cost_usd=total_estimated_cost_usd,
            last_run_status=str(report.get("status", "running")),
            counts=counts,
            last_error=last_error,
        )

        if args.sleep_seconds > 0:
            time.sleep(float(args.sleep_seconds))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--progress-report", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--cost-policy", default="director/config/cost_policy.yaml")
    parser.add_argument("--mode", choices=["live", "dry-run"], default="live")
    parser.add_argument("--max-rows-per-call", type=int, default=1)
    parser.add_argument("--max-requests", type=int, default=0)
    parser.add_argument("--max-total-cost-usd", type=float, default=5.0)
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    _, exit_code = run_restartable_prelabel(args)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
