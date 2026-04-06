# AI-Washing Member Shell Readiness V1

## Verdict

`ai_washing` is ready for a real filesystem member shell, but not yet for a buildable project-local `pyproject.toml`.

## Why it is ready for a shell now

The project already has:
- a stable member identity
- active project-owned docs and report lanes
- a real live artifact in the member lane
- explicit mapping notes for legacy vs future authority

That is enough to make the member shell visible in the filesystem.

## Why a buildable local package is still premature

A buildable `projects/ai_washing/pyproject.toml` would currently create too much ambiguity because:
- the authoritative import package still lives at `src/semantic_ai_washing/`
- the manuscript lane still lives under `paper/`
- analysis and processed-data authority still spans legacy top-level lanes
- a duplicate local `semantic_ai_washing` package shell would risk confusion about which package is canonical

## Safe current state

The member should now have real shell directories for:
- `docs/`
- `configs/`
- `reports/`
- `output/`
- `tests/`
- `src/`

These directories are shell anchors, not authority claims.

## Gate for a future buildable member shell

Move toward a real `pyproject.toml` only after:
- the code-side authority map is narrower
- at least one bounded code slice is ready to live under the member shell
- package identity duplication risk is explicitly addressed
- manuscript and project-output boundaries are still clean

## Bottom line

The right next step is a real member shell without a real member package build yet.
That gives structure now without creating import ambiguity.
