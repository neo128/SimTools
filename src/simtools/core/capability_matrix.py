"""Capability matrix generation."""

from __future__ import annotations

from typing import Any

from simtools.core.models import ToolManifest
from simtools.core.registry import ToolRegistry


def value_label(value: Any) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value)


def matrix_rows(registry: ToolRegistry) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for manifest in registry.all():
        caps = manifest.capabilities
        rows.append(
            {
                "id": manifest.id,
                "name": manifest.name,
                "backend": manifest.backend.engine,
                "install_level": manifest.install_level,
                "visualization": caps.visualization_label or value_label(caps.visualization),
                "headless": value_label(caps.supports_headless),
                "gpu": value_label(caps.supports_gpu),
                "large_assets": value_label(caps.large_assets_required),
                "tasks": ", ".join(caps.tasks),
            }
        )
    return rows


def matrix_markdown(registry: ToolRegistry) -> str:
    headers = [
        "ID",
        "Tool",
        "Backend",
        "Install Level",
        "Visualization",
        "Headless",
        "GPU",
        "Large Assets",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in matrix_rows(registry):
        lines.append(
            "| {id} | {name} | {backend} | {install_level} | {visualization} | "
            "{headless} | {gpu} | {large_assets} |".format(**row)
        )
    return "\n".join(lines)
