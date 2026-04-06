from __future__ import annotations

import json

from semantic_director.schemas import ConditionSpec
from semantic_director.sensors import _sentence_fragment_rate, evaluate_condition


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


def test_sentence_fragment_rate_flags_short_or_truncated_rows(tmp_path):
    csv_path = tmp_path / "sentences.csv"
    csv_path.write_text(
        "sentence\nThis is a complete sentence.\nfragment\nmissing punctuation\n",
        encoding="utf-8",
    )

    rate, extra = _sentence_fragment_rate(csv_path)

    assert rate == 2 / 3
    assert extra == {"rows": 3, "fragment_rows": 2}
