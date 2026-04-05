from __future__ import annotations

from pathlib import Path

from ai_washing_member.classification.preliminary_pipeline import (
    _resolve_sentence_transformer_source,
)


def test_resolve_sentence_transformer_source_prefers_cached_snapshot(
    tmp_path: Path, monkeypatch
) -> None:
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


def test_resolve_sentence_transformer_source_keeps_explicit_path(tmp_path: Path) -> None:
    local_model = tmp_path / "local-model"
    local_model.mkdir()

    resolved = _resolve_sentence_transformer_source(str(local_model))

    assert resolved == str(local_model)
