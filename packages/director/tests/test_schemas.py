from __future__ import annotations

from semantic_director.schemas import ConditionSpec, CostUsageRecord, SCHEMA_VERSION


def test_condition_spec_deterministic_helpers_round_trip() -> None:
    condition = ConditionSpec(
        condition_id="cond1",
        kind="artifact_exists",
        target="reports/example.json",
        expected=True,
        message="artifact missing",
    )

    assert condition.schema_version == SCHEMA_VERSION
    assert condition.as_deterministic_dict() == {
        "condition_id": "cond1",
        "expected": True,
        "kind": "artifact_exists",
        "message": "artifact missing",
        "on_fail": "block",
        "operator": "==",
        "reroute_to": [],
        "schema_version": SCHEMA_VERSION,
        "target": "reports/example.json",
    }
    assert (
        condition.as_deterministic_json()
        == '{"condition_id":"cond1","expected":true,"kind":"artifact_exists","message":"artifact missing","on_fail":"block","operator":"==","reroute_to":[],"schema_version":"1.0.0","target":"reports/example.json"}'
    )


def test_cost_usage_record_derives_total_tokens() -> None:
    record = CostUsageRecord(
        usage_id="usage1",
        component="director",
        prompt_tokens=11,
        completion_tokens=7,
        total_tokens=0,
    )

    assert record.total_tokens == 18
