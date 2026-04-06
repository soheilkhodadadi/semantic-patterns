import json

from semantic_director.planner import plan_output_manifest, write_plan_manifest


def test_write_plan_manifest_persists_expected_shape(tmp_path) -> None:
    out_path = tmp_path / "manifest.json"
    result = {
        "runbook_id": "rb-123",
        "iteration_id": "1",
        "phase_name": "phase_a",
        "runbook_file": "runbook.yaml",
        "plan_file": "plan.md",
        "decision_file": "decision.json",
        "llm_refine": {"used_llm": False},
    }

    manifest = plan_output_manifest(result)
    assert manifest["runbook_id"] == "rb-123"
    assert manifest["files"]["plan_md"] == "plan.md"

    write_plan_manifest(result, str(out_path))
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["phase_name"] == "phase_a"
    assert payload["files"]["decision_json"] == "decision.json"
