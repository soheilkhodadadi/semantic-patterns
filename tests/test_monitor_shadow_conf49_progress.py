from __future__ import annotations

import json
from pathlib import Path

from semantic_ai_washing.classification.monitor_shadow_conf49_progress import build_monitor_snapshot


def write_progress(path: Path, *, done: int, pending: int, cost: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                'status': 'running',
                'generated_at_utc': '2026-04-10T15:00:00+00:00',
                'summary': {'iterations_completed': 4, 'max_requests': 10000, 'total_estimated_cost_usd': cost, 'last_run_status': 'in_progress'},
                'counts': {'input_rows': done + pending, 'canonical_labeled_rows': 0, 'assistive_labeled_rows': done, 'pending_rows': pending},
                'last_error': None,
            }
        ),
        encoding='utf-8',
    )


def test_build_monitor_snapshot_computes_summary_and_rate(tmp_path: Path) -> None:
    shard1 = tmp_path / 'shard1.json'
    shard2 = tmp_path / 'shard2.json'
    state = tmp_path / 'state.json'
    write_progress(shard1, done=100, pending=50, cost=1.25)
    write_progress(shard2, done=80, pending=70, cost=0.75)
    state.write_text(json.dumps({'observed_at_utc': '2026-04-10T14:00:00+00:00', 'combined_completed': 1500}), encoding='utf-8')

    snapshot = build_monitor_snapshot((str(shard1), str(shard2)), total_rows=2000, base_completed=1506, state_path=str(state))

    assert snapshot['summary']['combined_completed'] == 1686
    assert snapshot['summary']['combined_pending'] == 120
    assert snapshot['summary']['total_estimated_cost_usd'] == 2.0
    assert snapshot['summary']['recent_rate_rows_per_hour'] is not None
    assert snapshot['summary']['eta_hours'] is not None

