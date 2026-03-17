# Paper Workflow

This directory is the repo-native writing layer for the paper draft.

The intended workflow is hybrid:

1. Keep the advisor-facing manuscript in Word while the draft is still evolving.
2. Write dynamic sections here in Markdown so they are easy to version, diff, and update from pipeline outputs.
3. Build a draft `.docx` from these files with Pandoc when you want a machine-generated manuscript snapshot.

## Recommended usage

- Put prose in `paper/sections/`.
- Put generated tables, figures, and reusable result snippets in `paper/generated/`.
- Keep the current Word draft as the final citation/polish surface for now.

## Reference docx

If you want the generated Word draft to follow your existing manuscript styling, copy a clean style template to:

`paper/reference.docx`

The build script will use it automatically when present. If it is absent, Pandoc will still build a `.docx` with default Word styling.

## Build

From the repo root:

```bash
make paper-build
```

Outputs:

- `output/paper/manuscript_compiled.md`
- `output/doc/ai_washing_preliminary_draft.docx`

## Notes

- This layer is meant for dynamic methodology/results/discussion content.
- It does not replace Zotero-in-Word right now.
- After the deadline, we can decide whether to keep the hybrid workflow or migrate more of the manuscript into the repo.
