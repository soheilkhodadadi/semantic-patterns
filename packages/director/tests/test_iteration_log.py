from __future__ import annotations

from pathlib import Path

from semantic_director.iteration_log import parse_iteration_log


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_parse_iteration_log_handles_missing_and_conflicting_phase_entries(tmp_path):
    log_path = tmp_path / "iteration_log.md"
    _write(
        log_path,
        """
## Iteration 1 (In Progress)
```md
### Phase: <name>
- Date:
```
### Phase: alpha (start)
- Date: 2026-03-01
- Status: pending
### Phase: alpha (completed)
- Date: 2026-03-02
- Status: done
""".strip(),
    )

    parsed = parse_iteration_log(str(log_path))
    assert parsed["iteration_count"] == 1
    assert len(parsed["phases"]) == 2
    assert parsed["phases"][0]["name"] == "alpha"
    assert parsed["phases"][1]["status_label"] == "completed"
