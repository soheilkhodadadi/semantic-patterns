"""Compatibility shim for the member-owned preliminary centroid training helpers."""

import ai_washing_member.classification.train_preliminary_centroids as _member
from ai_washing_member.classification.train_preliminary_centroids import (
    main,
    parse_args,
    run_training,
)

__all__ = ["run_training", "parse_args", "main"]

member = _member
