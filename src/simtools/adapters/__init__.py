"""Adapter loading utilities."""

from __future__ import annotations

import importlib

from simtools.adapters.base import SimToolAdapter
from simtools.core.models import ToolManifest
from simtools.core.registry import ToolRegistry


def get_adapter(manifest: ToolManifest) -> SimToolAdapter:
    module = importlib.import_module(manifest.adapter.module)
    adapter_class = getattr(module, manifest.adapter.class_name)
    adapter = adapter_class(manifest)
    if adapter.tool_id != manifest.id:
        raise ValueError(
            f"Adapter tool_id '{adapter.tool_id}' does not match manifest id '{manifest.id}'"
        )
    return adapter


def get_adapter_for_tool(registry: ToolRegistry, tool_id: str) -> SimToolAdapter:
    return get_adapter(registry.get(tool_id))


def iter_adapters(registry: ToolRegistry) -> list[SimToolAdapter]:
    return [get_adapter(manifest) for manifest in registry.all()]
