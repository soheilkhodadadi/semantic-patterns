# Director Workspace

This directory stores the autonomous planning and execution control plane for
`semantic_ai_washing.director`.

## Director Pillars

Director is organized around five complementary pillars:

1. Continuous Planning
2. Controlled Execution
3. Iteration Review
4. Playbook Library
5. Continuous Learning

The current implementation uses machine-readable roadmap state, deterministic
review artifacts, and low-blast-radius intervention playbooks to keep project
delivery moving without relying on chat memory.

## Standards Alignment

The Playbook Library and review loop are intentionally mapped to familiar
standards so the system is understandable outside this repository:

- Google SRE runbooks, playbooks, and postmortems
- PMI lessons learned and knowledge capture
- continuous improvement / operational excellence
- data science and ML lifecycle guidance
- MAPE-K style monitor-analyze-plan-execute-knowledge control loops

See `docs/director/playbook_library.md` for the curated library design.

- `config/`: project, autonomy, and cost policies
- `snapshots/`: canonical planning snapshots
- `plans/`: generated runbooks and markdown plans
- `playbooks/`: curated reusable intervention playbooks
- `decisions/`: blocker decision records
- `runs/`: execution states, results, and audit logs
- `reviews/`: iteration and phase review artifacts, approvals, and starter prompts
- `cache/`: LLM cache artifacts

Canonical in-repo strategy inputs:
- `docs/director/implementation_protocol_master.md`
- `docs/director/roadmap_master.md`
- `docs/director/data_architecture_target.md`
- `docs/director/stakeholder_expectations.md`
- `docs/director/proposal_methodology.md`
- `docs/director/playbook_library.md`
- `docs/director/project_scoped_roadmap_pattern_v1.md`
