import pytest

from simtools.core.errors import ToolNotFoundError
from simtools.core.registry import ToolRegistry


def test_registry_loads_all_tools():
    registry = ToolRegistry.from_configs()
    assert len(registry) == 6
    assert registry.ids()[0] == "ai2thor"
    assert registry.get("ai2thor").name == "AI2-THOR"


def test_registry_filters_by_category():
    registry = ToolRegistry.from_configs()
    indoor = registry.filter_by_category("indoor_interaction")
    assert {tool.id for tool in indoor} >= {"ai2thor", "habitat"}


def test_registry_unknown_tool_has_valid_ids():
    registry = ToolRegistry.from_configs()
    with pytest.raises(ToolNotFoundError) as exc:
        registry.get("missing")
    assert "Valid ids" in str(exc.value)
    assert "ai2thor" in str(exc.value)
