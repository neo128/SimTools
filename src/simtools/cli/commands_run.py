"""Run command helpers."""

from __future__ import annotations

from simtools.adapters import get_adapter_for_tool
from simtools.core.registry import ToolRegistry


def run_tool(
    registry: ToolRegistry,
    tool_id: str,
    *,
    mode: str,
    dry_run: bool,
) -> dict[str, object]:
    adapter = get_adapter_for_tool(registry, tool_id)
    if mode != "smoke":
        return {
            "tool_id": tool_id,
            "status": "failed",
            "message": f"Unsupported run mode '{mode}'. Supported modes: smoke.",
        }
    return adapter.smoke(dry_run=dry_run)
