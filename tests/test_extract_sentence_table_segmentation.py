from __future__ import annotations

import pytest

from ai_washing_member.data.extract_sentence_table import _segment_text


def test_segment_text_dispatches_fast_mode(monkeypatch) -> None:
    monkeypatch.setattr(
        "ai_washing_member.data.extract_sentence_table.segment_sentences_fast",
        lambda text: ["fast"],
    )
    monkeypatch.setattr(
        "ai_washing_member.data.extract_sentence_table.segment_sentences",
        lambda text: ["default"],
    )
    assert _segment_text("hello", "fast") == ["fast"]
    assert _segment_text("hello", "default") == ["default"]


def test_segment_text_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported segmentation mode"):
        _segment_text("hello", "weird")
