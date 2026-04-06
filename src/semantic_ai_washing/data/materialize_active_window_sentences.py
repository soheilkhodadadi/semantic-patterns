"""Compatibility shim for the member-owned active-window materialization helpers."""

from ai_washing_member.data.materialize_active_window_sentences import (
    DEFAULT_YEARS,
    _build_year_manifest,
    _load_or_refresh_index,
    _load_prior_inventory,
    _manifest_hash,
    _sha256_file,
    main,
    parse_args,
    run_materialization,
)

__all__ = [
    "DEFAULT_YEARS",
    "_load_prior_inventory",
    "_manifest_hash",
    "_load_or_refresh_index",
    "_build_year_manifest",
    "_sha256_file",
    "run_materialization",
    "parse_args",
    "main",
]
