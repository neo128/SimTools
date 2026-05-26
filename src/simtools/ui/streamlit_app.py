"""Streamlit dashboard for SimTools.

This module intentionally avoids importing Streamlit at module import time so it
can be imported in base tests without the dashboard extra installed.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from simtools.adapters import iter_adapters
from simtools.core.artifact_store import ArtifactStore
from simtools.core.capability_matrix import matrix_rows
from simtools.core.config_loader import load_profiles
from simtools.core.environment import collect_system_info
from simtools.core.experiments import RunStore, compare_runs, load_experiments
from simtools.core.readiness import readiness_summary
from simtools.core.registry import ToolRegistry


def load_dashboard_data() -> dict[str, Any]:
    registry = ToolRegistry.from_configs()
    rows = matrix_rows(registry)
    artifacts = ArtifactStore().list_artifacts()
    experiments = load_experiment_library(registry=registry)
    runs = load_run_history()
    run_comparison = load_run_comparison()
    category_counts: Counter[str] = Counter()
    install_counts: Counter[str] = Counter()
    for manifest in registry.all():
        category_counts.update(manifest.category)
        install_counts.update([manifest.install_level])
    return {
        "tool_count": len(registry),
        "categories": dict(sorted(category_counts.items())),
        "install_levels": dict(sorted(install_counts.items())),
        "matrix": rows,
        "tools": [manifest.as_metadata() for manifest in registry.all()],
        "doctor": [adapter.doctor() for adapter in iter_adapters(registry)],
        "system": collect_system_info(),
        "profiles": [profile.model_dump(mode="json") for profile in load_profiles()],
        "experiments": experiments,
        "runs": runs,
        "run_summaries": [run_metric_summary(run) for run in runs],
        "run_comparison": run_comparison,
        "artifacts": artifacts,
        "artifact_summary": summarize_artifacts(artifacts),
        "readiness": readiness_summary(registry),
    }


def summarize_artifacts(artifacts: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for artifact in artifacts:
        counts[str(artifact["tool_id"])] += 1
    return dict(sorted(counts.items()))


def run_metric_summary(run_or_report: dict[str, Any]) -> dict[str, Any]:
    report = run_or_report.get("report")
    source = report if isinstance(report, dict) else run_or_report
    metrics = source.get("metrics") if isinstance(source.get("metrics"), dict) else {}
    benchmark = (
        source.get("benchmark_result")
        if isinstance(source.get("benchmark_result"), dict)
        else {}
    )
    artifact_count = metrics.get("artifact_count")
    if artifact_count is None:
        artifact_count = len(source.get("artifacts") or [])
    return {
        "metrics_schema": str(metrics.get("schema_version") or ""),
        "artifact_count": int(artifact_count),
        "benchmark_status": str(benchmark.get("status") or ""),
        "report_path": str(run_or_report.get("report_path") or source.get("report_path") or ""),
    }


def load_run_history(root: str | Path | None = None) -> list[dict[str, Any]]:
    return RunStore(Path(root) if root is not None else None).list_runs(include_report=True)


def load_experiment_library(
    experiments_dir: str | Path | None = None,
    *,
    registry: ToolRegistry | None = None,
) -> list[dict[str, Any]]:
    selected_registry = registry or ToolRegistry.from_configs()
    directory = Path(experiments_dir) if experiments_dir is not None else None
    return [
        experiment.model_dump(mode="json")
        for experiment in load_experiments(directory, registry=selected_registry)
    ]


def load_run_comparison(
    root: str | Path | None = None,
    *,
    experiment_id: str | None = None,
    tool_id: str | None = None,
    status: str | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    store = RunStore(Path(root) if root is not None else None)
    return compare_runs(
        store,
        experiment_id=experiment_id,
        tool_id=tool_id,
        status=status,
        dry_run=dry_run,
    )


def artifact_preview(path: str) -> dict[str, Any]:
    artifact_path = Path(path)
    suffix = artifact_path.suffix.lower()
    if suffix == ".json":
        with artifact_path.open("r", encoding="utf-8") as handle:
            return {"kind": "json", "content": json.load(handle)}
    if suffix in {".png", ".jpg", ".jpeg", ".ppm"}:
        return {"kind": "image", "content": str(artifact_path)}
    if suffix in {".txt", ".log", ".md"}:
        return {
            "kind": "text",
            "content": artifact_path.read_text(encoding="utf-8", errors="replace")[:8000],
        }
    return {"kind": "file", "content": str(artifact_path)}


def main() -> None:
    import streamlit as st

    data = load_dashboard_data()
    st.set_page_config(page_title="SimTools", layout="wide")
    st.title("SimTools")

    (
        overview,
        matrix,
        readiness,
        experiments,
        run_history,
        run_detail,
        detail,
        doctor,
        artifacts,
        profiles,
    ) = st.tabs(
        [
            "Overview",
            "Tool Matrix",
            "Real Readiness",
            "Experiment Library",
            "Run History",
            "Run Detail",
            "Tool Detail",
            "Doctor Preview",
            "Artifacts",
            "Profiles",
        ]
    )

    with overview:
        col1, col2, col3 = st.columns(3)
        col1.metric("Tools", data["tool_count"])
        col2.metric("Categories", len(data["categories"]))
        col3.metric("Install Levels", len(data["install_levels"]))
        st.subheader("Categories")
        st.json(data["categories"])
        st.subheader("Install Levels")
        st.json(data["install_levels"])
        st.subheader("Artifacts")
        st.json(data["artifact_summary"])
        st.subheader("Runs")
        st.metric("Recorded Runs", len(data["runs"]))

    with matrix:
        st.dataframe(data["matrix"], use_container_width=True)

    with readiness:
        summary = data["readiness"]
        col1, col2, col3 = st.columns(3)
        col1.metric("Ready", summary["ready_count"])
        col2.metric("Not Ready", summary["not_ready_count"])
        col3.metric("Total", summary["tool_count"])
        st.dataframe(summary["tools"], use_container_width=True)

    with experiments:
        st.dataframe(data["experiments"], use_container_width=True)

    with run_history:
        if data["runs"]:
            tool_options = ["all"] + sorted({run["tool_id"] for run in data["runs"]})
            experiment_options = ["all"] + sorted({run["experiment_id"] for run in data["runs"]})
            status_options = ["all"] + sorted({run["status"] for run in data["runs"]})
            col1, col2, col3, col4 = st.columns(4)
            selected_tool = col1.selectbox("Tool", tool_options)
            selected_experiment = col2.selectbox("Experiment", experiment_options)
            selected_status = col3.selectbox("Status", status_options)
            selected_dry = col4.selectbox("Dry Run", ["all", "true", "false"])
            comparison = load_run_comparison(
                tool_id=None if selected_tool == "all" else selected_tool,
                experiment_id=None if selected_experiment == "all" else selected_experiment,
                status=None if selected_status == "all" else selected_status,
                dry_run=None if selected_dry == "all" else selected_dry == "true",
            )
            st.dataframe(comparison["runs"], use_container_width=True)
            st.subheader("Comparison Summary")
            st.json(comparison["summary"])
        else:
            st.info("Experiment runs will appear under .simtools/runs.")

    with run_detail:
        if data["runs"]:
            run_options = [run["run_id"] for run in data["runs"]]
            selected_run_id = st.selectbox("Run", run_options)
            selected_run = next(run for run in data["runs"] if run["run_id"] == selected_run_id)
            selected_report = selected_run["report"]
            st.subheader("Benchmark Summary")
            st.json(run_metric_summary(selected_run))
            st.subheader("Paths")
            st.json(
                {
                    "run_dir": selected_run["run_dir"],
                    "report_path": selected_run["report_path"],
                    "artifacts_dir": selected_report.get("artifacts_dir", ""),
                }
            )
            st.subheader("Report")
            st.json(selected_run["report"])
            st.subheader("Artifact References")
            if selected_run["artifacts"]:
                st.write(selected_run["artifacts"])
            else:
                st.write([])
        else:
            st.info("Run reports will appear after an experiment is executed or dry-run.")

    with detail:
        tool_names = {tool["name"]: tool for tool in data["tools"]}
        selected_name = st.selectbox("Tool", list(tool_names))
        selected = tool_names[selected_name]
        st.subheader(selected["name"])
        st.write(selected["summary"])
        st.json(
            {
                "id": selected["id"],
                "backend": selected["backend"],
                "capabilities": selected["capabilities"],
                "install_profiles": selected["install_profiles"],
                "commands": selected["commands"],
            }
        )

    with doctor:
        st.subheader("System")
        st.json(data["system"])
        st.subheader("Adapters")
        st.json(data["doctor"])

    with artifacts:
        if data["artifacts"]:
            tool_options = ["all"] + sorted({item["tool_id"] for item in data["artifacts"]})
            selected_tool = st.selectbox("Tool filter", tool_options)
            rows = data["artifacts"]
            if selected_tool != "all":
                rows = [item for item in rows if item["tool_id"] == selected_tool]
            st.dataframe(rows, use_container_width=True)
            labels = [item["relative_path"] for item in rows]
            selected_artifact = st.selectbox("Artifact", labels)
            artifact = next(item for item in rows if item["relative_path"] == selected_artifact)
            preview = artifact_preview(artifact["path"])
            if preview["kind"] == "json":
                st.json(preview["content"])
            elif preview["kind"] == "image":
                st.image(preview["content"])
            elif preview["kind"] == "text":
                st.code(preview["content"])
            else:
                st.write(preview["content"])
        else:
            st.info("Artifacts will appear under .simtools/artifacts after opt-in smoke tests.")

    with profiles:
        st.dataframe(data["profiles"], use_container_width=True)


if __name__ == "__main__":
    main()
