from __future__ import annotations

from ai_washing_member.labeling.ff12_mapping import FF12Bucket, map_sic_to_ff12


def test_ff12_mapping_member_routes_known_sic_codes() -> None:
    assert map_sic_to_ff12("3571") == FF12Bucket(6, "BusEq")
    assert map_sic_to_ff12("6021") == FF12Bucket(11, "Money")
    assert map_sic_to_ff12("2834") == FF12Bucket(10, "Hlth")


def test_ff12_mapping_member_falls_back_to_other_for_missing_sic() -> None:
    assert map_sic_to_ff12("") == FF12Bucket(12, "Other")
    assert map_sic_to_ff12(None) == FF12Bucket(12, "Other")
