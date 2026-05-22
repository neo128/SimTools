"""Info command rendering."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table

from simtools.core.models import ToolManifest


def build_info_panel(manifest: ToolManifest) -> Panel:
    body = (
        f"[bold]{manifest.name}[/bold]\n"
        f"ID: {manifest.id}\n"
        f"Backend: {manifest.backend.engine} ({manifest.backend.runtime})\n"
        f"Homepage: {manifest.homepage}\n"
        f"Install level: {manifest.install_level}\n\n"
        f"{manifest.summary}"
    )
    return Panel(body, title="Tool Info", border_style="cyan")


def build_install_table(manifest: ToolManifest) -> Table:
    table = Table(title="Install Profiles")
    table.add_column("Profile", style="cyan")
    table.add_column("Manager")
    table.add_column("Commands")
    for name, profile in manifest.install_profiles.items():
        table.add_row(name, profile.manager, "\n".join(profile.commands))
    return table
