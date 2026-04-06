from __future__ import annotations

import argparse
import json

from ai_washing_member.classification.publish_selected_preliminary_eval import run_publish


def test_member_publish_selected_preliminary_eval_pending_selected_model(tmp_path):
    selected_manifest = tmp_path / "selected.json"
    benchmark_matrix = tmp_path / "matrix.json"
    output_report = tmp_path / "selected_eval.json"

    selected_manifest.write_text(
        json.dumps({"status": "pending_primary_benchmark", "winner": {}}, indent=2),
        encoding="utf-8",
    )
    benchmark_matrix.write_text(
        json.dumps(
            {
                "generated_at_utc": "2026-04-06T00:00:00Z",
                "summary": {"primary_benchmark_name": "held_out_v2"},
                "models": [],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    payload = run_publish(
        argparse.Namespace(
            selected_manifest=str(selected_manifest),
            benchmark_matrix=str(benchmark_matrix),
            output_report=str(output_report),
            accuracy_threshold=0.80,
        )
    )

    assert payload["status"] == "pending_selected_model"
    written = json.loads(output_report.read_text(encoding="utf-8"))
    assert written["summary"]["selected_model_id"] == ""
    assert written["summary"]["primary_benchmark_name"] == "held_out_v2"
