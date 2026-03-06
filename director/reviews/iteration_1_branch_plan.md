# Branch Plan

- Current branch: `director/iteration-review`
- Integration branch: `iteration1/integration`
- Merge target: `main`
- Suggested next phase: `iteration2/kickoff-and-preflight`
- Starter prompt: `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/reviews/iteration_1_starter_prompt.md`

## Closeout Steps
- `git push origin director/iteration-review`
- `git switch iteration1/integration`
- `git merge --ff-only director/iteration-review`
- `git switch main`
- `git pull --ff-only`
- `git switch iteration1/integration`
- `git merge --ff-only main`

## Merge Strategy
- Prefer ff-only. If ff-only is not possible, use a non-interactive PR/merge-commit workflow after rerunning closeout validation.

## Next Iteration Steps
- `git switch main`
- `git pull --ff-only`
- `git switch -c iteration2/integration`
