# Projects

This lane is for package-style project members.

Each project member should become a coherent unit with its own:
- `README.md`
- `src/`
- `tests/`
- `docs/`
- `configs/`
- `reports/`
- `output/`
- later, `pyproject.toml` when buildable

Current intended members:
- `projects/ai_washing/`
- `projects/eri/`
- `projects/allocationlab/`

## Workspace member vs path dependency

Use a workspace member when:
- the unit is strategically central to the lab
- we expect iterative local development inside this repo
- the unit benefits from shared tooling and coordinated review
- ownership and scope are stable enough to seed a member

Use a path dependency or staged external intake when:
- the unit still lives primarily in another repo
- the boundary is still unclear
- confidentiality or independent release constraints are stronger
- we want to evaluate the unit before promoting it into the workspace
