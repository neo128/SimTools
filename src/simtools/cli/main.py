"""SimTools command line interface."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from simtools.adapters import get_adapter_for_tool
from simtools.cli.commands_compare import build_compare_table
from simtools.cli.commands_doctor import build_manifest_table, build_system_table
from simtools.cli.commands_info import build_info_panel, build_install_table
from simtools.cli.commands_list import build_list_table
from simtools.cli.commands_run import run_tool
from simtools.cli.commands_view import view_tool
from simtools.core.capability_matrix import matrix_markdown
from simtools.core.errors import ConfigError, ToolNotFoundError
from simtools.core.registry import ToolRegistry
from simtools.core.config_loader import repo_root

console = Console()
app = typer.Typer(no_args_is_help=True, help="SimTools simulator management CLI.")


def registry_or_exit() -> ToolRegistry:
    try:
        return ToolRegistry.from_configs()
    except ConfigError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=2) from exc


def handle_tool_error(exc: ToolNotFoundError) -> None:
    console.print(f"[red]{exc}[/red]")


@app.command("list")
def list_tools(
    category: Optional[str] = typer.Option(None, "--category", "-c"),
    installed: bool = typer.Option(False, "--installed", help="Show installed tools only."),
) -> None:
    """List tools in the registry."""

    registry = registry_or_exit()
    console.print(build_list_table(registry, category=category, installed_only=installed))


@app.command()
def info(tool_id: str = typer.Argument(..., help="Tool id, for example ai2thor.")) -> None:
    """Show manifest information for a tool."""

    registry = registry_or_exit()
    try:
        manifest = registry.get(tool_id)
    except ToolNotFoundError as exc:
        handle_tool_error(exc)
        raise typer.Exit(code=2) from exc
    console.print(build_info_panel(manifest))
    console.print(build_install_table(manifest))
    console.print_json(data=manifest.as_metadata())


@app.command()
def compare(
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table or markdown.",
    )
) -> None:
    """Compare tool capabilities."""

    registry = registry_or_exit()
    if output_format == "table":
        console.print(build_compare_table(registry))
    elif output_format == "markdown":
        console.print(matrix_markdown(registry))
    else:
        console.print("[red]Unsupported format. Use table or markdown.[/red]")
        raise typer.Exit(code=2)


@app.command()
def doctor(
    tool_id: Optional[str] = typer.Argument(None, help="Optional tool id."),
) -> None:
    """Show local diagnostics or tool-specific diagnostics."""

    registry = registry_or_exit()
    if tool_id is None:
        console.print(build_system_table())
        console.print(build_manifest_table(registry))
        return
    try:
        adapter = get_adapter_for_tool(registry, tool_id)
    except ToolNotFoundError as exc:
        handle_tool_error(exc)
        raise typer.Exit(code=2) from exc
    console.print_json(data=adapter.doctor())


@app.command("run")
def run_command(
    tool_id: str = typer.Argument(...),
    mode: str = typer.Option("smoke", "--mode", "-m"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Plan without executing."),
) -> None:
    """Run a tool action such as a smoke test."""

    registry = registry_or_exit()
    try:
        result = run_tool(registry, tool_id, mode=mode, dry_run=dry_run)
    except ToolNotFoundError as exc:
        handle_tool_error(exc)
        raise typer.Exit(code=2) from exc
    console.print_json(data=result)


@app.command("view")
def view_command(
    tool_id: str = typer.Argument(...),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run"),
    execute: bool = typer.Option(False, "--execute", help="Opt in to viewer execution."),
) -> None:
    """Launch or plan a simulator viewer."""

    registry = registry_or_exit()
    try:
        result = view_tool(registry, tool_id, dry_run=dry_run and not execute, execute=execute)
    except ToolNotFoundError as exc:
        handle_tool_error(exc)
        raise typer.Exit(code=2) from exc
    console.print_json(data=result)


@app.command("install-plan")
def install_plan(
    tool_id: str = typer.Argument(...),
    profile: str = typer.Option("minimal", "--profile", "-p"),
) -> None:
    """Print an installation plan without executing it."""

    registry = registry_or_exit()
    try:
        manifest = registry.get(tool_id)
    except ToolNotFoundError as exc:
        handle_tool_error(exc)
        raise typer.Exit(code=2) from exc
    install_profile = manifest.install_profiles.get(profile)
    if install_profile is None:
        valid = ", ".join(manifest.install_profiles)
        console.print(f"[red]Unknown profile '{profile}'. Valid profiles: {valid}[/red]")
        raise typer.Exit(code=2)
    console.print(Panel.fit(
        "\n".join(install_profile.commands) or "No commands declared.",
        title=f"{manifest.name} install plan: {profile}",
        border_style="cyan",
    ))
    if install_profile.notes:
        console.print("[bold]Notes[/bold]")
        for note in install_profile.notes:
            console.print(f"- {note}")
    console.print("[yellow]Dry-run only: no commands were executed.[/yellow]")


@app.command()
def ui(
    port: int = typer.Option(8501, "--port"),
) -> None:
    """Start the local Streamlit dashboard."""

    if importlib.util.find_spec("streamlit") is None:
        console.print(
            Panel(
                "Streamlit is not installed.\n\n"
                "Install the dashboard extra with:\n"
                "  pip install -e \".[dashboard]\"\n\n"
                "No dashboard process was started.",
                title="Dashboard unavailable",
                border_style="yellow",
            ),
            markup=False,
        )
        return

    app_path = repo_root() / "src" / "simtools" / "ui" / "streamlit_app.py"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(port),
        ],
        check=False,
    )


if __name__ == "__main__":
    app()
