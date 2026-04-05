"""Compatibility shim for director schemas."""

from semantic_director.schemas import *  # noqa: F403
from semantic_director.schemas import __all__ as _SCHEMA_ALL

__all__ = list(_SCHEMA_ALL)
