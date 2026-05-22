"""Doctor command helpers."""

from __future__ import annotations

from rich.table import Table

from simtools.core.environment import collect_system_info
from simtools.core.registry import ToolRegistry


def build_system_table() -> Table:
    table = Table(title="System")
    table.add_column("Key", style="cyan")
    table.add_column("Value")
    for key, value in collect_system_info().items():
        table.add_row(key, str(value))
    return table


def build_manifest_table(registry: ToolRegistry) -> Table:
    table = Table(title="Manifest Load Status")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("tool_count", str(len(registry)))
    table.add_row("tool_ids", ", ".join(registry.ids()))
    table.add_row("categories", ", ".join(registry.categories()))
    return table
