from __future__ import annotations

from semantic_director.decision import DecisionEngine
from semantic_director.schemas import BlockerEvent


def test_decision_engine_ranks_options_deterministically(tmp_path) -> None:
    engine = DecisionEngine(decisions_dir=tmp_path)
    blocker = BlockerEvent(
        blocker_id="b1",
        blocker_type="runtime",
        message="command failed",
    )

    first = engine.options_for(blocker)
    second = engine.options_for(blocker)

    assert [opt.option_id for opt in first] == [opt.option_id for opt in second]
    assert first[0].score >= first[-1].score
