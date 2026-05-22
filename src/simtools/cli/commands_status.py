"""Status command rendering."""

from __future__ import annotations

from rich.table import Table

from simtools.core.registry import ToolRegistry
from simtools.core.status import tool_status_rows


def build_status_table(registry: ToolRegistry) -> Table:
    table = Table(title="SimTools Tool Status")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Install")
    table.add_column("Missing Packages")
    table.add_column("GPU")
    table.add_column("Assets")

    for row in tool_status_rows(registry):
        missing = ", ".join(row["missing_packages"]) or "-"
        table.add_row(
            row["id"],
            row["name"],
            row["status"],
            row["install_level"],
            missing,
            str(row["gpu"]),
            str(row["large_assets_required"]),
        )
    return table
