"""Tool registry backed by YAML manifests."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from simtools.core.config_loader import load_tool_manifests
from simtools.core.errors import ToolNotFoundError
from simtools.core.models import ToolManifest


class ToolRegistry:
    """Registry of simulator manifests."""

    def __init__(self, manifests: Iterable[ToolManifest]):
        self._tools = {manifest.id: manifest for manifest in manifests}

    @classmethod
    def from_configs(cls, tools_dir: Path | None = None) -> "ToolRegistry":
        return cls(load_tool_manifests(tools_dir))

    def all(self) -> list[ToolManifest]:
        return [self._tools[key] for key in sorted(self._tools)]

    def ids(self) -> list[str]:
        return sorted(self._tools)

    def get(self, tool_id: str) -> ToolManifest:
        try:
            return self._tools[tool_id]
        except KeyError as exc:
            valid = ", ".join(self.ids())
            raise ToolNotFoundError(f"Unknown tool id '{tool_id}'. Valid ids: {valid}") from exc

    def filter_by_category(self, category: str) -> list[ToolManifest]:
        return [
            manifest
            for manifest in self.all()
            if category in manifest.category
        ]

    def categories(self) -> list[str]:
        values: set[str] = set()
        for manifest in self.all():
            values.update(manifest.category)
        return sorted(values)

    def __len__(self) -> int:
        return len(self._tools)
