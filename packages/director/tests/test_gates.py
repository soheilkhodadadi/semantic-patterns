from __future__ import annotations

from pathlib import Path

from semantic_director.gates import GateEvaluator
from semantic_director.schemas import PhaseGate


def test_gate_evaluator_handles_missing_outputs(tmp_path: Path) -> None:
    gate = PhaseGate(
        gate_id="phase-001",
        name="Artifacts present",
        description="Ensure required outputs exist.",
        pass_condition="required outputs exist",
        required_outputs=["reports/missing.json"],
        check_command="",
    )
    result = GateEvaluator(repo_root=str(tmp_path)).evaluate(gate)
    assert result["passed"] is False
    assert result["missing_outputs"] == ["reports/missing.json"]


def test_gate_evaluator_passes_simple_command(tmp_path: Path) -> None:
    output_path = tmp_path / "reports" / "ok.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("{}", encoding="utf-8")
    gate = PhaseGate(
        gate_id="phase-002",
        name="Smoke command",
        description="Run a simple smoke command.",
        pass_condition="required outputs exist and command exits 0",
        required_outputs=[str(output_path)],
        check_command="python -c 'print(1)'",
    )
    result = GateEvaluator(repo_root=str(tmp_path)).evaluate(gate)
    assert result["passed"] is True
    assert result["command_result"]["exit_code"] == 0
