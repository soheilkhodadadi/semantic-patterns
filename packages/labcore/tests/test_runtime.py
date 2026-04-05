from pathlib import Path

from semantic_labcore.runtime import (
    dump_json,
    ensure_dir,
    load_json,
    repository_root,
    run_command,
    sha256_file,
    sha256_text,
)


def test_runtime_round_trip(tmp_path: Path) -> None:
    payload = {"status": "ok", "count": 2}
    out = tmp_path / "nested" / "payload.json"

    dump_json(out, payload)

    assert load_json(out) == payload


def test_runtime_hash_and_command(tmp_path: Path) -> None:
    target = tmp_path / "artifact.txt"
    target.write_text("content", encoding="utf-8")

    assert len(sha256_text("labcore-runtime")) == 64
    assert len(sha256_file(target)) == 64

    created = ensure_dir(tmp_path / "a" / "b")
    assert created.is_dir()

    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    nested = repo / "nested" / "child"
    nested.mkdir(parents=True)
    assert repository_root(nested) == str(repo.resolve())

    result = run_command("printf 'hello'", cwd=tmp_path)
    assert result["exit_code"] == 0
    assert result["stdout"] == "hello"
