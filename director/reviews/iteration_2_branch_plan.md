# Branch Plan

- Current branch: `iteration2/integration`
- Integration branch: `iteration2/integration`
- Merge target: `main`
- Suggested next phase: `iteration3/kickoff-and-preflight`
- Starter prompt: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/reviews/iteration_2_starter_prompt.md`

## Closeout Steps
- `git push origin iteration2/integration`
- `git switch iteration2/integration`
- `git merge --ff-only iteration2/integration`
- `git switch main`
- `git pull --ff-only`
- `git switch iteration2/integration`
- `git merge --ff-only main`

## Merge Strategy
- Prefer ff-only. If ff-only is not possible, use a non-interactive PR/merge-commit workflow after rerunning closeout validation.

## Next Iteration Steps
- `git switch main`
- `git pull --ff-only`
- `git switch -c iteration3/integration`
