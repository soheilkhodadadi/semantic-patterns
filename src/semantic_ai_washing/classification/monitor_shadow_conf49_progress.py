"""Summarize shadow conf49 shard progress and estimate ETA from recent checkpoints."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_SHARD_PROGRESS = (
    "reports/api/shards/conf49_shard01_overnight_progress.json",
    "reports/api/shards/conf49_shard02_overnight_progress.json",
)
DEFAULT_STATE = "reports/api/shards/conf49_monitor_state_v1.json"
DEFAULT_OUTPUT = "reports/api/shards/conf49_monitor_snapshot_v1.json"
DEFAULT_TOTAL_ROWS = 28721
DEFAULT_BASE_COMPLETED = 1506


@dataclass(frozen=True)
class ShardSnapshot:
    path: str
    generated_at_utc: str
    status: str
    assistive_labeled_rows: int
    pending_rows: int
    estimated_cost_usd: float
    age_seconds: float


def _load_progress(path: Path) -> ShardSnapshot:
    data = json.loads(path.read_text(encoding="utf-8"))
    counts = data.get("counts", {})
    summary = data.get("summary", {})
    age_seconds = max(0.0, datetime.now(timezone.utc).timestamp() - path.stat().st_mtime)
    return ShardSnapshot(
        path=str(path.resolve()),
        generated_at_utc=str(data.get("generated_at_utc") or ""),
        status=str(data.get("status") or ""),
        assistive_labeled_rows=int(counts.get("assistive_labeled_rows") or 0),
        pending_rows=int(counts.get("pending_rows") or 0),
        estimated_cost_usd=float(summary.get("total_estimated_cost_usd") or 0.0),
        age_seconds=age_seconds,
    )


def _load_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_ts(value: str) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_monitor_snapshot(
    shard_progress_paths: tuple[str, ...] = DEFAULT_SHARD_PROGRESS,
    *,
    total_rows: int = DEFAULT_TOTAL_ROWS,
    base_completed: int = DEFAULT_BASE_COMPLETED,
    state_path: str = DEFAULT_STATE,
) -> dict[str, Any]:
    shard_snapshots = [_load_progress(Path(path)) for path in shard_progress_paths]
    combined_completed = base_completed + sum(item.assistive_labeled_rows for item in shard_snapshots)
    combined_pending = sum(item.pending_rows for item in shard_snapshots)
    completion_pct = round(combined_completed / total_rows, 4) if total_rows else 0.0
    total_cost_usd = round(sum(item.estimated_cost_usd for item in shard_snapshots), 6)

    now = datetime.now(timezone.utc)
    state_file = Path(state_path)
    prior = _load_state(state_file)
    recent_rate_rows_per_hour = None
    eta_hours = None
    delta_rows = None
    delta_minutes = None

    if prior:
        prior_ts = _parse_ts(str(prior.get("observed_at_utc") or ""))
        prior_completed = int(prior.get("combined_completed") or 0)
        if prior_ts and combined_completed > prior_completed:
            elapsed_hours = (now - prior_ts).total_seconds() / 3600.0
            if elapsed_hours > 0:
                delta_rows = combined_completed - prior_completed
                delta_minutes = round(elapsed_hours * 60.0, 2)
                recent_rate_rows_per_hour = round(delta_rows / elapsed_hours, 2)
                remaining = max(0, total_rows - combined_completed)
                if recent_rate_rows_per_hour > 0:
                    eta_hours = round(remaining / recent_rate_rows_per_hour, 2)

    snapshot = {
        "observed_at_utc": now.isoformat(),
        "inputs": {
            "total_rows": total_rows,
            "base_completed": base_completed,
            "shard_progress_paths": [str(Path(path).resolve()) for path in shard_progress_paths],
        },
        "shards": [item.__dict__ for item in shard_snapshots],
        "summary": {
            "combined_completed": combined_completed,
            "combined_pending": combined_pending,
            "completion_pct": completion_pct,
            "total_estimated_cost_usd": total_cost_usd,
            "delta_rows_since_last_snapshot": delta_rows,
            "delta_minutes_since_last_snapshot": delta_minutes,
            "recent_rate_rows_per_hour": recent_rate_rows_per_hour,
            "eta_hours": eta_hours,
        },
    }
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(
        json.dumps(
            {
                "observed_at_utc": snapshot["observed_at_utc"],
                "combined_completed": combined_completed,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--total-rows", type=int, default=DEFAULT_TOTAL_ROWS)
    parser.add_argument("--base-completed", type=int, default=DEFAULT_BASE_COMPLETED)
    parser.add_argument("--state", default=DEFAULT_STATE)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--shard-progress", nargs="*", default=list(DEFAULT_SHARD_PROGRESS))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    snapshot = build_monitor_snapshot(
        tuple(args.shard_progress),
        total_rows=args.total_rows,
        base_completed=args.base_completed,
        state_path=args.state,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(json.dumps(snapshot["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
