"""Artifact command rendering."""

from __future__ import annotations

from rich.table import Table


def build_artifacts_table(artifacts: list[dict[str, object]]) -> Table:
    table = Table(title="SimTools Artifacts")
    table.add_column("Tool", style="cyan", no_wrap=True)
    table.add_column("Path")
    table.add_column("Size")
    table.add_column("Modified")

    for artifact in artifacts:
        table.add_row(
            str(artifact["tool_id"]),
            str(artifact["relative_path"]),
            str(artifact["size_bytes"]),
            str(artifact["modified"]),
        )
    return table
