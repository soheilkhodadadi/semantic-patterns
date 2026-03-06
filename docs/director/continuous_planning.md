# Continuous Planning

Director now follows a deterministic continuous planning loop:

1. Monitor
2. Analyze
3. Plan
4. Execute
5. Knowledge

## Monitor

Director ingests:

- canonical roadmap YAML
- protocol snapshot
- iteration log snapshot
- compiled repo state
- deferred blocker records
- available artifacts in the repo

## Analyze

Director compiles:

- the task dependency graph
- task readiness states
- missing preconditions
- failed quality checks
- manual blockers

## Plan

Director scores non-satisfied tasks using configured weights and emits:

- task graph JSON
- readiness JSON
- recommendation JSON
- recommendation Markdown
- optional roadmap patch proposal YAML

## Execute

`plan` still emits a phase runbook.

For modeled phases, the runbook is compiled from task groups:

- precondition step
- command or manual-handoff step
- verification step

## Knowledge

Every run should update:

- execution state
- execution result
- blocker or decision records
- optimization artifacts
- iteration log evidence

## Policy

- The optimizer is proposal-only.
- Cross-iteration resequencing may be recommended, but not auto-applied.
- Manual tasks are first-class and must block truthfully when outputs are missing.
- Strict science gates are not cleared by infrastructure-only completion.
