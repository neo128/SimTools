"""List command rendering."""

from __future__ import annotations

from rich.table import Table

from simtools.adapters import get_adapter
from simtools.core.registry import ToolRegistry


def build_list_table(
    registry: ToolRegistry,
    *,
    category: str | None = None,
    installed_only: bool = False,
) -> Table:
    table = Table(title="SimTools Registry")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Backend")
    table.add_column("Visualization")
    table.add_column("Install Level")
    table.add_column("Installed")

    manifests = registry.filter_by_category(category) if category else registry.all()
    for manifest in manifests:
        adapter = get_adapter(manifest)
        installed = adapter.check_installed()
        if installed_only and not installed:
            continue
        table.add_row(
            manifest.id,
            manifest.name,
            manifest.backend.engine,
            manifest.capabilities.visualization_label
            or ("yes" if manifest.capabilities.visualization else "no"),
            manifest.install_level,
            "yes" if installed else "no",
        )
    return table
