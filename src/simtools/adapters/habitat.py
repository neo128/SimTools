"""Habitat adapter."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter


class HabitatAdapter(ManifestOnlyAdapter):
    tool_id = "habitat"

    def package_status(self) -> dict[str, bool]:
        return {
            "habitat": importlib.util.find_spec("habitat") is not None,
            "habitat_sim": importlib.util.find_spec("habitat_sim") is not None,
        }

    def check_installed(self) -> bool:
        status = self.package_status()
        return all(status.values())

    def doctor(self) -> dict[str, Any]:
        status = self.package_status()
        installed = all(status.values())
        return {
            "tool_id": self.tool_id,
            "status": "installed" if installed else "missing",
            "installed": installed,
            "package_checks": status,
            "message": (
                "Habitat and Habitat-Sim are importable. Import-only smoke can run."
                if installed
                else "Habitat is not fully installed in this environment."
            ),
            "next_steps": (
                [
                    "Run: python -m simtools run habitat --mode smoke --dry-run",
                    "Run without --dry-run for an import-only smoke test.",
                ]
                if installed
                else [
                    "Run: python -m simtools install-plan habitat",
                    "Use an isolated Habitat environment before real smoke tests.",
                ]
            ),
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": (
                    "Habitat smoke would lazy import habitat and habitat_sim only. "
                    "It does not launch a simulator, GUI, or dataset-backed scene."
                ),
                "commands": self.sample_commands(),
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "Habitat and/or Habitat-Sim are not installed.",
                "next_steps": [
                    "Run: python -m simtools install-plan habitat",
                    "Install Habitat in an isolated environment.",
                ],
            }

        try:
            habitat = importlib.import_module("habitat")
            habitat_sim = importlib.import_module("habitat_sim")
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "Habitat import-only smoke completed.",
                "modules": {
                    "habitat": getattr(habitat, "__version__", "unknown"),
                    "habitat_sim": getattr(habitat_sim, "__version__", "unknown"),
                },
            }
        except Exception as exc:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": f"Habitat import-only smoke failed: {exc}",
                "next_steps": [
                    "Check that Habitat and Habitat-Sim are installed in the same isolated environment.",
                    "Run: python -m simtools doctor habitat",
                ],
            }
