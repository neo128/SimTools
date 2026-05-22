"""Streamlit dashboard for SimTools.

This module intentionally avoids importing Streamlit at module import time so it
can be imported in base tests without the dashboard extra installed.
"""

from __future__ import annotations

from collections import Counter
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
        "artifacts": ArtifactStore().list_artifacts(),
    }


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
            st.dataframe(data["artifacts"], use_container_width=True)
        else:
            st.info("Artifacts will appear under .simtools/artifacts after opt-in smoke tests.")

    with profiles:
        st.dataframe(data["profiles"], use_container_width=True)


if __name__ == "__main__":
    main()
