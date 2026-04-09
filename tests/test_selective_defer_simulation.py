from __future__ import annotations

import pandas as pd

from semantic_ai_washing.classification.simulate_selective_defer import simulate_policies


def test_simulate_policies_prefers_deployable_policy_over_oracle():
    frame = pd.DataFrame(
        [
            {
                "sentence_id": "1",
                "sentence": "a",
                "label": "Actionable",
                "assistive_label": "Actionable",
                "api_b_label": "",
                "local_label": "Speculative",
                "local_confidence": 0.55,
                "conditional_as_margin": 0.05,
                "binary_logreg_relevance_disagreement": False,
                "logreg_label": "Speculative",
            },
            {
                "sentence_id": "2",
                "sentence": "b",
                "label": "Irrelevant",
                "assistive_label": "Irrelevant",
                "api_b_label": "",
                "local_label": "Irrelevant",
                "local_confidence": 0.90,
                "conditional_as_margin": 1.00,
                "binary_logreg_relevance_disagreement": False,
                "logreg_label": "Irrelevant",
            },
        ]
    )

    summaries, detailed = simulate_policies(frame)

    assert summaries[0]["deployable"] is True
    assert summaries[0]["policy_name"] != "oracle_error_only"
    oracle = next(row for row in summaries if row["policy_name"] == "oracle_error_only")
    assert oracle["deployable"] is False
    assert "final_label__api_a_low_conf_060" in detailed.columns
    assert "final_label__oracle_error_only" in detailed.columns
