"""Status aggregation for tools and profiles."""

from __future__ import annotations

from typing import Any

from simtools.adapters import get_adapter
from simtools.core.models import ToolManifest
from simtools.core.registry import ToolRegistry


def summarize_tool_status(manifest: ToolManifest) -> dict[str, Any]:
    adapter = get_adapter(manifest)
    doctor = adapter.doctor()
    package_checks = doctor.get("package_checks", {})
    missing_packages = [
        name for name, installed in package_checks.items() if installed is False
    ]
    return {
        "id": manifest.id,
        "name": manifest.name,
        "backend": manifest.backend.engine,
        "install_level": manifest.install_level,
        "status": doctor.get("status", "unknown"),
        "installed": bool(doctor.get("installed", False)),
        "package_checks": package_checks,
        "missing_packages": missing_packages,
        "large_assets_required": manifest.capabilities.large_assets_required,
        "gpu": manifest.capabilities.supports_gpu,
        "message": doctor.get("message", ""),
    }


def tool_status_rows(registry: ToolRegistry) -> list[dict[str, Any]]:
    return [summarize_tool_status(manifest) for manifest in registry.all()]
