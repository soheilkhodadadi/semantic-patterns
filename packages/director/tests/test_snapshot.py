from __future__ import annotations

import json
from pathlib import Path

from semantic_director.snapshot import SnapshotIngestor


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_snapshot_ingestor_writes_manifest_and_context_files(tmp_path: Path) -> None:
    protocol = tmp_path / "protocol.md"
    roadmap = tmp_path / "roadmap.md"
    iteration_log = tmp_path / "docs" / "iteration_log.md"
    snapshots_dir = tmp_path / "director" / "snapshots"

    _write(protocol, "Diagnostics -> Planning -> Execution")
    _write(roadmap, "Iteration 1: label expansion")
    _write(
        iteration_log,
        """
## Iteration 1 (In Progress)
### Phase: label-expansion (start)
- Validation run: pending
""".strip(),
    )

    ingestor = SnapshotIngestor(snapshots_dir)
    manifest = ingestor.ingest(
        protocol_path=str(protocol),
        roadmap_path=str(roadmap),
        iteration_log_path=str(iteration_log),
        enable_atlas=False,
    )

    protocol_summary = json.loads(Path(manifest["protocol_summary"]).read_text(encoding="utf-8"))
    iteration_state = json.loads(Path(manifest["iteration_state"]).read_text(encoding="utf-8"))
    atlas_metadata = json.loads(Path(manifest["atlas_metadata"]).read_text(encoding="utf-8"))

    assert protocol_summary["source_path"] == str(protocol)
    assert iteration_state["iterations"][0]["iteration_id"] == "1"
    assert atlas_metadata["enabled"] is False
