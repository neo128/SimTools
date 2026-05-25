"""ManiSkill adapter."""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter
from simtools.core.artifact_store import ArtifactStore


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
                "The SimTools viewer path renders a short PickCube-v1 MP4 artifact.",
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
        env_id = str(options.get("scene") or "PickCube-v1")
        if env_id == "FloorPlan1":
            env_id = "PickCube-v1"
        artifact_dir = ArtifactStore().tool_dir(self.tool_id) / "videos"
        command = (
            f"python -m simtools view maniskill --execute --scene {env_id}"
        )
        demo_command = [
            sys.executable,
            "-m",
            "mani_skill.examples.demo_random_action",
            "-e",
            env_id,
            "--render-mode",
            "rgb_array",
            "--record-dir",
            str(artifact_dir),
            "--quiet",
        ]
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "ManiSkill viewer execution will render a short MP4 artifact.",
                "commands": [
                    command,
                    " ".join(demo_command),
                    f"python -m mani_skill.examples.demo_random_action -e {env_id} --render-mode human",
                ],
                "next_steps": [
                    "Install ManiSkill in an isolated environment.",
                    "Run with --execute to create a visual MP4 artifact.",
                ],
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
        before = {
            path.resolve()
            for path in artifact_dir.rglob("*")
            if path.is_file()
        } if artifact_dir.exists() else set()
        artifact_dir.mkdir(parents=True, exist_ok=True)
        started_at = datetime.now(timezone.utc).isoformat()
        try:
            completed = subprocess.run(
                demo_command,
                check=False,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": "ManiSkill visual render timed out.",
                "started_at": started_at,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "commands": [" ".join(demo_command)],
            }
        after = [
            path.resolve()
            for path in artifact_dir.rglob("*")
            if path.is_file()
        ]
        new_artifacts = sorted(str(path) for path in after if path not in before)
        if not new_artifacts:
            new_artifacts = sorted(str(path) for path in after if path.suffix == ".mp4")
        if completed.returncode != 0:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": "ManiSkill visual render failed.",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "commands": [" ".join(demo_command)],
            }
        return {
            "tool_id": self.tool_id,
            "status": "passed",
            "message": "ManiSkill visual render completed.",
            "env_id": env_id,
            "artifacts": new_artifacts,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "commands": [" ".join(demo_command)],
        }
