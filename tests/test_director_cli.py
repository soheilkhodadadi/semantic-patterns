from __future__ import annotations

import json
from pathlib import Path

from semantic_ai_washing.director.cli import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_cli_init_and_status(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    exit_code = main_with_args(["init"])
    assert exit_code == 0

    status_code = main_with_args(["status"])
    assert status_code == 0


def test_cli_ingest_and_plan(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main_with_args(["init"])

    protocol = tmp_path / "protocol.md"
    roadmap = tmp_path / "roadmap.md"
    iteration_log = tmp_path / "docs" / "iteration_log.md"
    _write(protocol, "Protocol text")
    _write(roadmap, "Roadmap text")
    _write(iteration_log, "## Iteration 1\n### Phase: p1 (start)")

    ingest_code = main_with_args(
        [
            "ingest",
            "--protocol",
            str(protocol),
            "--roadmap",
            str(roadmap),
            "--iteration-log",
            str(iteration_log),
        ]
    )
    assert ingest_code == 0

    plan_code = main_with_args(["plan", "--iteration", "1", "--phase", "p1"])
    assert plan_code == 0

    plans = list((tmp_path / "director" / "plans").glob("runbook_*.yaml"))
    assert plans


def test_cli_decide_from_blocker(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main_with_args(["init"])

    blocker = {
        "schema_version": "1.0.0",
        "blocker_id": "btest",
        "blocker_type": "env",
        "severity": "high",
        "message": "doctor failed",
        "context": {},
    }
    blocker_file = tmp_path / "blocker.json"
    blocker_file.write_text(json.dumps(blocker), encoding="utf-8")

    code = main_with_args(["decide", "--blocker-file", str(blocker_file)])
    assert code == 0

    decisions = list((tmp_path / "director" / "decisions").glob("decision_*.json"))
    assert decisions


def main_with_args(args: list[str]) -> int:
    import sys

    previous = sys.argv
    try:
        sys.argv = ["director"] + args
        return int(main())
    finally:
        sys.argv = previous
