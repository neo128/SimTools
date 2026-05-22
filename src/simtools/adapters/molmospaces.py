"""MolmoSpaces planned adapter."""

from __future__ import annotations

from simtools.adapters.planned import PlannedSimulatorAdapter


class MolmoSpacesAdapter(PlannedSimulatorAdapter):
    tool_id = "molmospaces"
    install_guidance = [
        "Run: python -m simtools install-plan molmospaces --profile conda",
        "Use a dedicated MolmoSpaces checkout and Python 3.11 environment.",
        "Choose asset/cache directories explicitly before running commands that can download assets.",
    ]
    smoke_guidance = (
        "MolmoSpaces smoke is currently dry-run only. A real smoke should verify "
        "the molmo_spaces and mujoco imports before any data generation or asset download."
    )
    viewer_guidance = (
        "MolmoSpaces viewer support is planned. Official debug viewer commands can "
        "download assets, so SimTools keeps them as manual dry-run guidance."
    )
    manual_viewer_commands = [
        "python -m simtools view molmospaces --dry-run",
        "python scripts/datagen/run_pipeline.py --viewer --seed 3",
        "mjpython scripts/datagen/run_pipeline.py --viewer --seed 3",
    ]
