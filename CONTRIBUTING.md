# Contributing

## Branching Convention

Use iteration-scoped branches for incremental delivery:

- `iteration<k>/<dimension>`
- Example: `iteration0/documentation`, `iteration0/error-handling`

Create branches from `main` unless a task explicitly depends on another feature branch.

## Canonical Execution Policy

Use package-module invocation for scripts:

```bash
python -m semantic_ai_washing.<domain>.<module>
```

Legacy `src/...` script paths are compatibility shims and should only be used when validating backward compatibility.

## Local Validation Checklist

Run all checks before opening a PR:

```bash
make bootstrap
make doctor
make format
make lint
pytest -q
```

If your task changes classifier behavior, also run:

```bash
python -m semantic_ai_washing.tests.evaluate_classifier_on_held_out
```

## Pull Request Checklist

- Keep changes within approved task scope.
- Update docs when commands, paths, or outputs change.
- Include test coverage for behavior changes.
- Verify lint/format/tests are green locally.
- Summarize key outputs/metrics in the PR description when relevant.

## Merge Strategy

Use non-fast-forward merges to preserve iteration history:

```bash
git checkout main
git pull --ff-only origin main
git merge --no-ff <feature-branch>
git push origin main
```

## Scope Discipline

Avoid unrelated refactors in task branches.  
If you discover a high-impact issue outside current scope, document it in the PR and open a follow-up task.
