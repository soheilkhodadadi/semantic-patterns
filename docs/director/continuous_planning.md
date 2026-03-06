# Continuous Planning

Director now operates as a deterministic planning control loop.

## Loop
1. Monitor
2. Analyze
3. Plan
4. Execute
5. Knowledge

## Monitor
Director ingests:
- canonical roadmap YAML
- implementation protocol summary
- iteration log snapshot
- compiled repo state
- deferred blocker records
- artifact presence and source-window state

## Analyze
Director compiles:
- task dependency graph
- phase dependency graph
- task readiness states
- phase readiness states
- policy blocks
- source-window deferrals
- sentence-quality gate failures

## Plan
Director scores ready work using configured weights and emits:
- task and phase graph JSON
- readiness JSON
- recommendation JSON
- recommendation Markdown
- optional roadmap patch proposal YAML

Optimization is deterministic in v2. LLM narration remains optional and non-authoritative.

## Execute
`plan` still emits a phase runbook.

For modeled phases, the runbook is compiled from task groups:
- precondition step
- command or manual-handoff step
- verification step

For phase-level-only roadmap entries without task decomposition, director can optimize them but should not execute them until implementation exists or fallback commands are defined.

## Knowledge
Every run should update:
- execution state
- execution result
- blocker and decision records
- optimization artifacts
- iteration log evidence

## Policy
- The optimizer is proposal-only.
- Cross-iteration resequencing may be recommended, but not auto-applied.
- Manual tasks are first-class and must block truthfully when outputs are missing.
- Historical and superseded phases remain visible for traceability and are excluded from next-work ranking.
- Strict science gates are not cleared by infrastructure-only completion.
- Held-out evaluation data remain frozen and cannot be repurposed for training.
