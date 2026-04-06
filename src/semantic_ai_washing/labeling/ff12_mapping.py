"""Compatibility shim for the ai_washing member-local FF12 mapping helpers."""

from ai_washing_member.labeling.ff12_mapping import *  # noqa: F403
from ai_washing_member.labeling.ff12_mapping import __all__ as _FF12_ALL

__all__ = list(_FF12_ALL)
