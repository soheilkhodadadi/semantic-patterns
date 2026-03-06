"""Snapshot ingestor for protocol/roadmap/iteration context."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from semantic_ai_washing.director.adapters.atlas import fetch_atlas_metadata
from semantic_ai_washing.director.adapters.documents import (
    summarize_document,
    summarize_roadmap_model,
)
from semantic_ai_washing.director.adapters.iteration_log import parse_iteration_log
from semantic_ai_washing.director.core.utils import dump_json, now_utc_iso


class SnapshotIngestor:
    def __init__(self, snapshots_dir: str | Path):
        self.snapshots_dir = Path(snapshots_dir)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def ingest(
        self,
        protocol_path: str,
        iteration_log_path: str,
        roadmap_path: str = "",
        roadmap_model_path: str = "",
        atlas_search: str = "",
        atlas_limit: int = 20,
        enable_atlas: bool = False,
    ) -> dict[str, Any]:
        protocol_summary = summarize_document(protocol_path)
        if roadmap_model_path:
            roadmap_summary = summarize_roadmap_model(roadmap_model_path)
        elif roadmap_path:
            roadmap_summary = summarize_document(roadmap_path)
        else:
            raise ValueError("Provide roadmap_path or roadmap_model_path.")
        iteration_summary = parse_iteration_log(iteration_log_path)

        protocol_out = self.snapshots_dir / "protocol_summary.json"
        roadmap_out = self.snapshots_dir / "roadmap_summary.json"
        iteration_out = self.snapshots_dir / "iteration_state.json"

        dump_json(protocol_out, protocol_summary)
        dump_json(roadmap_out, roadmap_summary)
        dump_json(iteration_out, iteration_summary)

        atlas_metadata = {
            "captured_at": now_utc_iso(),
            "enabled": False,
            "notes": ["atlas metadata fetch disabled"],
        }
        if enable_atlas or atlas_search:
            repo_root = str(self.snapshots_dir.parent.parent.resolve())
            atlas_metadata = fetch_atlas_metadata(
                search_term=atlas_search,
                limit=atlas_limit,
                repo_root=repo_root,
            )
            atlas_metadata["enabled"] = True
        atlas_out = self.snapshots_dir / "atlas_metadata.json"
        dump_json(atlas_out, atlas_metadata)

        manifest = {
            "ingested_at": now_utc_iso(),
            "protocol_summary": str(protocol_out),
            "roadmap_summary": str(roadmap_out),
            "iteration_state": str(iteration_out),
            "atlas_metadata": str(atlas_out),
        }
        manifest_out = self.snapshots_dir / "ingest_manifest.json"
        dump_json(manifest_out, manifest)
        return manifest
