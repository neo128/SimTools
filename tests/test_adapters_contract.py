import importlib.util
import sys

from simtools.adapters import get_adapter, iter_adapters
from simtools.adapters.base import SimToolAdapter
from simtools.core.registry import ToolRegistry


HEAVY_MODULES = {
    "ai2thor",
    "habitat",
    "habitat_sim",
    "mani_skill",
    "molmo_spaces",
    "omnigibson",
    "sapien",
    "mujoco",
    "robocasa",
    "robosuite",
    "bddl",
}


def test_all_initial_adapters_follow_contract():
    registry = ToolRegistry.from_configs()
    adapters = iter_adapters(registry)
    assert {adapter.tool_id for adapter in adapters} == set(registry.ids())
    for adapter in adapters:
        assert isinstance(adapter, SimToolAdapter)
        assert adapter.metadata()["id"] == adapter.tool_id
        assert isinstance(adapter.check_installed(), bool)
        assert "status" in adapter.doctor()
        assert "status" in adapter.smoke(dry_run=True)
        assert "status" in adapter.launch_viewer(dry_run=True)
        assert isinstance(adapter.sample_commands(), list)


def test_adapter_diagnostics_do_not_import_heavy_modules():
    registry = ToolRegistry.from_configs()
    before = {name for name in HEAVY_MODULES if name in sys.modules}
    for adapter in iter_adapters(registry):
        adapter.doctor()
        adapter.smoke(dry_run=True)
        adapter.launch_viewer(dry_run=True)
    after = {name for name in HEAVY_MODULES if name in sys.modules}
    assert after == before


def test_ai2thor_smoke_skips_when_not_installed(monkeypatch):
    registry = ToolRegistry.from_configs()
    adapter = get_adapter(registry.get("ai2thor"))
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name):
        if name == "ai2thor":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = adapter.smoke()
    assert result["status"] == "skipped"
    assert "install-plan ai2thor" in " ".join(result["next_steps"])


def test_ai2thor_viewer_execute_skips_when_not_installed(monkeypatch):
    registry = ToolRegistry.from_configs()
    adapter = get_adapter(registry.get("ai2thor"))
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name):
        if name == "ai2thor":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = adapter.launch_viewer(
        dry_run=False,
        execute=True,
        scene="FloorPlan1",
        width=300,
        height=300,
        max_actions=0,
    )
    assert result["status"] == "skipped"
    assert "install-plan ai2thor" in " ".join(result["next_steps"])


def test_ai2thor_viewer_dry_run_includes_execute_command():
    registry = ToolRegistry.from_configs()
    adapter = get_adapter(registry.get("ai2thor"))
    result = adapter.launch_viewer(
        dry_run=True,
        execute=False,
        scene="FloorPlan1",
        width=300,
        height=300,
        max_actions=0,
    )
    assert result["status"] == "planned"
    assert "--execute" in result["commands"][0]
    assert "--max-actions 0" in result["commands"][0]


def test_ai2thor_mouse_ui_dry_run_includes_ui_command():
    registry = ToolRegistry.from_configs()
    adapter = get_adapter(registry.get("ai2thor"))
    result = adapter.launch_viewer(
        dry_run=True,
        execute=False,
        ui=True,
        scene="FloorPlan1",
        width=300,
        height=300,
        port=8502,
    )
    assert result["status"] == "planned"
    assert "--ui --execute" in result["commands"][0]
    assert "--port 8502" in result["commands"][0]


def test_habitat_smoke_skips_when_not_installed(monkeypatch):
    registry = ToolRegistry.from_configs()
    adapter = get_adapter(registry.get("habitat"))
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name):
        if name in {"habitat", "habitat_sim"}:
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = adapter.smoke()
    assert result["status"] == "skipped"
    assert "install-plan habitat" in " ".join(result["next_steps"])


def test_maniskill_smoke_skips_when_not_installed(monkeypatch):
    registry = ToolRegistry.from_configs()
    adapter = get_adapter(registry.get("maniskill"))
    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name):
        if name == "mani_skill":
            return None
        return original_find_spec(name)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)
    result = adapter.smoke()
    assert result["status"] == "skipped"
    assert "install-plan maniskill" in " ".join(result["next_steps"])


def test_planned_heavy_adapters_stay_dry_run():
    registry = ToolRegistry.from_configs()
    for tool_id in {"behavior1k", "molmospaces", "omnigibson", "robocasa365"}:
        adapter = get_adapter(registry.get(tool_id))
        smoke = adapter.smoke(dry_run=True)
        viewer = adapter.launch_viewer(dry_run=True)
        assert smoke["status"] == "planned"
        assert viewer["status"] == "planned"
        assert viewer["commands"]
