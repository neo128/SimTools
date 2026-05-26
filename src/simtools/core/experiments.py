"""Experiment specifications and run records."""

from __future__ import annotations

import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from simtools.adapters import get_adapter
from simtools.core.benchmarking import (
    build_benchmark_result,
    collect_reproducibility_metadata,
)
from simtools.core.config_loader import load_yaml, repo_root
from simtools.core.environment import collect_system_info
from simtools.core.errors import ConfigError, ToolNotFoundError
from simtools.core.models import ToolManifest
from simtools.core.registry import ToolRegistry

METRICS_SCHEMA_VERSION = "simtools.metrics.v1"
RUN_COMPARISON_SCHEMA_VERSION = "simtools.run_comparison.v1"
SUCCESS_STATUSES = {"passed", "success", "completed"}


class ExperimentSpec(BaseModel):
    """Typed YAML model for a local experiment."""

    model_config = ConfigDict(extra="forbid")

    id: str
    tool_id: str
    scene: str
    task: str
    seed: int
    max_steps: int = Field(gt=0)
    output: dict[str, Any]
    notes: list[str] = Field(default_factory=list)
    source_path: str | None = None

    @field_validator("id", "tool_id")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        if not value:
            raise ValueError("identifier cannot be empty")
        if value != value.lower():
            raise ValueError("identifier must be lowercase")
        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_-")
        if any(char not in allowed for char in value):
            raise ValueError(
                "identifier may contain only lowercase letters, numbers, '-' and '_'"
            )
        return value

    @field_validator("scene", "task")
    @classmethod
    def validate_non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("field cannot be empty")
        return value


class RunStore:
    """Repository-local run artifact store."""

    def __init__(self, root: Path | None = None):
        override = os.environ.get("SIMTOOLS_RUNS_DIR")
        selected = root or (Path(override) if override else repo_root() / ".simtools" / "runs")
        self.root = selected.expanduser().resolve()

    def create_run_dir(self, experiment_id: str) -> Path:
        safe_id = _safe_filename_part(experiment_id)
        for index in range(100):
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            suffix = f"_{index}" if index else ""
            run_dir = self.root / f"{timestamp}_{safe_id}{suffix}"
            if not run_dir.exists():
                (run_dir / "artifacts").mkdir(parents=True, exist_ok=False)
                return run_dir
        raise ConfigError(f"Could not allocate run directory for experiment: {experiment_id}")

    def path_for(self, run_id: str) -> Path:
        path = (self.root / run_id).resolve()
        if path != self.root and self.root not in path.parents:
            raise ConfigError(f"Run path escaped run root: {run_id}")
        return path

    def load_report(self, run_id: str) -> dict[str, Any]:
        run_dir = self.path_for(run_id)
        report_path = run_dir / "report.json"
        if not report_path.exists():
            raise ConfigError(f"Run report does not exist: {report_path}")
        with report_path.open("r", encoding="utf-8") as handle:
            report = json.load(handle)
        report = _report_with_metrics(report, run_dir)
        return {
            **report,
            "run_id": run_id,
            "run_dir": str(run_dir),
            "report_path": str(report_path),
        }

    def list_runs(self, *, include_report: bool = False) -> list[dict[str, Any]]:
        if not self.root.exists():
            return []
        rows: list[dict[str, Any]] = []
        for run_dir in sorted(self.root.iterdir(), reverse=True):
            if not run_dir.is_dir():
                continue
            report = _read_json(run_dir / "report.json")
            run_meta = _read_yaml(run_dir / "run.yaml")
            experiment_id = str(
                report.get("experiment_id")
                or run_meta.get("experiment_id")
                or _experiment_id_from_run_id(run_dir.name)
            )
            row: dict[str, Any] = {
                "run_id": run_dir.name,
                "experiment_id": experiment_id,
                "tool_id": str(report.get("tool_id") or run_meta.get("tool_id") or ""),
                "status": str(report.get("status") or run_meta.get("status") or "unknown"),
                "dry_run": bool(report.get("dry_run", run_meta.get("dry_run", False))),
                "started_at": str(report.get("started_at") or run_meta.get("started_at") or ""),
                "finished_at": str(
                    report.get("finished_at") or run_meta.get("finished_at") or ""
                ),
                "duration_seconds": _coerce_float(
                    report.get("duration_seconds", run_meta.get("duration_seconds", 0.0))
                ),
                "command": str(report.get("command") or run_meta.get("command") or ""),
                "run_dir": str(run_dir),
                "report_path": str(run_dir / "report.json"),
                "artifacts": list(report.get("artifacts") or []),
                "metrics": _report_metrics(report, run_dir),
            }
            if include_report:
                row["report"] = _report_with_metrics(report, run_dir)
            rows.append(row)
        return rows


