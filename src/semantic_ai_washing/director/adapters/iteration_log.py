"""Parser for docs/iteration_log.md snapshots."""

from __future__ import annotations

import re
from pathlib import Path

from semantic_ai_washing.director.core.utils import now_utc_iso, sha256_file

_ITERATION_HEADER_RE = re.compile(r"^##\s+Iteration\s+(?P<id>\d+).*$")
_PHASE_HEADER_RE = re.compile(
    r"^###\s+Phase:\s+(?P<name>[^\(]+?)(?:\s*\((?P<status>[^\)]+)\))?\s*$"
)
_BULLET_RE = re.compile(r"^-\s+(?P<text>.+)$")


def parse_iteration_log(path: str) -> dict:
    p = Path(path)
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()

    iterations: list[dict] = []
    phases: list[dict] = []
    current_iteration: dict | None = None
    current_phase: dict | None = None

    for line in lines:
        iteration_match = _ITERATION_HEADER_RE.match(line)
        if iteration_match:
            current_iteration = {
                "iteration_id": iteration_match.group("id"),
                "title": line.strip("# "),
                "phases": [],
            }
            iterations.append(current_iteration)
            current_phase = None
            continue

        phase_match = _PHASE_HEADER_RE.match(line)
        if phase_match:
            current_phase = {
                "name": phase_match.group("name").strip(),
                "status_label": (phase_match.group("status") or "").strip().lower(),
                "details": [],
            }
            phases.append(current_phase)
            if current_iteration is not None:
                current_iteration["phases"].append(current_phase["name"])
            continue

        bullet_match = _BULLET_RE.match(line)
        if bullet_match and current_phase is not None:
            current_phase["details"].append(bullet_match.group("text").strip())

    gates = [
        line.strip("- ")
        for line in lines
        if line.strip().startswith("-") and "gate" in line.lower() and "Iteration 1" not in line
    ]
    risk_lines = [line.strip("- ") for line in lines if re.search(r"\bR[1-9]\b", line)]

    last_successful_gate = "unknown"
    for line in reversed(lines):
        if "status" in line.lower() and "pass" in line.lower():
            last_successful_gate = line.strip()
            break

    return {
        "source_path": path,
        "source_sha256": sha256_file(path),
        "ingested_at": now_utc_iso(),
        "iteration_count": len(iterations),
        "iterations": iterations,
        "phases": phases,
        "global_gates": gates,
        "risk_lines": risk_lines,
        "last_successful_gate": last_successful_gate,
    }
