"""SimTools command line interface."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from simtools.adapters import get_adapter_for_tool
from simtools.cli.commands_artifacts import build_artifacts_table
from simtools.cli.commands_compare import build_compare_table
from simtools.cli.commands_doctor import build_manifest_table, build_system_table
from simtools.cli.commands_info import build_info_panel, build_install_table
from simtools.cli.commands_list import build_list_table
from simtools.cli.commands_profiles import build_profiles_table
from simtools.cli.commands_readiness import build_readiness_table
from simtools.cli.commands_run import run_tool
from simtools.cli.commands_status import build_status_table
from simtools.cli.commands_view import view_tool
from simtools.core.artifact_store import ArtifactStore
from simtools.core.benchmarking import export_runs_csv, export_runs_json
from simtools.core.capability_matrix import matrix_markdown
from simtools.core.config_loader import load_profiles, repo_root
from simtools.core.errors import ConfigError, ToolNotFoundError
from simtools.core.experiments import (
    RunStore,
    compare_runs,
    get_experiment,
    load_experiments,
    run_experiment,
)
from simtools.core.registry import ToolRegistry
from simtools.core.readiness import readiness_summary
from simtools.core.status import tool_status_rows
from simtools.core.validation import validate_repository

console = Console()
app = typer.Typer(no_args_is_help=True, help="SimTools simulator management CLI.")
experiments_app = typer.Typer(no_args_is_help=True, help="Experiment workbench commands.")
runs_app = typer.Typer(no_args_is_help=True, help="Run history commands.")


def registry_or_exit() -> ToolRegistry:
    try:
        return ToolRegistry.from_configs()
    except ConfigError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=2) from exc


def handle_tool_error(exc: ToolNotFoundError) -> None:
    console.print(f"[red]{exc}[/red]")


def handle_config_error(exc: ConfigError) -> None:
    console.print(f"[red]Config error:[/red] {exc}")


def build_experiments_table(experiments: list[object]) -> Table:
    table = Table(title="Experiment Library")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Tool")
    table.add_column("Scene")
    table.add_column("Task")
    table.add_column("Max Steps", justify="right")
    for experiment in experiments:
        table.add_row(
            str(getattr(experiment, "id")),
            str(getattr(experiment, "tool_id")),
            str(getattr(experiment, "scene")),
            str(getattr(experiment, "task")),
            str(getattr(experiment, "max_steps")),
        )
    return table


def build_runs_table(runs: list[dict[str, object]]) -> Table:
    table = Table(title="Run History")
    table.add_column("Run ID", style="cyan", no_wrap=True)
    table.add_column("Experiment")
    table.add_column("Tool")
    table.add_column("Status")
    table.add_column("Dry Run")
    table.add_column("Started")
    for run in runs:
        table.add_row(
            str(run["run_id"]),
            str(run["experiment_id"]),
            str(run["tool_id"]),
            str(run["status"]),
            str(run["dry_run"]),
            str(run["started_at"]),
        )
    return table


def build_run_comparison_table(comparison: dict[str, object]) -> Table:
    table = Table(title="Run Comparison")
    table.add_column("Run ID", style="cyan", no_wrap=True)
    table.add_column("Experiment")
    table.add_column("Tool")
    table.add_column("Status")
    table.add_column("Dry")
    table.add_column("Duration", justify="right")
    table.add_column("Artifacts", justify="right")
    table.add_column("Success")
    for run in comparison.get("runs", []):
        if not isinstance(run, dict):
            continue
        table.add_row(
            str(run["run_id"]),
            str(run["experiment_id"]),
            str(run["tool_id"]),
            str(run["status"]),
            str(run["dry_run"]),
            f"{float(run['duration_seconds']):.3f}",
            str(run["artifact_count"]),
            str(run["success"]),
        )
    return table


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
def status(
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of a table."),
) -> None:
    """Show install and package-check status for all registered tools."""

    registry = registry_or_exit()
    if json_output:
        console.print_json(data={"tools": tool_status_rows(registry)})
    else:
        console.print(build_status_table(registry))


@app.command("real-status")
def real_status(
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Exit non-zero unless every registered tool is real-run and visual verified.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of a table."),
) -> None:
    """Show real local runnable and visualization readiness."""

    registry = registry_or_exit()
    summary = readiness_summary(registry)
    if json_output:
        console.print_json(data=summary)
    else:
        console.print(build_readiness_table(registry))
        console.print(
            f"Real-ready tools: {summary['ready_count']}/{summary['tool_count']}"
        )
        if summary["not_ready_tools"]:
            console.print(
                "Not ready: " + ", ".join(summary["not_ready_tools"]),
                style="yellow",
            )
    if strict and summary["status"] != "passed":
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
    save_report: bool = typer.Option(
        True,
        "--save-report/--no-save-report",
        help="Write non-dry-run results under .simtools/artifacts.",
    ),
) -> None:
    """Run a tool action such as a smoke test."""

    registry = registry_or_exit()
    try:
        result = run_tool(registry, tool_id, mode=mode, dry_run=dry_run)
    except ToolNotFoundError as exc:
        handle_tool_error(exc)
        raise typer.Exit(code=2) from exc
    if save_report and not dry_run:
        report_path = ArtifactStore().write_json_report(tool_id, f"{mode}_report", result)
        result = {**result, "report": str(report_path)}
    console.print_json(data=result)


@app.command("view")
def view_command(
    tool_id: str = typer.Argument(...),
    dry_run: bool = typer.Option(True, "--dry-run/--no-dry-run"),
    execute: bool = typer.Option(False, "--execute", help="Opt in to viewer execution."),
    ui: bool = typer.Option(False, "--ui", help="Launch a mouse-driven UI where supported."),
    scene: str = typer.Option("FloorPlan1", "--scene", help="Simulator scene to open."),
    width: int = typer.Option(800, "--width", min=64, help="Viewer render width."),
    height: int = typer.Option(600, "--height", min=64, help="Viewer render height."),
    port: int = typer.Option(8502, "--port", min=1, max=65535, help="UI server port."),
    max_actions: Optional[int] = typer.Option(
        None,
        "--max-actions",
        min=0,
        help="Stop after N terminal actions; 0 validates launch then closes.",
    ),
) -> None:
    """Launch or plan a simulator viewer."""

    registry = registry_or_exit()
    try:
        result = view_tool(
            registry,
            tool_id,
            dry_run=dry_run and not execute,
            execute=execute,
            ui=ui,
            scene=scene,
            width=width,
            height=height,
            port=port,
            max_actions=max_actions,
        )
    except ToolNotFoundError as exc:
        handle_tool_error(exc)
        raise typer.Exit(code=2) from exc
    console.print_json(data=result)


@app.command("install-plan")
def install_plan(
    tool_id: Optional[str] = typer.Argument(None),
    profile: str = typer.Option("minimal", "--profile", "-p"),
) -> None:
    """Print an installation plan without executing it."""

    registry = registry_or_exit()
    if tool_id is None:
        for manifest in registry.all():
            console.print(f"[bold cyan]{manifest.id}[/bold cyan]: {manifest.name}")
            if profile in manifest.install_profiles:
                for command in manifest.install_profiles[profile].commands:
                    console.print(Text(f"  {command}"))
            else:
                console.print(f"  No '{profile}' profile declared.")
        console.print("[yellow]Dry-run only: no commands were executed.[/yellow]")
        return
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
        Text("\n".join(install_profile.commands) or "No commands declared."),
        title=f"{manifest.name} install plan: {profile}",
        border_style="cyan",
    ))
    if install_profile.notes:
        console.print("[bold]Notes[/bold]")
        for note in install_profile.notes:
            console.print(f"- {note}")
    console.print("[yellow]Dry-run only: no commands were executed.[/yellow]")


@app.command()
def profiles(
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of a table."),
) -> None:
    """List local environment profiles."""

    try:
        loaded_profiles = load_profiles()
    except ConfigError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=2) from exc
    if json_output:
        console.print_json(
            data={
                "profiles": [
                    profile.model_dump(mode="json")
                    for profile in loaded_profiles
                ]
            }
        )
    else:
        console.print(build_profiles_table(loaded_profiles))


@app.command()
def artifacts(
    tool_id: Optional[str] = typer.Argument(None, help="Optional tool id."),
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of a table."),
) -> None:
    """List repository-local artifacts."""

    store = ArtifactStore()
    rows = store.list_artifacts(tool_id)
    if json_output:
        console.print_json(data={"artifacts": rows})
        return
    if not rows:
        target = f" for {tool_id}" if tool_id else ""
        console.print(f"No artifacts found{target}.")
        return
    console.print(build_artifacts_table(rows))


@experiments_app.command("list")
def experiments_list(
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of a table."),
) -> None:
    """List experiment configurations."""

    try:
        experiments = load_experiments()
    except ConfigError as exc:
        handle_config_error(exc)
        raise typer.Exit(code=2) from exc
    if json_output:
        console.print_json(
            data={
                "experiments": [
                    experiment.model_dump(mode="json")
                    for experiment in experiments
                ]
            }
        )
        return
    console.print(build_experiments_table(experiments))


@experiments_app.command("info")
def experiments_info(
    experiment_id: str = typer.Argument(..., help="Experiment id."),
) -> None:
    """Show one experiment configuration."""

    try:
        experiment = get_experiment(experiment_id)
    except ConfigError as exc:
        handle_config_error(exc)
        raise typer.Exit(code=2) from exc
    console.print_json(data=experiment.model_dump(mode="json"))


@experiments_app.command("run")
def experiments_run(
    experiment_id: str = typer.Argument(..., help="Experiment id."),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--no-dry-run",
        help="Record a plan without executing, or opt in to real execution.",
    ),
) -> None:
    """Run or dry-run an experiment and record a run directory."""

    registry = registry_or_exit()
    try:
        result = run_experiment(experiment_id, registry=registry, dry_run=dry_run)
    except (ConfigError, ToolNotFoundError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc
    console.print_json(data=result)


@experiments_app.command("report")
def experiments_report(
    run_id: str = typer.Argument(..., help="Run id under .simtools/runs."),
) -> None:
    """Show a recorded experiment report."""

    try:
        report = RunStore().load_report(run_id)
    except ConfigError as exc:
        handle_config_error(exc)
        raise typer.Exit(code=2) from exc
    console.print_json(data=report)


@runs_app.command("list")
def runs_list(
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of a table."),
) -> None:
    """List recorded experiment runs."""

    runs = RunStore().list_runs()
    if json_output:
        console.print_json(data={"runs": runs})
        return
    if not runs:
        console.print("No experiment runs found.")
        return
    console.print(build_runs_table(runs))


@runs_app.command("compare")
def runs_compare(
    experiment_id: Optional[str] = typer.Option(None, "--experiment", help="Filter by experiment id."),
    tool_id: Optional[str] = typer.Option(None, "--tool", help="Filter by tool id."),
    status: Optional[str] = typer.Option(None, "--status", help="Filter by run status."),
    dry_run: Optional[bool] = typer.Option(
        None,
        "--dry-run/--no-dry-run",
        help="Filter by dry-run flag.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of a table."),
) -> None:
    """Compare recorded experiment runs and summarize standard metrics."""

    comparison = compare_runs(
        RunStore(),
        experiment_id=experiment_id,
        tool_id=tool_id,
        status=status,
        dry_run=dry_run,
    )
    if json_output:
        console.print_json(data=comparison)
        return
    if comparison["summary"]["run_count"] == 0:
        console.print("No experiment runs matched the filters.")
        return
    console.print(build_run_comparison_table(comparison))
    console.print_json(data=comparison["summary"])


@runs_app.command("export")
def runs_export(
    output_format: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="Output format: json or csv.",
    ),
) -> None:
    """Export recorded run summaries without executing simulators."""

    comparison = compare_runs(RunStore())
    if output_format == "json":
        console.print_json(data=export_runs_json(comparison))
        return
    if output_format == "csv":
        sys.stdout.write(export_runs_csv(comparison))
        return
    console.print("[red]Unsupported format. Use json or csv.[/red]")
    raise typer.Exit(code=2)


@app.command()
def validate(
    json_output: bool = typer.Option(False, "--json", help="Print JSON instead of text."),
) -> None:
    """Validate manifests, profiles, adapters, and registry wiring."""

    registry = registry_or_exit()
    try:
        result = validate_repository(registry)
    except ConfigError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        raise typer.Exit(code=2) from exc
    if json_output:
        console.print_json(data=result)
    else:
        if result["status"] == "passed":
            console.print(
                f"[green]Validation passed[/green]: {result['tool_count']} tools, "
                f"{result['profile_count']} profiles."
            )
        else:
            console.print("[red]Validation failed[/red]")
            console.print_json(data=result)
    if result["status"] != "passed":
        raise typer.Exit(code=2)


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
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ],
        check=False,
    )


app.add_typer(experiments_app, name="experiments")
app.add_typer(runs_app, name="runs")


if __name__ == "__main__":
    app()
