# Branching Policy

Director standardizes iteration boundaries around an integration branch.

## Branch Types
- Integration branch:
  - `iteration{iteration_id}/integration`
- Optional work branches inside an iteration:
  - `iteration{iteration_id}/{slug}`
- Director/control-plane branches may continue to use:
  - `director/{slug}`

## End-of-Iteration Closeout
1. Push the current working branch.
2. Merge work branches into `iterationN/integration`.
3. Run the iteration review.
4. Approve the review manually.
5. Optionally apply accepted roadmap changes.
6. Sync `iterationN/integration` with `main`.
7. Rerun closeout validation commands.
8. Merge `iterationN/integration` into `main`.
9. Tag the closeout milestone:
   - `iteration{iteration_id}-closeout`

## Start-of-Iteration Kickoff
1. `git switch main`
2. `git pull --ff-only`
3. `git switch -c iterationN/integration`
4. `python -m semantic_ai_washing.director.cli kickoff --iteration N`
5. Use the generated starter prompt as the default next-chat handoff

## Merge Strategy
- Preferred default:
  - `ff-only`
- If `ff-only` is not possible:
  - use a non-interactive PR/merge-commit workflow
  - rerun the closeout validation commands before merge

## Validation Scope
Branch closeout uses the commands declared in roadmap `branching_policy.closeout_validation_commands`.

Current default:
- `make bootstrap`
- `make doctor`
- `make format`
- `make lint`
- `.venv/bin/pytest -q`
