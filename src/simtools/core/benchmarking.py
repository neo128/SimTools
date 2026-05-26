"""Benchmark-oriented metadata helpers.

This module is intentionally metadata/report-driven. It must not import or
execute simulator adapters.
"""

from __future__ import annotations

import csv
import io
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

from simtools import __version__

TASK_METRICS_SCHEMA_VERSION = "simtools.task_metrics.v1"
BENCHMARK_RESULT_SCHEMA_VERSION = "simtools.benchmark_result.v1"
REPRODUCIBILITY_SCHEMA_VERSION = "simtools.reproducibility.v1"
RUN_EXPORT_SCHEMA_VERSION = "simtools.run_export.v1"


def normalize_task_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the stable task-metrics shape for benchmark-ready reports."""

    metrics = dict(payload)
    custom = metrics.get("custom")
    if not isinstance(custom, dict):
        custom = {}
    return {
        "schema_version": TASK_METRICS_SCHEMA_VERSION,
        "success": metrics.get("success"),
        "score": metrics.get("score"),
        "steps_completed": metrics.get("steps_completed"),
        "collisions": metrics.get("collisions"),
        "custom": dict(custom),
    }


def build_benchmark_result(
    status: str = "not_scored",
    task_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return benchmark state for a run report."""

    return {
        "schema_version": BENCHMARK_RESULT_SCHEMA_VERSION,
        "status": status,
        "task_metrics": normalize_task_metrics(task_metrics or {}),
    }


def collect_reproducibility_metadata(repo_path: Path | None = None) -> dict[str, Any]:
    """Collect local, non-mutating provenance for a run report."""

    return {
        "schema_version": REPRODUCIBILITY_SCHEMA_VERSION,
        "python": platform.python_version(),
        "executable": sys.executable,
        "platform": platform.platform(),
        "git_commit": _git_commit(repo_path),
        "simtools_version": __version__,
    }


def export_runs_json(comparison: dict[str, Any]) -> dict[str, Any]:
    """Wrap a run comparison payload in a stable export schema."""

    return {
        "schema_version": RUN_EXPORT_SCHEMA_VERSION,
        "comparison": comparison,
    }


def export_runs_csv(comparison: dict[str, Any]) -> str:
    """Return a CSV snapshot of comparison rows."""

    output = io.StringIO()
    fieldnames = [
        "run_id",
        "experiment_id",
        "tool_id",
        "status",
        "dry_run",
        "duration_seconds",
        "artifact_count",
        "success",
        "metrics_schema",
        "benchmark_status",
        "report_path",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in comparison.get("runs", []):
        if not isinstance(row, dict):
            continue
        metrics = row.get("metrics") if isinstance(row.get("metrics"), dict) else {}
        writer.writerow(
            {
                "run_id": row.get("run_id", ""),
                "experiment_id": row.get("experiment_id", ""),
                "tool_id": row.get("tool_id", ""),
                "status": row.get("status", ""),
                "dry_run": row.get("dry_run", ""),
                "duration_seconds": row.get("duration_seconds", ""),
                "artifact_count": row.get("artifact_count", ""),
                "success": row.get("success", ""),
                "metrics_schema": metrics.get("schema_version", ""),
                "benchmark_status": row.get("benchmark_status", ""),
                "report_path": row.get("report_path", ""),
            }
        )
    return output.getvalue()


def _git_commit(repo_path: Path | None) -> str:
    if repo_path is None:
        return ""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()
