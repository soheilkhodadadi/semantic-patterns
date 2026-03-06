#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "usage: $0 <atlas_cli.py> [args...]" >&2
  exit 2
fi

ATLAS_CLI="$1"
shift

TMPDIR_BASE="${TMPDIR:-/tmp}"
WORKDIR="$(mktemp -d "$TMPDIR_BASE/atlas-isolated.XXXXXX")"
cleanup() {
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

cd "$WORKDIR"
uv run --python 3.12 python "$ATLAS_CLI" "$@"
