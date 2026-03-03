"""Audit trail helpers (append-only JSONL + record hashing)."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from semantic_ai_washing.director.core.utils import ensure_dir, git_info, now_utc_iso


def payload_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def append_jsonl(path: str | Path, payload: dict[str, Any]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, sort_keys=False) + "\n")


def write_audit_record(base_dir: str | Path, record_type: str, payload: dict[str, Any]) -> Path:
    base = ensure_dir(base_dir)
    record = {
        "record_type": record_type,
        "timestamp": now_utc_iso(),
        "payload_hash": payload_hash(payload),
        "payload": payload,
    }
    path = base / f"{record_type}.jsonl"
    append_jsonl(path, record)
    return path


def default_provenance(repo_root: str = ".") -> dict[str, Any]:
    git_meta = git_info(repo_root)
    return {
        "generated_at": now_utc_iso(),
        "git": git_meta,
        "tool": "semantic_ai_washing.director",
        "schema_version": "1.0.0",
    }
