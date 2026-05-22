"""Real local readiness command rendering."""

from __future__ import annotations

from rich.table import Table

from simtools.core.readiness import readiness_rows
from simtools.core.registry import ToolRegistry


def bool_label(value: bool) -> str:
    return "yes" if value else "no"


def build_readiness_table(registry: ToolRegistry) -> Table:
    table = Table(title="SimTools Real Local Run Readiness")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Stage")
    table.add_column("Env")
    table.add_column("Run")
    table.add_column("Smoke")
    table.add_column("Visual")
    table.add_column("Last Verified")
    table.add_column("Blockers")

    for row in readiness_rows(registry):
        blocker_count = len(row["blockers"])
        table.add_row(
            row["id"],
            row["stage"],
            row["local_environment"],
            bool_label(row["local_runnable"]),
            bool_label(row["smoke_verified"]),
            bool_label(row["visualization_verified"]),
            row["last_verified"] or "-",
            "-" if blocker_count == 0 else str(blocker_count),
        )
    return table
