"""Audit sentence integrity before IRR handoff."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import pandas as pd

from semantic_ai_washing.director.core.sensors import _sentence_fragment_rate


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256_file(path: str | Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def run_audit(args: argparse.Namespace) -> dict:
    input_path = Path(args.input_csv)
    output_path = Path(args.output_report)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fragment_rate, extra = _sentence_fragment_rate(input_path)
    report = {
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "git_commit": _git_commit(),
        "input": str(input_path),
        "input_sha256": _sha256_file(input_path),
        "rows": int(extra["rows"]),
        "fragment_rows": int(extra["fragment_rows"]),
        "fragment_rate": float(fragment_rate),
        "threshold": float(args.threshold),
        "passed": bool(fragment_rate <= float(args.threshold)),
    }
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit sentence integrity for IRR prep.")
    parser.add_argument("--input-csv", default="data/labels/v1/labels_master_review.csv")
    parser.add_argument(
        "--output-report",
        default="reports/labels/irr_sentence_quality.json",
    )
    parser.add_argument("--threshold", type=float, default=0.15)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_audit(args)
    print(
        f"[irr] sentence_integrity rows={report['rows']} fragment_rows={report['fragment_rows']} "
        f"fragment_rate={report['fragment_rate']:.6f} passed={report['passed']}"
    )
    print(f"[irr] report -> {args.output_report}")


if __name__ == "__main__":
    main()
