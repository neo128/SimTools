"""Repository validation helpers."""

from __future__ import annotations

import importlib.util
from typing import Any

from simtools.adapters import get_adapter
from simtools.adapters.base import SimToolAdapter
from simtools.core.config_loader import load_global_config, load_profiles
from simtools.core.registry import ToolRegistry


def validate_repository(registry: ToolRegistry | None = None) -> dict[str, Any]:
    registry = registry or ToolRegistry.from_configs()
    issues: list[dict[str, str]] = []

    load_global_config()
    profiles = load_profiles()

    for manifest in registry.all():
        if "smoke" not in manifest.commands:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "manifest is missing commands.smoke",
                }
            )
        if "minimal" not in manifest.install_profiles:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "manifest is missing install_profiles.minimal",
                }
            )
        if importlib.util.find_spec(manifest.adapter.module) is None:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": f"adapter module not importable: {manifest.adapter.module}",
                }
            )
            continue
        adapter = get_adapter(manifest)
        if not isinstance(adapter, SimToolAdapter):
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "adapter does not implement SimToolAdapter",
                }
            )
        if adapter.tool_id != manifest.id:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "adapter.tool_id does not match manifest id",
                }
            )

    return {
        "status": "passed" if not issues else "failed",
        "tool_count": len(registry),
        "profile_count": len(profiles),
        "issues": issues,
    }
