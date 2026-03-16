# Environment Setup

This repository standardizes on one local runtime only:

- Python: **3.11+**
- Architecture on Apple Silicon: **native arm64**
- Canonical environment directory: **`.venv`**

Conda base and legacy repo-local `venv/` directories are not supported as the primary runtime for this project.

## Recommended Setup

### Apple Silicon (M1/M2/M3)

Install a native Python 3.11 first. Homebrew is the simplest path:

```bash
brew install python@3.11
```

Confirm the interpreter is native arm64:

```bash
python3.11 -c "import platform, sys; print(platform.machine()); print(sys.version)"
```

Expected architecture: `arm64`

### Build the canonical repo environment

From the repository root:

```bash
make rebuild-venv
source .venv/bin/activate
make doctor
```

## Validation Commands

Use these after bootstrap and before major pipeline work:

```bash
make doctor
make lint
.venv/bin/pytest -q
.venv/bin/python -m semantic_ai_washing.diagnostics.environment_audit \
  --output reports/environment/environment_audit_post_rebuild_v1.json
.venv/bin/python -m semantic_ai_washing.diagnostics.wrds_smoke \
  --output reports/environment/wrds_smoke_v1.json
```

## WRDS Configuration

Store WRDS credentials in `.env`:

```bash
WRDS_USER=...
WRDS_PASS=...
WRDS_DB_HOST=wrds-pgdata.wharton.upenn.edu
WRDS_DB_PORT=9737
```

The repository uses both `wrds` and `psycopg2-binary` in different data-pull paths, so both packages must import successfully in `.venv`.

Run the live smoke test before any WRDS-dependent extraction or controls refresh.

## Notes

- Do not use Anaconda as the supported repo runtime.
- Do not use the legacy repo-local `venv/` after the `.venv` cutover succeeds.
- Do not migrate package management during this setup step. `uv.lock` can remain in the repo untouched.
