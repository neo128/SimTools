"""RoboCasa365 planned adapter."""

from __future__ import annotations

from simtools.adapters.planned import PlannedSimulatorAdapter


class RoboCasa365Adapter(PlannedSimulatorAdapter):
    tool_id = "robocasa365"
    install_guidance = [
        "Run: python -m simtools install-plan robocasa365 --profile conda",
        "Install RoboCasa365 and robosuite in an isolated conda environment.",
        "Download kitchen assets only after accepting the RoboCasa asset requirements.",
    ]
    smoke_guidance = (
        "RoboCasa365 smoke is currently a dry-run plan. A real smoke should first "
        "check robocasa and robosuite imports, then create a tiny non-rendering "
        "environment without downloading assets during tests."
    )
    viewer_guidance = (
        "RoboCasa365 viewer support is planned. Use official examples manually "
        "inside the isolated RoboCasa environment until SimTools has an opt-in viewer."
    )
    manual_viewer_commands = [
        "python -m simtools view robocasa365 --dry-run",
        "python -m robocasa.demos.demo_random_action",
    ]
