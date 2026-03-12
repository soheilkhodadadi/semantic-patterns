# Director Playbook Library

The Playbook Library is Director's curated response layer for recurring blocker patterns. It is not a generic notebook of ideas. It is a small, maintained set of reusable interventions that fit predictable failure modes.

## What a playbook is
A playbook is a reusable remediation procedure with clear triggers, preconditions, expected outputs, success metrics, and stop conditions.

## What belongs here
- repeatable responses to common blocker types
- low-blast-radius interventions that can be reused across projects
- procedures that are easier to run correctly when written once and reused many times

## What does not belong here
- project-specific one-off notes
- unproven ideas that have not been validated in real work
- raw logs or review artifacts

## Playbooks vs lessons
- Playbooks are curated and reusable.
- Lessons are project-local outcomes recorded in review artifacts.
- A lesson becomes a playbook only after it is clearly reusable and worth standardizing.

## Standards alignment
The library maps to familiar practices rather than inventing a new framework:
- SRE runbooks, playbooks, and postmortems
- PMI lessons learned and knowledge capture
- continuous improvement and retrospectives
- data science and ML lifecycle guidance
- MAPE-K monitor/analyze/plan/execute/knowledge control loops

## Promotion model
1. A blocker occurs.
2. A playbook is recommended or used.
3. The outcome is recorded in review artifacts.
4. If the intervention is reusable and successful, it stays or is promoted into the curated library.
5. If it is a one-off, it stays only as project-local review evidence.
