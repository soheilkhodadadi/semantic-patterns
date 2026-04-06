# Repo Root Clutter Posture Refresh V1

## Purpose

Record the intended posture after Queue V31's root-clutter review.

## Current posture

- the repo root is mostly in a good late-stage state
- most tracked root files still serve a real setup, packaging, or contributor
  function
- the reviewed root-level retire candidate has now been retired

## What should not drive cleanup decisions

These are local-only or ignored surfaces, not repo-structure decisions:
- `.DS_Store`
- `.env`
- `tmp_doc.docx`

They may be cleaned locally, but they should not be treated as tracked repo
cleanup wins.

## Safe follow-on scope

The safe narrow follow-on has now been executed:
- `old_requirements.txt` was removed
- related posture/checkpoint docs were refreshed

Any later root cleanup should still not do these:
- delete `semantic-patterns.code-workspace`
- change `setup.py` / `setup.cfg` packaging posture opportunistically
- mix in local ignored-file cleanup
