"""Compatibility shim for the package-owned director script inventory module."""

from semantic_director.script_inventory import (
    build_script_inventory,
    main,
    parse_args,
    render_script_registry,
)

__all__ = [
    "build_script_inventory",
    "render_script_registry",
    "parse_args",
    "main",
]
