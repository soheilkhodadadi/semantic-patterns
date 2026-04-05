from __future__ import annotations

from pathlib import Path

from ai_washing_member.classification.model_runtime import build_legacy_two_stage_runtime
from ai_washing_member.classification.preliminary_pipeline import (
    _resolve_sentence_transformer_source,
    sha256_file,
)


def test_member_preliminary_pipeline_prefers_cached_snapshot(tmp_path: Path, monkeypatch) -> None:
    hub_root = tmp_path / "hf-cache"
    repo_root = hub_root / "models--sentence-transformers--all-mpnet-base-v2"
    snapshot = repo_root / "snapshots" / "abc123"
    snapshot.mkdir(parents=True)
    refs = repo_root / "refs"
    refs.mkdir(parents=True)
    (refs / "main").write_text("abc123\n", encoding="utf-8")
    monkeypatch.setenv("HUGGINGFACE_HUB_CACHE", str(hub_root))

    resolved = _resolve_sentence_transformer_source("sentence-transformers/all-mpnet-base-v2")

    assert resolved == str(snapshot)


def test_member_classification_support_helpers_smoke(tmp_path: Path) -> None:
    payload = tmp_path / "payload.txt"
    payload.write_text("alpha", encoding="utf-8")

    runtime = build_legacy_two_stage_runtime(model_id="legacy-test", tau=0.11, min_tokens=8)

    assert runtime["model_id"] == "legacy-test"
    assert runtime["runtime"]["tau"] == 0.11
    assert runtime["runtime"]["min_tokens"] == 8
    assert len(sha256_file(payload)) == 64
