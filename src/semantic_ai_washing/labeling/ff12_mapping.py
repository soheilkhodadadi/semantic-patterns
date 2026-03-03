"""SIC -> Fama-French 12 industry mapping utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FF12Bucket:
    code: int
    name: str


FF12_NAMES = {
    1: "NoDur",
    2: "Durbl",
    3: "Manuf",
    4: "Enrgy",
    5: "Chems",
    6: "BusEq",
    7: "Telcm",
    8: "Utils",
    9: "Shops",
    10: "Hlth",
    11: "Money",
    12: "Other",
}


def _in_range(value: int, start: int, end: int) -> bool:
    return start <= value <= end


def map_sic_to_ff12(sic) -> FF12Bucket:
    """Map SIC code to a Fama-French 12 bucket (coarse implementation)."""
    try:
        sic_int = int(float(str(sic).strip()))
    except (TypeError, ValueError):
        return FF12Bucket(12, FF12_NAMES[12])

    # 1: Consumer Non-Durables
    if (
        _in_range(sic_int, 100, 999)
        or _in_range(sic_int, 2000, 2399)
        or _in_range(sic_int, 2700, 2749)
        or _in_range(sic_int, 2770, 2799)
        or _in_range(sic_int, 3100, 3199)
        or _in_range(sic_int, 3940, 3989)
    ):
        return FF12Bucket(1, FF12_NAMES[1])

    # 2: Consumer Durables
    if (
        _in_range(sic_int, 2500, 2519)
        or _in_range(sic_int, 2590, 2599)
        or _in_range(sic_int, 3630, 3659)
        or _in_range(sic_int, 3710, 3711)
        or sic_int in {3714, 3716, 3750, 3751, 3792}
        or _in_range(sic_int, 3900, 3939)
        or _in_range(sic_int, 3990, 3999)
    ):
        return FF12Bucket(2, FF12_NAMES[2])

    # 3: Manufacturing
    if (
        _in_range(sic_int, 2520, 2589)
        or _in_range(sic_int, 2600, 2699)
        or _in_range(sic_int, 2750, 2769)
        or _in_range(sic_int, 3000, 3099)
        or _in_range(sic_int, 3200, 3569)
        or _in_range(sic_int, 3580, 3629)
        or _in_range(sic_int, 3700, 3709)
        or _in_range(sic_int, 3712, 3713)
        or sic_int in {3715}
        or _in_range(sic_int, 3717, 3749)
        or _in_range(sic_int, 3752, 3791)
        or _in_range(sic_int, 3793, 3799)
        or _in_range(sic_int, 3830, 3839)
        or _in_range(sic_int, 3860, 3899)
    ):
        return FF12Bucket(3, FF12_NAMES[3])

    # 4: Energy
    if _in_range(sic_int, 1200, 1399) or _in_range(sic_int, 2900, 2999):
        return FF12Bucket(4, FF12_NAMES[4])

    # 5: Chemicals
    if _in_range(sic_int, 2800, 2829) or _in_range(sic_int, 2840, 2899):
        return FF12Bucket(5, FF12_NAMES[5])

    # 6: Business Equipment
    if (
        _in_range(sic_int, 3570, 3579)
        or _in_range(sic_int, 3660, 3692)
        or _in_range(sic_int, 3694, 3699)
        or _in_range(sic_int, 3810, 3829)
        or _in_range(sic_int, 7370, 7379)
    ):
        return FF12Bucket(6, FF12_NAMES[6])

    # 7: Telecommunications
    if _in_range(sic_int, 4800, 4899):
        return FF12Bucket(7, FF12_NAMES[7])

    # 8: Utilities
    if _in_range(sic_int, 4900, 4949):
        return FF12Bucket(8, FF12_NAMES[8])

    # 9: Shops
    if (
        _in_range(sic_int, 5000, 5999)
        or _in_range(sic_int, 7200, 7299)
        or _in_range(sic_int, 7600, 7699)
    ):
        return FF12Bucket(9, FF12_NAMES[9])

    # 10: Healthcare
    if (
        _in_range(sic_int, 2830, 2839)
        or sic_int == 3693
        or _in_range(sic_int, 3840, 3859)
        or _in_range(sic_int, 8000, 8099)
    ):
        return FF12Bucket(10, FF12_NAMES[10])

    # 11: Finance
    if _in_range(sic_int, 6000, 6999):
        return FF12Bucket(11, FF12_NAMES[11])

    return FF12Bucket(12, FF12_NAMES[12])
