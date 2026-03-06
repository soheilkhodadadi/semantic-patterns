# Iteration 1 Starter Prompt

- Recommended new chat: `true`
- Next phase: `iteration2/kickoff-and-preflight`

## Stable Checkpoints
- `b6baec2dcda846c8b5283272ea03e7280dc2fd20`
- `aac143c5a52bc75a01fc135fb67727ab030a7889`
- `7f8a13e99876c3678672e48a2bc70b6b4e062ac7`
- `9ac631c9b7f10742c4f171f44fc2e8f84cf440a3`
- `c3b20341ce51d8344fd11487ec6b4add8eac41eb`
- `6c0f3dbe2486400974fd824a7354cc22aa8594f5`
- `a4f50d652f4581ec9f5b9f04c3f1430a95fc6080`
- `a7f6e82cd000e9a22db9bd47f33e5815c551ea75`
- `6d41f6e85192d3623322047c036dbdda45562481`
- `47363777f19c43045cb13cedeae159fd3894b4ae`
- `bfe48945b7ff9c828e6f31c45e0a5079fccda985`
- `174d36f3ea46fd0e4ec3c3552232b57fe3ecdbe4`

## Key Artifacts
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_8e98f992d1de07fc.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_8e98f992d1de07fc.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_65384ecfb68ad78d.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_65384ecfb68ad78d.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_0a62e7356305be6f.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_0a62e7356305be6f.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_1a84f9c9937bc0d3.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_1a84f9c9937bc0d3.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_73ff6330d958a0df.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_73ff6330d958a0df.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_state_16d394fb26b6a459.json`
- `/Users/soheilkhodadadi/Documents/Projects/semantic-patterns/director/runs/execution_result_16d394fb26b6a459.json`

## Constraints
- Do not start the next iteration before review approval.
- Use the iteration integration branch as the default working base.

## First Commands
- `git switch main`
- `git pull --ff-only`
- `git switch -c iteration2/integration`
- `.venv/bin/python -m semantic_ai_washing.director.cli kickoff --iteration 2`

## Prompt
Use the iteration integration branch as the default base. Start from the next recommended phase, preserve proposal-only roadmap changes until explicitly approved, and prefer a new Codex chat at approved iteration boundaries.
