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
_GLOBAL_GATES_HEADER_RE = re.compile(r"^###\s+Iteration\s+\d+\s+Global Gates\s*$", re.I)
_HEADING_RE = re.compile(r"^#{2,6}\s+")


def parse_iteration_log(path: str) -> dict:
    p = Path(path)
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()

    iterations: list[dict] = []
    phases: list[dict] = []
    current_iteration: dict | None = None
    current_phase: dict | None = None
    in_code_block = False
    in_global_gates = False
    gates: list[str] = []
    risk_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        iteration_match = _ITERATION_HEADER_RE.match(line)
        if iteration_match:
            current_iteration = {
                "iteration_id": iteration_match.group("id"),
                "title": line.strip("# "),
                "phases": [],
            }
            iterations.append(current_iteration)
            current_phase = None
            in_global_gates = False
            continue

        if _GLOBAL_GATES_HEADER_RE.match(line):
            in_global_gates = True
            current_phase = None
            continue
        if _HEADING_RE.match(line):
            in_global_gates = False

        phase_match = _PHASE_HEADER_RE.match(line)
        if phase_match:
            phase_name = phase_match.group("name").strip()
            if phase_name == "<name>":
                current_phase = None
                continue
            current_phase = {
                "name": phase_name,
                "status_label": (phase_match.group("status") or "").strip().lower(),
                "details": [],
            }
            phases.append(current_phase)
            if current_iteration is not None:
                current_iteration["phases"].append(current_phase["name"])
            continue

        bullet_match = _BULLET_RE.match(line)
        if bullet_match:
            bullet_text = bullet_match.group("text").strip()
            if in_global_gates:
                gates.append(bullet_text)
            if current_phase is not None:
                current_phase["details"].append(bullet_text)
            if re.search(r"\bR[1-9]\b", bullet_text):
                risk_lines.append(bullet_text)
            continue
        if re.search(r"\bR[1-9]\b", line):
            risk_lines.append(line.strip("- ").strip())

    last_successful_gate = "unknown"
    for line in reversed(lines):
        text = line.strip()
        if not text:
            continue
        lowered = text.lower()
        if (
            ("gate" in lowered or "status" in lowered)
            and ("pass" in lowered or "success" in lowered)
            and text.startswith("-")
        ):
            last_successful_gate = text.strip("- ").strip()
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
