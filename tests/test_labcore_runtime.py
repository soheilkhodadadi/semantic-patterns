import sys
from pathlib import Path

from semantic_ai_washing.labcore.runtime import (
    dump_json,
    ensure_dir,
    load_json,
    repository_root,
    run_command,
    sha256_file,
    sha256_text,
)
from semantic_ai_washing.director.core.utils import dump_json as director_dump_json
from semantic_ai_washing.director.core.utils import run_command as director_run_command
from semantic_ai_washing.director.core.utils import sha256_text as director_sha256_text


def test_sha256_text_matches_director_compat_shim() -> None:
    text = "labcore-runtime-test"
    assert sha256_text(text) == director_sha256_text(text)


def test_dump_and_load_json_round_trip(tmp_path: Path) -> None:
    payload = {"status": "ok", "count": 2}
    out = tmp_path / "nested" / "payload.json"

    dump_json(out, payload)

    assert out.exists()
    assert load_json(out) == payload


def test_director_dump_json_uses_shared_runtime(tmp_path: Path) -> None:
    payload = {"from": "director-shim"}
    out = tmp_path / "shim" / "payload.json"

    director_dump_json(out, payload)

    assert load_json(out) == payload


def test_ensure_dir_and_repository_root(tmp_path: Path) -> None:
    created = ensure_dir(tmp_path / "a" / "b")
    assert created.exists()
    assert created.is_dir()

    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    nested = repo / "nested" / "child"
    nested.mkdir(parents=True)
    assert repository_root(nested) == str(repo.resolve())


def test_sha256_file_and_run_command(tmp_path: Path) -> None:
    target = tmp_path / "artifact.txt"
    target.write_text("content", encoding="utf-8")

    digest = sha256_file(target)
    assert len(digest) == 64

    result = run_command("printf 'hello'", cwd=tmp_path)
    assert result["exit_code"] == 0
    assert result["stdout"] == "hello"
    assert result["timed_out"] is False


def test_timeout_wording_is_generic_in_labcore_and_compatible_in_director(
    tmp_path: Path,
) -> None:
    command = f'{sys.executable} -c "import time; time.sleep(0.2)"'

    shared = run_command(command, cwd=tmp_path, timeout_seconds=0.01)
    director = director_run_command(command, cwd=tmp_path, timeout_seconds=0.01)

    assert shared["timed_out"] is True
    assert director["timed_out"] is True
    assert "[runtime] command timed out" in shared["stderr"]
    assert "[director] command timed out" in director["stderr"]
