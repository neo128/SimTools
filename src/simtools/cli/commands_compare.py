"""Compare command rendering."""

from __future__ import annotations

from rich.table import Table

from simtools.core.capability_matrix import matrix_rows
from simtools.core.registry import ToolRegistry


def build_compare_table(registry: ToolRegistry) -> Table:
    table = Table(title="SimTools Capability Matrix")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Tool")
    table.add_column("Backend")
    table.add_column("Install")
    table.add_column("Visualization")
    table.add_column("Headless")
    table.add_column("GPU")
    table.add_column("Assets")

    for row in matrix_rows(registry):
        table.add_row(
            row["id"],
            row["name"],
            row["backend"],
            row["install_level"],
            row["visualization"],
            row["headless"],
            row["gpu"],
            row["large_assets"],
        )
    return table
