from __future__ import annotations

import pandas as pd

from semantic_ai_washing.analysis.build_filing_estimation_sample import _flag_complete


def test_flag_complete_marks_rows_with_all_required_fields() -> None:
    df = pd.DataFrame(
        {
            "car_m1_p1": [0.1, None],
            "ln_assets": [1.0, 2.0],
            "leverage": [0.2, None],
        }
    )
    flag = _flag_complete(df, ["car_m1_p1", "ln_assets", "leverage"])
    assert flag.tolist() == [1, 0]