def default_experiments_dir() -> Path:
    return repo_root() / "configs" / "experiments"


def load_experiment(
    path: Path,
    *,
    registry: ToolRegistry | None = None,
    validate_tool_id: bool = True,
) -> ExperimentSpec:
    data = load_yaml(path)
    data["source_path"] = str(path)
    try:
        spec = ExperimentSpec.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"Invalid experiment config {path}: {exc}") from exc
    if spec.id != path.stem:
        raise ConfigError(
            f"Experiment id '{spec.id}' must match filename stem '{path.stem}'"
        )
    selected_registry = registry
    if validate_tool_id and selected_registry is None:
        selected_registry = ToolRegistry.from_configs()
    if selected_registry is not None:
        _validate_experiment_tool_id(spec, path, selected_registry)
    return spec


def load_experiments(
    experiments_dir: Path | None = None,
    *,
    registry: ToolRegistry | None = None,
    validate_tool_ids: bool = True,
) -> list[ExperimentSpec]:
    directory = experiments_dir or default_experiments_dir()
    if not directory.exists():
        raise ConfigError(f"Experiments directory does not exist: {directory}")
    selected_registry = registry
    if validate_tool_ids and selected_registry is None:
        selected_registry = ToolRegistry.from_configs()
    experiments = [
        load_experiment(
            path,
            registry=selected_registry,
            validate_tool_id=validate_tool_ids,
        )
        for path in sorted(directory.glob("*.yaml"))
    ]
    if not experiments:
        raise ConfigError(f"No experiment configs found in {directory}")
    return experiments


def get_experiment(
    experiment_id: str,
    experiments_dir: Path | None = None,
    *,
    registry: ToolRegistry | None = None,
) -> ExperimentSpec:
    experiments = load_experiments(experiments_dir, registry=registry)
    for experiment in experiments:
        if experiment.id == experiment_id:
            return experiment
    valid = ", ".join(experiment.id for experiment in experiments)
    raise ConfigError(f"Unknown experiment id '{experiment_id}'. Valid ids: {valid}")


