from __future__ import annotations

import json

from semantic_director.state import StateCompiler


def test_state_compiler_infers_active_iteration_and_last_gate(tmp_path) -> None:
    iteration_state = tmp_path / "iteration_state.json"
    iteration_state.write_text(
        json.dumps(
            {
                "iterations": [{"iteration_id": "1"}, {"iteration_id": "2"}],
                "last_successful_gate": "unknown",
            }
        ),
        encoding="utf-8",
    )

    report_dir = tmp_path / "reports" / "iteration1" / "phase1"
    report_dir.mkdir(parents=True)
    (report_dir / "qa_report.json").write_text(
        json.dumps({"summary": {"status": "pass"}}), encoding="utf-8"
    )

    compiler = StateCompiler(repo_root=str(tmp_path))
    compiled = compiler.compile(str(iteration_state), output_path=str(tmp_path / "compiled.json"))

    assert compiled["active_iteration"] == "2"
    assert str(compiled["last_gate_status"]).startswith("pass:")
    assert (tmp_path / "compiled.json").exists()
