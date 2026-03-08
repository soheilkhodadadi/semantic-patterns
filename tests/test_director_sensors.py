from __future__ import annotations

import json

from semantic_ai_washing.director.core.sensors import evaluate_condition
from semantic_ai_washing.director.schemas import ConditionSpec


def test_json_field_compare_missing_nested_field_returns_failed_condition(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(json.dumps({"status": "dry_run"}), encoding="utf-8")

    result = evaluate_condition(
        ConditionSpec(
            condition_id="missing_usage_count",
            kind="json_field_compare",
            target=f"{report}::usage.request_count",
            operator=">=",
            expected=1,
            on_fail="block",
            message="usage count missing",
            reroute_to=[],
        ),
        repo_root=str(tmp_path),
    )

    assert result["passed"] is False
    assert result["actual"] is None
