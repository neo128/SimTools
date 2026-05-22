"""Profiles command rendering."""

from __future__ import annotations

from rich.table import Table

from simtools.core.models import ProfileConfig


def build_profiles_table(profiles: list[ProfileConfig]) -> Table:
    table = Table(title="SimTools Profiles")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("Python")
    table.add_column("GPU")
    table.add_column("Viewer Default")
    table.add_column("Large Downloads")

    for profile in profiles:
        table.add_row(
            profile.id,
            profile.name,
            profile.python,
            "recommended" if profile.gpu.recommended else "no",
            profile.install_policy.viewer_launch_default,
            "yes" if profile.install_policy.automatic_large_downloads else "no",
        )
    return table
