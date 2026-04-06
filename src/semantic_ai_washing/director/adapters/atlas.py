"""Compatibility shim for the package-owned director Atlas adapter."""

from semantic_director.atlas import _run_atlas_command, fetch_atlas_metadata

__all__ = ["fetch_atlas_metadata", "_run_atlas_command"]
