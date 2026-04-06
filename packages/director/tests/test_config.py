from __future__ import annotations

from semantic_director.config import ensure_default_configs, get_director_paths, load_configs


def test_config_seed_creates_expected_default_files(tmp_path) -> None:
    paths = get_director_paths(str(tmp_path))

    ensure_default_configs(paths)
    config = load_configs(paths)

    assert (paths.config_dir / "project_profile.yaml").exists()
    assert (paths.model_dir / "roadmap_model.yaml").exists()
    assert config["project_profile"]["project_name"] == "semantic-patterns"
