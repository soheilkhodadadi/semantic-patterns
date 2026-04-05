"""Compatibility shim for AI-washing labeling common helpers."""

from ai_washing_member.labeling.common import *  # noqa: F403
from ai_washing_member.labeling.common import __all__ as _COMMON_ALL

__all__ = list(_COMMON_ALL)
