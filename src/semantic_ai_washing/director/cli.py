"""Compatibility shim for the package-owned director CLI."""

from semantic_director.cli import build_parser, main

__all__ = ["build_parser", "main"]
