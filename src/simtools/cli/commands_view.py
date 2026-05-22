"""View command helpers."""

from __future__ import annotations

from simtools.adapters import get_adapter_for_tool
from simtools.core.registry import ToolRegistry


def view_tool(
    registry: ToolRegistry,
    tool_id: str,
    *,
    dry_run: bool,
    execute: bool,
    scene: str,
    width: int,
    height: int,
    max_actions: int | None,
) -> dict[str, object]:
    adapter = get_adapter_for_tool(registry, tool_id)
    return adapter.launch_viewer(
        dry_run=dry_run,
        execute=execute,
        scene=scene,
        width=width,
        height=height,
        max_actions=max_actions,
    )
