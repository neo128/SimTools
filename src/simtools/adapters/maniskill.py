"""ManiSkill adapter."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter


class ManiSkillAdapter(ManifestOnlyAdapter):
    tool_id = "maniskill"

    def package_status(self) -> dict[str, bool]:
        return {"mani_skill": importlib.util.find_spec("mani_skill") is not None}

    def check_installed(self) -> bool:
        return all(self.package_status().values())

    def doctor(self) -> dict[str, Any]:
        installed = self.check_installed()
        return {
            "tool_id": self.tool_id,
            "status": "installed" if installed else "missing",
            "installed": installed,
            "package_checks": self.package_status(),
            "message": (
                "ManiSkill is importable. Package-only smoke can run."
                if installed
                else "ManiSkill is not installed in this environment."
            ),
            "next_steps": (
                [
                    "Run: python -m simtools run maniskill --mode smoke --dry-run",
                    "Run without --dry-run for a package-only smoke test.",
                ]
                if installed
                else [
                    "Run: python -m simtools install-plan maniskill",
                    "Install ManiSkill in an isolated environment before real smoke tests.",
                ]
            ),
            "notes": [
                "Rendering may require Vulkan and a compatible GPU driver.",
                "Assets and demonstrations should remain opt-in.",
            ],
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": (
                    "ManiSkill smoke would lazy import mani_skill only. It does "
                    "not create an environment, render frames, or download assets."
                ),
                "commands": self.sample_commands(),
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "ManiSkill is not installed.",
                "next_steps": [
                    "Run: python -m simtools install-plan maniskill",
                    "Install ManiSkill in an isolated environment.",
                ],
            }

        try:
            mani_skill = importlib.import_module("mani_skill")
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "ManiSkill package-only smoke completed.",
                "modules": {
                    "mani_skill": getattr(mani_skill, "__version__", "unknown"),
                },
            }
        except Exception as exc:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": f"ManiSkill package-only smoke failed: {exc}",
                "next_steps": [
                    "Check that ManiSkill is installed in the active isolated environment.",
                    "Run: python -m simtools doctor maniskill",
                ],
            }

    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
        **options: Any,
    ) -> dict[str, Any]:
        command = "python -m simtools view maniskill --execute"
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "ManiSkill real viewer execution is not wired yet.",
                "commands": [
                    command,
                    "python -m mani_skill.examples.demo_random_action -e PickCube-v1",
                ],
                "next_steps": [
                    "Install ManiSkill in an isolated environment.",
                    "Use the official demo_random_action command for manual validation.",
                    "Add an opt-in SimTools viewer adapter after Vulkan/rendering is verified.",
                ],
            }
        return {
            "tool_id": self.tool_id,
            "status": "skipped",
            "message": "ManiSkill viewer execution is not implemented in SimTools yet.",
            "commands": [command],
            "next_steps": [
                "Run with --dry-run for the current manual validation commands.",
                "Keep GUI/rendering checks opt-in and outside base tests.",
            ],
        }
