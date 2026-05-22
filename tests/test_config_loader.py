from pathlib import Path

import pytest

from simtools.core.config_loader import load_tool_manifest, load_tool_manifests
from simtools.core.errors import ConfigError


def test_load_initial_tool_manifests():
    manifests = load_tool_manifests()
    ids = {manifest.id for manifest in manifests}
    assert ids == {
        "ai2thor",
        "habitat",
        "behavior1k",
        "omnigibson",
        "molmospaces",
        "robocasa365",
    }


def test_load_fake_manifest_fixture():
    path = Path("tests/fixtures/tools/fake_tool.yaml")
    manifest = load_tool_manifest(path)
    assert manifest.id == "fake_tool"
    assert manifest.backend.engine == "FakeEngine"


def test_manifest_id_must_match_filename(tmp_path):
    path = tmp_path / "wrong.yaml"
    path.write_text(Path("tests/fixtures/tools/fake_tool.yaml").read_text(), encoding="utf-8")
    with pytest.raises(ConfigError):
        load_tool_manifest(path)
