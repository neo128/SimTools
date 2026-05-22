"""Base adapter contracts."""

from __future__ import annotations

import importlib.util
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from simtools.core.models import ToolManifest


class SimToolAdapter(ABC):
    """Contract for simulator adapters."""

    tool_id: ClassVar[str]

    def __init__(self, manifest: ToolManifest):
        self.manifest = manifest

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """Return static metadata loaded from the manifest."""

    @abstractmethod
    def check_installed(self) -> bool:
        """Return whether the tool appears installed in the current profile."""

    @abstractmethod
    def doctor(self) -> dict[str, Any]:
        """Return diagnostic information."""

    @abstractmethod
    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        """Run or plan a minimal non-destructive smoke test."""

    @abstractmethod
    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
    ) -> dict[str, Any]:
        """Launch or plan a viewer."""

    @abstractmethod
    def sample_commands(self) -> list[str]:
        """Return reproducible manual commands."""


class ManifestOnlyAdapter(SimToolAdapter):
    """Default lightweight adapter for tools that are not fully integrated yet."""

    package_checks: ClassVar[list[str]] = []

    def metadata(self) -> dict[str, Any]:
        return self.manifest.as_metadata()

    def package_status(self) -> dict[str, bool]:
        checks = self.package_checks or self.manifest.adapter.package_checks
        return {package: importlib.util.find_spec(package) is not None for package in checks}

    def check_installed(self) -> bool:
        status = self.package_status()
        return bool(status) and all(status.values())

    def doctor(self) -> dict[str, Any]:
        installed = self.check_installed()
        return {
            "tool_id": self.tool_id,
            "status": "installed" if installed else "missing",
            "installed": installed,
            "package_checks": self.package_status(),
            "message": (
                f"{self.manifest.name} package checks passed."
                if installed
                else f"{self.manifest.name} is not fully installed in this environment."
            ),
            "next_steps": [
                f"Run: python -m simtools install-plan {self.tool_id}",
                "Use an isolated simulator-specific environment before executing install commands.",
            ],
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": f"Dry-run smoke plan for {self.manifest.name}.",
                "commands": self.sample_commands(),
            }
        return {
            "tool_id": self.tool_id,
            "status": "skipped",
            "message": (
                f"No real smoke implementation is available for {self.manifest.name} yet."
            ),
            "next_steps": [
                f"Run: python -m simtools run {self.tool_id} --mode smoke --dry-run",
                "Add a real adapter path before executing simulator-specific smoke tests.",
            ],
        }

    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
    ) -> dict[str, Any]:
        return {
            "tool_id": self.tool_id,
            "status": "planned" if dry_run or not execute else "skipped",
            "message": (
                f"Viewer launch for {self.manifest.name} is dry-run only in this adapter."
            ),
            "commands": self.sample_commands(),
            "next_steps": [
                "Install the simulator in an isolated profile.",
                f"Add a real launch path to src/simtools/adapters/{self.tool_id}.py.",
            ],
        }

    def sample_commands(self) -> list[str]:
        return [spec.command for spec in self.manifest.commands.values()]
