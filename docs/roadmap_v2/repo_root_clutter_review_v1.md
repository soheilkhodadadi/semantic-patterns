# Repo Root Clutter Review V1

## Purpose

Review the visible repo-root surfaces after Queue V30 so we can tell the
remaining real front-door files from low-signal or local-only clutter.

## Tracked root files that clearly still matter

These remain part of the intended repo contract:
- `README.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `LICENSE`
- `Makefile`
- `pyproject.toml`
- `requirements.txt`
- `setup.cfg`
- `setup.py`
- `semantic-patterns.code-workspace`

Why:
- they define project setup, packaging, contributor guidance, or the visible
  repo front door

## Tracked root files that are low-signal or legacy-looking

### `old_requirements.txt`

Current posture:
- legacy-looking root artifact
- no direct references in the repo scan
- contents reflect an older environment export rather than the current package
  or `.venv` workflow

Assessment:
- this is the strongest current root-level retire candidate

## Local-only or ignored root noise

These are visible in a local checkout but are not part of the tracked repo
contract:
- `.DS_Store`
- `.env`
- `tmp_doc.docx`

Assessment:
- these are local-machine or ad hoc working files, not repo-structure
  decisions
- they should not drive repo history or migration logic

## Keep-vs-retire posture

Keep:
- repo contract files listed above

Retire candidate:
- `old_requirements.txt`

Local-only noise:
- `.DS_Store`
- `.env`
- `tmp_doc.docx`

## Recommendation

A bounded V32 cleanup queue is justified if it stays narrow:
- retire `old_requirements.txt`
- refresh the root clutter posture/checkpoint docs
- do not mix in local ignored-file cleanup or broader packaging changes
