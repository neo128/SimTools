from pathlib import Path

import pytest

from simtools.core.config_loader import (
    load_global_config,
    load_profile,
    load_profiles,
    load_tool_manifest,
    load_tool_manifests,
)
from simtools.core.errors import ConfigError


def test_load_initial_tool_manifests():
    manifests = load_tool_manifests()
    ids = {manifest.id for manifest in manifests}
    assert ids == {
        "ai2thor",
        "habitat",
        "behavior1k",
        "maniskill",
        "omnigibson",
        "molmospaces",
        "robocasa365",
    }
    assert all(manifest.readiness.stage for manifest in manifests)
    assert any(manifest.id == "ai2thor" and manifest.readiness.visualization_verified for manifest in manifests)


def test_load_global_config_and_profiles():
    config = load_global_config()
    assert config["project"]["name"] == "SimTools"

    local = load_profile("local")
    assert local.id == "local"
    assert local.install_policy.automatic_large_downloads is False

    profiles = load_profiles()
    assert {profile.id for profile in profiles} == {
        "local",
        "linux_gpu",
        "macos_light",
        "windows_light",
    }


def test_load_fake_manifest_fixture():
    path = Path("tests/fixtures/tools/fake_tool.yaml")
    manifest = load_tool_manifest(path)
    assert manifest.id == "fake_tool"
    assert manifest.backend.engine == "FakeEngine"
    assert manifest.readiness.blockers == ["Fake fixture is not a real simulator."]


def test_manifest_id_must_match_filename(tmp_path):
    path = tmp_path / "wrong.yaml"
    path.write_text(Path("tests/fixtures/tools/fake_tool.yaml").read_text(), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_tool_manifest(path)
