# Migration Round D: AI-Washing Member Shell V1

## Purpose

This note records the first real filesystem shell for the `ai_washing` member.

## What changed

The member now has explicit local shell directories for:
- `projects/ai_washing/docs/`
- `projects/ai_washing/configs/`
- `projects/ai_washing/reports/`
- `projects/ai_washing/output/`
- `projects/ai_washing/tests/`
- `projects/ai_washing/src/`

## Readiness decision

The member is ready for a real shell, but not yet for a buildable local package.
That decision is documented in:
- `projects/ai_washing/member_shell_readiness_v1.md`

## Why this is the right move now

This adds structure and exportability potential without creating package identity ambiguity or disturbing the live manuscript lane.

## Acceptance gate

This slice is accepted when:
- the member shell is visible in the filesystem
- each shell directory has a clear README
- the shell does not imply that code authority has already moved

## Bottom line

The `ai_washing` member is now more than a placeholder, but it still avoids a premature duplicate package build.
