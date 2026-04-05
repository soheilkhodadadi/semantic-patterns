import json
from pathlib import Path

from semantic_labcore.audit import (
    append_jsonl,
    default_provenance,
    payload_hash,
    write_audit_record,
)


def test_payload_hash_is_stable_for_same_payload() -> None:
    payload = {"b": 2, "a": 1}
    assert payload_hash(payload) == payload_hash({"a": 1, "b": 2})


def test_append_jsonl_writes_single_json_line(tmp_path: Path) -> None:
    target = tmp_path / "records" / "events.jsonl"
    append_jsonl(target, {"event": "created", "ok": True})

    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == {"event": "created", "ok": True}


def test_write_audit_record_appends_normalized_record(tmp_path: Path) -> None:
    payload = {"phase": "wave3", "status": "ok"}
    out = write_audit_record(tmp_path / "audit", "planning", payload)

    assert out == tmp_path / "audit" / "planning.jsonl"
    rows = out.read_text(encoding="utf-8").splitlines()
    assert len(rows) == 1

    record = json.loads(rows[0])
    assert record["record_type"] == "planning"
    assert record["payload"] == payload
    assert record["payload_hash"] == payload_hash(payload)
    assert "timestamp" in record


def test_default_provenance_is_generic_in_package(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)

    provenance = default_provenance(repo, tool="custom.tool", schema_version="2.0.0")

    assert provenance["tool"] == "custom.tool"
    assert provenance["schema_version"] == "2.0.0"
    assert provenance["git"]["dirty"] is False
    assert "generated_at" in provenance
