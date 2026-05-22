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
from simtools.core.registry import ToolRegistry


def load_dashboard_data() -> dict[str, Any]:
    registry = ToolRegistry.from_configs()
    rows = matrix_rows(registry)
    artifacts = ArtifactStore().list_artifacts()
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
        "artifacts": artifacts,
        "artifact_summary": summarize_artifacts(artifacts),
    }


def summarize_artifacts(artifacts: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for artifact in artifacts:
        counts[str(artifact["tool_id"])] += 1
    return dict(sorted(counts.items()))


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

    overview, matrix, detail, doctor, artifacts, profiles = st.tabs(
        [
            "Overview",
            "Tool Matrix",
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

    with matrix:
        st.dataframe(data["matrix"], use_container_width=True)

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
