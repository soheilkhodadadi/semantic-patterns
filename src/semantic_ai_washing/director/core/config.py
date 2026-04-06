"""Compatibility shim for director config helpers."""

from semantic_director.config import (
    DEFAULT_CONFIG,
    DirectorPaths,
    ensure_default_configs,
    ensure_director_dirs,
    get_director_paths,
    load_configs,
    required_file_paths,
)

__all__ = [
    "DEFAULT_CONFIG",
    "DirectorPaths",
    "ensure_default_configs",
    "ensure_director_dirs",
    "get_director_paths",
    "load_configs",
    "required_file_paths",
]
