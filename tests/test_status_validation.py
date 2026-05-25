from simtools.core.registry import ToolRegistry
from simtools.core.readiness import readiness_summary
from simtools.core.status import tool_status_rows
from simtools.core.validation import validate_repository


def test_tool_status_rows_are_manifest_backed():
    registry = ToolRegistry.from_configs()
    rows = tool_status_rows(registry)
    assert len(rows) == 7
    assert {row["id"] for row in rows} == set(registry.ids())
    assert all("status" in row for row in rows)


def test_validate_repository_passes_for_initial_scaffold():
    registry = ToolRegistry.from_configs()
    result = validate_repository(registry)
    assert result["status"] == "passed"
    assert result["tool_count"] == 7
    assert result["profile_count"] == 4
    assert result["issues"] == []


def test_real_readiness_summary_is_strict_about_viewers():
    registry = ToolRegistry.from_configs()
    result = readiness_summary(registry)
    assert result["status"] == "passed"
    assert result["ready_tools"] == [
        "ai2thor",
        "behavior1k",
        "habitat",
        "maniskill",
        "molmospaces",
        "omnigibson",
        "robocasa365",
    ]
    assert result["not_ready_tools"] == []
