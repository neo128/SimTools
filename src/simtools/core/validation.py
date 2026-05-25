"""Repository validation helpers."""

from __future__ import annotations

import importlib.util
from typing import Any

from simtools.adapters import get_adapter
from simtools.adapters.base import SimToolAdapter
from simtools.core.config_loader import load_global_config, load_profiles
from simtools.core.experiments import load_experiments
from simtools.core.registry import ToolRegistry


def validate_repository(registry: ToolRegistry | None = None) -> dict[str, Any]:
    registry = registry or ToolRegistry.from_configs()
    issues: list[dict[str, str]] = []

    load_global_config()
    profiles = load_profiles()
    experiments = load_experiments(registry=registry)

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
        readiness = manifest.readiness
        if readiness.stage == "real_viewer" and not (
            readiness.local_runnable
            and readiness.smoke_verified
            and readiness.visualization_verified
        ):
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "real_viewer readiness requires runnable, smoke, and visual verification",
                }
            )
        if readiness.stage == "real_viewer" and readiness.blockers:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "real_viewer readiness cannot include blockers",
                }
            )
        if readiness.stage == "real_viewer" and not readiness.last_verified:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "real_viewer readiness requires readiness.last_verified",
                }
            )
        if readiness.visualization_verified and not readiness.viewer_command:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "visualization verification requires readiness.viewer_command",
                }
            )
        if readiness.local_runnable and not readiness.validation_command:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "local runnable readiness requires readiness.validation_command",
                }
            )
        if readiness.stage != "real_viewer" and not readiness.blockers:
            issues.append(
                {
                    "tool_id": manifest.id,
                    "level": "error",
                    "message": "non-real readiness must document blockers",
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

    tool_ids = set(registry.ids())
    for experiment in experiments:
        if experiment.tool_id not in tool_ids:
            issues.append(
                {
                    "tool_id": experiment.tool_id,
                    "level": "error",
                    "message": f"experiment references unknown tool: {experiment.id}",
                }
            )

    return {
        "status": "passed" if not issues else "failed",
        "tool_count": len(registry),
        "profile_count": len(profiles),
        "experiment_count": len(experiments),
        "issues": issues,
    }
