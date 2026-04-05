# Labcore

`labcore/` is the seed of the shared code layer for the lab.

Its purpose is narrow:
- hold small, clearly cross-project helpers and contracts
- avoid mixing domain-specific semantics into the shared layer
- grow only when reuse is real, not speculative

Current Wave 3 rule:
- keep this package small
- add only structure-aware, project-agnostic helpers
- do not move AI-washing analytical logic here just because it exists

Current seed modules:
- `registry/lanes.py` for shared/project lane resolution
- `runtime.py` for low-level runtime helpers that are reusable across projects
