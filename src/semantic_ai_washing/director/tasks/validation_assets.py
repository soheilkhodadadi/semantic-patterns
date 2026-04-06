"""Compatibility shim for the package-owned validation asset registry module."""

from semantic_director.validation_assets import (
    build_validation_asset_registry,
    classify_dataset_relationship,
    main,
    parse_args,
)

__all__ = [
    "build_validation_asset_registry",
    "classify_dataset_relationship",
    "parse_args",
    "main",
]