def run_experiment(
    experiment: str | ExperimentSpec,
    *,
    registry: ToolRegistry | None = None,
    experiments_dir: Path | None = None,
    run_store: RunStore | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    registry = registry or ToolRegistry.from_configs()
    spec = (
        get_experiment(experiment, experiments_dir, registry=registry)
        if isinstance(experiment, str)
        else experiment
    )
    manifest = registry.get(spec.tool_id)
    store = run_store or RunStore()
    run_dir = store.create_run_dir(spec.id)
    started = datetime.now(timezone.utc)
    started_at = started.isoformat()

    _write_yaml(run_dir / "manifest_snapshot.yaml", manifest.model_dump(mode="json"))
    _write_json(run_dir / "environment.json", collect_system_info())

    if dry_run:
        adapter_result = _dry_run_result(spec, manifest)
    else:
        try:
            adapter_result = _execute_real_or_metadata(spec, manifest)
        except Exception as exc:
            adapter_result = {
                "tool_id": spec.tool_id,
                "status": "failed",
                "message": f"Experiment execution failed: {exc}",
                "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}\n",
                "artifacts": [],
            }

    finished = datetime.now(timezone.utc)
    finished_at = finished.isoformat()
    duration_seconds = max(0.0, (finished - started).total_seconds())
    stdout = _coerce_log(adapter_result.get("stdout", ""))
    stderr = _coerce_log(adapter_result.get("stderr", ""))
    (run_dir / "stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "stderr.log").write_text(stderr, encoding="utf-8")

    artifacts = _artifact_references(adapter_result)
    status = str(adapter_result.get("status") or ("planned" if dry_run else "unknown"))
    metrics = _build_metrics(
        status=status,
        dry_run=dry_run,
        duration_seconds=duration_seconds,
        artifacts=artifacts,
        stdout=stdout,
        stderr=stderr,
        max_steps=spec.max_steps,
    )
    benchmark_result = build_benchmark_result()
    reproducibility = collect_reproducibility_metadata(repo_root())
    report: dict[str, Any] = {
        "run_id": run_dir.name,
        "experiment_id": spec.id,
        "tool_id": spec.tool_id,
        "scene": spec.scene,
        "task": spec.task,
        "seed": spec.seed,
        "max_steps": spec.max_steps,
        "dry_run": dry_run,
        "status": status,
        "message": str(adapter_result.get("message") or ""),
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "command": _experiment_cli_command(spec, dry_run=dry_run),
        "metrics": metrics,
        "benchmark_result": benchmark_result,
        "reproducibility": reproducibility,
        "run_dir": str(run_dir),
        "artifacts_dir": str(run_dir / "artifacts"),
        "artifacts": artifacts,
        "output": spec.output,
        "notes": spec.notes,
        "adapter_result": adapter_result,
    }
    _write_json(run_dir / "report.json", report)

    run_meta = {
        "run_id": run_dir.name,
        "experiment_id": spec.id,
        "tool_id": spec.tool_id,
        "status": status,
        "dry_run": dry_run,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_seconds": duration_seconds,
        "command": report["command"],
        "metrics": metrics,
        "benchmark_result": benchmark_result,
        "reproducibility": reproducibility,
        "experiment": spec.model_dump(mode="json"),
        "files": {
            "manifest_snapshot": "manifest_snapshot.yaml",
            "environment": "environment.json",
            "stdout": "stdout.log",
            "stderr": "stderr.log",
            "report": "report.json",
            "artifacts": "artifacts/",
        },
    }
    _write_yaml(run_dir / "run.yaml", run_meta)
    return {
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "experiment_id": spec.id,
        "tool_id": spec.tool_id,
        "dry_run": dry_run,
        "status": status,
        "duration_seconds": duration_seconds,
        "command": report["command"],
        "report_path": str(run_dir / "report.json"),
        "artifacts": artifacts,
        "metrics": metrics,
    }


def compare_runs(
    run_store: RunStore | None = None,
    *,
    experiment_id: str | None = None,
    tool_id: str | None = None,
    status: str | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """Return a filterable comparison payload for recorded runs."""

    store = run_store or RunStore()
    rows = [
        _comparison_row(row)
        for row in store.list_runs(include_report=True)
        if _run_matches_filters(
            row,
            experiment_id=experiment_id,
            tool_id=tool_id,
            status=status,
            dry_run=dry_run,
        )
    ]
    return {
        "schema_version": RUN_COMPARISON_SCHEMA_VERSION,
        "filters": {
            "experiment_id": experiment_id,
            "tool_id": tool_id,
            "status": status,
            "dry_run": dry_run,
        },
        "summary": _comparison_summary(rows),
        "runs": rows,
    }


def _run_matches_filters(
    row: dict[str, Any],
    *,
    experiment_id: str | None,
    tool_id: str | None,
    status: str | None,
    dry_run: bool | None,
) -> bool:
    if experiment_id is not None and row.get("experiment_id") != experiment_id:
        return False
    if tool_id is not None and row.get("tool_id") != tool_id:
        return False
    if status is not None and row.get("status") != status:
        return False
    if dry_run is not None and bool(row.get("dry_run")) is not dry_run:
        return False
    return True


def _comparison_row(row: dict[str, Any]) -> dict[str, Any]:
    report = row.get("report") if isinstance(row.get("report"), dict) else {}
    metrics = _normalized_metrics(row.get("metrics"), report, Path(str(row["run_dir"])))
    benchmark_result = report.get("benchmark_result")
    benchmark_status = ""
    if isinstance(benchmark_result, dict):
        benchmark_status = str(benchmark_result.get("status") or "")
    return {
        "run_id": str(row["run_id"]),
        "experiment_id": str(row["experiment_id"]),
        "tool_id": str(row["tool_id"]),
        "status": str(row["status"]),
        "dry_run": bool(row["dry_run"]),
        "started_at": str(row.get("started_at") or ""),
        "finished_at": str(row.get("finished_at") or ""),
        "duration_seconds": metrics["duration_seconds"],
        "artifact_count": metrics["artifact_count"],
        "success": metrics["success"],
        "metrics": metrics,
        "benchmark_status": benchmark_status,
        "run_dir": str(row["run_dir"]),
        "report_path": str(row["report_path"]),
    }


def _comparison_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    durations = [float(row["duration_seconds"]) for row in rows]
    status_counts = Counter(str(row["status"]) for row in rows)
    return {
        "run_count": len(rows),
        "experiment_count": len({row["experiment_id"] for row in rows}),
        "tool_count": len({row["tool_id"] for row in rows}),
        "status_counts": dict(sorted(status_counts.items())),
        "dry_run_count": sum(1 for row in rows if row["dry_run"]),
        "success_count": sum(1 for row in rows if row["success"]),
        "total_artifacts": sum(int(row["artifact_count"]) for row in rows),
        "average_duration_seconds": round(sum(durations) / len(durations), 6)
        if durations
        else 0.0,
    }


def _validate_experiment_tool_id(
    spec: ExperimentSpec,
    path: Path,
    registry: ToolRegistry,
) -> None:
    try:
        registry.get(spec.tool_id)
    except ToolNotFoundError as exc:
        valid = ", ".join(registry.ids())
        raise ConfigError(
            f"Invalid experiment config {path}: unknown tool_id "
            f"'{spec.tool_id}' for experiment '{spec.id}'. Valid tool ids: {valid}"
        ) from exc


def _experiment_cli_command(spec: ExperimentSpec, *, dry_run: bool) -> str:
    mode_flag = "--dry-run" if dry_run else "--no-dry-run"
    return f"python -m simtools experiments run {spec.id} {mode_flag}"


def _build_metrics(
    *,
    status: str,
    dry_run: bool,
    duration_seconds: float,
    artifacts: list[str],
    stdout: str,
    stderr: str,
    max_steps: int,
) -> dict[str, Any]:
    return {
        "schema_version": METRICS_SCHEMA_VERSION,
        "success": status in SUCCESS_STATUSES,
        "dry_run": dry_run,
        "duration_seconds": float(duration_seconds),
        "artifact_count": len(artifacts),
        "stdout_bytes": len(stdout.encode("utf-8")),
        "stderr_bytes": len(stderr.encode("utf-8")),
        "max_steps": max_steps,
    }


def _report_with_metrics(report: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    return {**report, "metrics": _report_metrics(report, run_dir)}


def _report_metrics(report: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    return _normalized_metrics(report.get("metrics"), report, run_dir)


def _normalized_metrics(
    metrics: Any,
    report: dict[str, Any],
    run_dir: Path,
) -> dict[str, Any]:
    if isinstance(metrics, dict):
        normalized = dict(metrics)
    else:
        normalized = {}
    artifacts = list(report.get("artifacts") or [])
    stdout = _read_text(run_dir / "stdout.log")
    stderr = _read_text(run_dir / "stderr.log")
    normalized.setdefault("schema_version", METRICS_SCHEMA_VERSION)
    normalized.setdefault("success", str(report.get("status") or "") in SUCCESS_STATUSES)
    normalized.setdefault("dry_run", bool(report.get("dry_run", False)))
    normalized.setdefault("duration_seconds", _coerce_float(report.get("duration_seconds", 0.0)))
    normalized.setdefault("artifact_count", len(artifacts))
    normalized.setdefault("stdout_bytes", len(stdout.encode("utf-8")))
    normalized.setdefault("stderr_bytes", len(stderr.encode("utf-8")))
    normalized.setdefault("max_steps", _coerce_int(report.get("max_steps", 0)))
    normalized["duration_seconds"] = _coerce_float(normalized["duration_seconds"])
    normalized["artifact_count"] = _coerce_int(normalized["artifact_count"])
    normalized["stdout_bytes"] = _coerce_int(normalized["stdout_bytes"])
    normalized["stderr_bytes"] = _coerce_int(normalized["stderr_bytes"])
    normalized["max_steps"] = _coerce_int(normalized["max_steps"])
    normalized["dry_run"] = bool(normalized["dry_run"])
    normalized["success"] = bool(normalized["success"])
    return normalized


def _dry_run_result(spec: ExperimentSpec, manifest: ToolManifest) -> dict[str, Any]:
    return {
        "tool_id": spec.tool_id,
        "status": "planned",
        "message": (
            f"Dry-run experiment plan for {spec.id}; no simulator process was started."
        ),
        "commands": [command.command for command in manifest.commands.values()],
    }


def _execute_real_or_metadata(
    spec: ExperimentSpec,
    manifest: ToolManifest,
) -> dict[str, Any]:
    if spec.tool_id not in {"ai2thor", "habitat", "maniskill"}:
        return {
            "tool_id": spec.tool_id,
            "status": "skipped",
            "message": (
                "Experiment metadata recorded; real experiment execution is not "
                "implemented for this tool in Workbench v0.2."
            ),
            "artifacts": [],
        }

    adapter = get_adapter(manifest)
    if spec.tool_id == "ai2thor":
        return adapter.smoke(dry_run=False)
    return adapter.launch_viewer(
        dry_run=False,
        execute=True,
        scene=spec.scene,
        max_actions=spec.max_steps,
    )


def _artifact_references(result: dict[str, Any]) -> list[str]:
    values: list[str] = []
    artifact = result.get("artifact")
    if artifact:
        values.append(str(artifact))
    artifacts = result.get("artifacts")
    if isinstance(artifacts, list):
        values.extend(str(item) for item in artifacts)
    elif artifacts:
        values.append(str(artifacts))
    return list(dict.fromkeys(values))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _write_yaml(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _coerce_log(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _coerce_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _coerce_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _experiment_id_from_run_id(run_id: str) -> str:
    parts = run_id.split("_", 1)
    return parts[1] if len(parts) == 2 else run_id


def _safe_filename_part(value: str) -> str:
    cleaned = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_"
        for char in value
    ).strip("_")
    return cleaned or "run"
