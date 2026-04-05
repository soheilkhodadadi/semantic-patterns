from semantic_director.policies import DEFAULT_RISK_REGISTER


def test_default_risk_register_exports_expected_seed_data() -> None:
    assert len(DEFAULT_RISK_REGISTER) == 7
    assert DEFAULT_RISK_REGISTER[0]["code"] == "R1"
    assert DEFAULT_RISK_REGISTER[-1]["code"] == "R7"
