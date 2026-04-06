from __future__ import annotations

from ai_washing_member.labeling.build_labeling_batch import build_labeling_batch


def test_build_labeling_batch_member_imports() -> None:
    assert callable(build_labeling_batch)
