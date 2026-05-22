"""Helpers for planned simulator integrations."""

from __future__ import annotations

from typing import Any, ClassVar

from simtools.adapters.base import ManifestOnlyAdapter


class PlannedSimulatorAdapter(ManifestOnlyAdapter):
    """Adapter for tools with declarative plans but no real execution path yet."""

    install_guidance: ClassVar[list[str]] = []
    smoke_guidance: ClassVar[str] = (
        "Smoke execution is planned but not implemented for this simulator yet."
    )
    viewer_guidance: ClassVar[str] = (
        "Viewer execution is planned but not implemented for this simulator yet."
    )
    manual_viewer_commands: ClassVar[list[str]] = []

    def doctor(self) -> dict[str, Any]:
        package_checks = self.package_status()
        installed = bool(package_checks) and all(package_checks.values())
        partial = bool(package_checks) and any(package_checks.values()) and not installed
        status = "installed" if installed else "partial" if partial else "missing"
        return {
            "tool_id": self.tool_id,
            "status": status,
            "installed": installed,
            "package_checks": package_checks,
            "message": (
                f"{self.manifest.name} package checks passed."
                if installed
                else f"{self.manifest.name} is not ready for real execution in this environment."
            ),
            "next_steps": self.install_guidance
            or [
                f"Run: python -m simtools install-plan {self.tool_id}",
                "Use an isolated simulator-specific environment.",
            ],
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": self.smoke_guidance,
                "commands": self.sample_commands(),
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": f"{self.manifest.name} is not installed.",
                "next_steps": self.install_guidance
                or [
                    f"Run: python -m simtools install-plan {self.tool_id}",
                    "Install the simulator in an isolated environment.",
                ],
            }
        return {
            "tool_id": self.tool_id,
            "status": "skipped",
            "message": (
                f"{self.manifest.name} package checks passed, but SimTools does "
                "not have a non-destructive real smoke implementation for it yet."
            ),
            "next_steps": [
                f"Run: python -m simtools run {self.tool_id} --mode smoke --dry-run",
                "Add a dedicated opt-in real smoke before running simulator workloads.",
            ],
        }

    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
        **options: Any,
    ) -> dict[str, Any]:
        commands = self.manual_viewer_commands or self.sample_commands()
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": self.viewer_guidance,
                "commands": commands,
                "next_steps": self.install_guidance
                or [
                    f"Run: python -m simtools install-plan {self.tool_id}",
                    "Use the simulator's official viewer manually until SimTools wires a real viewer.",
                ],
            }
        return {
            "tool_id": self.tool_id,
            "status": "skipped",
            "message": (
                f"{self.manifest.name} viewer execution is not implemented in SimTools yet."
            ),
            "commands": commands,
            "next_steps": [
                "Use --dry-run to print the current manual viewer plan.",
                "Keep GUI execution opt-in and outside base tests.",
            ],
        }
