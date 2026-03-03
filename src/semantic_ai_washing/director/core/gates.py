"""Gate evaluation logic for runbook execution."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.utils import run_command
from semantic_ai_washing.director.schemas import PhaseGate


class GateEvaluator:
    def __init__(self, repo_root: str = "."):
        self.repo_root = repo_root

    def evaluate(self, gate: PhaseGate) -> dict[str, Any]:
        missing_outputs = [path for path in gate.required_outputs if not Path(path).exists()]
        command_result = None
        command_passed = True

        if gate.check_command:
            command_result = run_command(
                gate.check_command, cwd=self.repo_root, timeout_seconds=1200
            )
            command_passed = command_result["exit_code"] == 0

        passed = (not missing_outputs) and command_passed
        return {
            "gate_id": gate.gate_id,
            "name": gate.name,
            "passed": passed,
            "missing_outputs": missing_outputs,
            "command_result": command_result,
        }
