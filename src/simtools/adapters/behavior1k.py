"""BEHAVIOR-1K planned adapter."""

from __future__ import annotations

from simtools.adapters.planned import PlannedSimulatorAdapter


class Behavior1KAdapter(PlannedSimulatorAdapter):
    tool_id = "behavior1k"
    install_guidance = [
        "Run: python -m simtools install-plan behavior1k --profile source",
        "Use the official BEHAVIOR-1K setup script in an isolated environment.",
        "Accept Isaac Sim and dataset licenses explicitly before any dataset download.",
    ]
    smoke_guidance = (
        "BEHAVIOR-1K smoke is dry-run only. A real smoke should check bddl and "
        "omnigibson package availability before any dataset-backed task is loaded."
    )
    viewer_guidance = (
        "BEHAVIOR-1K viewer support is planned through OmniGibson. SimTools keeps "
        "the command dry-run because real execution can launch Isaac Sim and use large assets."
    )
    manual_viewer_commands = [
        "python -m simtools view behavior1k --dry-run",
        "python -m omnigibson.examples.robots.robot_control_example --quickstart",
        "python -m omnigibson.examples.scenes.scene_selector",
    ]
