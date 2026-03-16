# Iteration 2 Starter Prompt

- Recommended new chat: `true`
- Next phase: `iteration3/kickoff-and-preflight`

## Stable Checkpoints
- `0b01933dda3edf8f733c90ee32aed029fac8f347`

## Key Artifacts
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_9e3044ec80575657.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_9e3044ec80575657.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_ed2674f06982d8b3.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_ed2674f06982d8b3.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_aba43632eb03847a.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_aba43632eb03847a.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_b9ff6738fad09751.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_b9ff6738fad09751.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_96a7623956dd41fe.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_96a7623956dd41fe.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_238ebae834077a35.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_238ebae834077a35.json`

## Constraints
- Do not start the next iteration before review approval.
- Use the iteration integration branch as the default working base.

## First Commands
- `git switch main`
- `git pull --ff-only`
- `git switch -c iteration3/integration`
- `.venv/bin/python -m semantic_ai_washing.director.cli kickoff --iteration 3`

## Prompt
Use the iteration integration branch as the default base. Start from the next recommended phase, preserve proposal-only roadmap changes until explicitly approved, and prefer a new Codex chat at approved iteration boundaries.
