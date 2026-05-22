"""OmniGibson planned adapter."""

from __future__ import annotations

from simtools.adapters.planned import PlannedSimulatorAdapter


class OmniGibsonAdapter(PlannedSimulatorAdapter):
    tool_id = "omnigibson"
    install_guidance = [
        "Run: python -m simtools install-plan omnigibson --profile source",
        "Use the BEHAVIOR/OmniGibson setup flow in an isolated environment.",
        "Confirm NVIDIA driver, Isaac Sim, display/headless mode, and asset paths manually.",
    ]
    smoke_guidance = (
        "OmniGibson smoke is dry-run only until a safe, opt-in Isaac/Omniverse "
        "startup check is implemented. Base tests must never import Omniverse."
    )
    viewer_guidance = (
        "OmniGibson viewer launch is planned. Official examples can start Isaac "
        "Sim and open a GUI, so SimTools prints commands instead of executing them."
    )
    manual_viewer_commands = [
        "python -m simtools view omnigibson --dry-run",
        "python -m omnigibson.examples.robots.robot_control_example --quickstart",
        "python -m omnigibson.examples.scenes.scene_selector",
    ]
