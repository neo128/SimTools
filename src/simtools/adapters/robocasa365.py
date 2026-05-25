"""RoboCasa365 adapter."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter
from simtools.core.artifact_store import ArtifactStore
from simtools.core.config_loader import repo_root


class RoboCasa365Adapter(ManifestOnlyAdapter):
    tool_id = "robocasa365"

    def package_status(self) -> dict[str, bool]:
        return {
            "robocasa": importlib.util.find_spec("robocasa") is not None,
            "robosuite": importlib.util.find_spec("robosuite") is not None,
            "mujoco": importlib.util.find_spec("mujoco") is not None,
        }

    def check_installed(self) -> bool:
        return all(self.package_status().values()) or self._external_package_status()["installed"]

    def doctor(self) -> dict[str, Any]:
        external = self._external_package_status()
        installed = all(self.package_status().values()) or external["installed"]
        return {
            "tool_id": self.tool_id,
            "status": "installed" if installed else "missing",
            "installed": installed,
            "package_checks": self.package_status(),
            "external_environment": external,
            "message": (
                "RoboCasa365, robosuite, and MuJoCo are available."
                if installed
                else "RoboCasa365 is not installed in this environment."
            ),
            "next_steps": (
                [
                    "Run: python -m simtools run robocasa365 --mode smoke",
                    "Run: python -m simtools view robocasa365 --execute --scene Kitchen",
                ]
                if installed
                else [
                    "Run: python -m simtools install-plan robocasa365",
                    "Install RoboCasa365 in .venv-robocasa365.",
                ]
            ),
            "notes": [
                "Kitchen assets are required for the real visual path.",
                "The SimTools viewer path uses MuJoCo EGL offscreen rendering.",
            ],
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": (
                    "RoboCasa365 smoke would lazy import robocasa, robosuite, "
                    "and mujoco in the active environment or .venv-robocasa365."
                ),
                "commands": self.sample_commands(),
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "RoboCasa365, robosuite, and/or MuJoCo are not installed.",
                "next_steps": [
                    "Run: python -m simtools install-plan robocasa365",
                    "Install dependencies in .venv-robocasa365.",
                ],
            }

        external = self._external_python()
        if external and not all(self.package_status().values()):
            completed = subprocess.run(
                [str(external), "-c", self._import_script()],
                check=False,
                capture_output=True,
                text=True,
                timeout=90,
                cwd=repo_root(),
            )
            if completed.returncode != 0:
                return {
                    "tool_id": self.tool_id,
                    "status": "failed",
                    "message": "RoboCasa365 external smoke failed.",
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "RoboCasa365 external import smoke completed.",
                "modules": json.loads(completed.stdout.splitlines()[-1]),
                "python": str(external),
                "stderr": completed.stderr,
            }

        try:
            robocasa = importlib.import_module("robocasa")
            robosuite = importlib.import_module("robosuite")
            mujoco = importlib.import_module("mujoco")
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "RoboCasa365 import smoke completed.",
                "modules": {
                    "robocasa": getattr(robocasa, "__version__", "unknown"),
                    "robosuite": getattr(robosuite, "__version__", "unknown"),
                    "mujoco": getattr(mujoco, "__version__", "unknown"),
                },
            }
        except Exception as exc:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": f"RoboCasa365 import smoke failed: {exc}",
                "next_steps": [
                    "Check .venv-robocasa365 package compatibility.",
                    "Run: python -m simtools doctor robocasa365",
                ],
            }

    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
        **options: Any,
    ) -> dict[str, Any]:
        scene = str(options.get("scene") or "Kitchen")
        width = int(options.get("width") or 640)
        height = int(options.get("height") or 480)
        artifact = ArtifactStore().path_for(self.tool_id, f"{scene.lower()}_rgb.png")
        commands = [
            f"python -m simtools view robocasa365 --execute --scene {scene} --width {width} --height {height}",
            "printf 'y\\n' | .venv-robocasa365/bin/python .simtools/external/robocasa/robocasa/scripts/download_kitchen_assets.py --type all",
            f"Open generated image: {artifact}",
        ]
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "RoboCasa365 viewer execution renders one MuJoCo EGL RGB frame.",
                "commands": commands,
                "next_steps": [
                    "Install RoboCasa365 and robosuite into .venv-robocasa365.",
                    "Download official kitchen assets.",
                    "Run with --execute to create the PNG artifact.",
                ],
            }
        python = self._external_python()
        if python is None and not all(self.package_status().values()):
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "RoboCasa365 is not installed in the active environment or .venv-robocasa365.",
                "commands": commands,
                "next_steps": [
                    "Run: python -m simtools install-plan robocasa365",
                    "Create .venv-robocasa365 and install robosuite plus robocasa.",
                ],
            }
        artifact.parent.mkdir(parents=True, exist_ok=True)
        runner = str(python or sys.executable)
        env = os.environ.copy()
        env.setdefault("MUJOCO_GL", "egl")
        completed = subprocess.run(
            [runner, "-c", self._render_script(scene, artifact, width, height)],
            check=False,
            capture_output=True,
            text=True,
            timeout=240,
            cwd=repo_root(),
            env=env,
        )
        if completed.returncode != 0:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": "RoboCasa365 visual render failed.",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "commands": commands,
            }
        return {
            "tool_id": self.tool_id,
            "status": "passed",
            "message": "RoboCasa365 visual render completed.",
            "scene": scene,
            "artifacts": [str(artifact)],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "commands": commands,
        }

    def _external_python(self) -> Path | None:
        candidate = repo_root() / ".venv-robocasa365" / "bin" / "python"
        return candidate if candidate.exists() else None

    def _external_package_status(self) -> dict[str, Any]:
        python = self._external_python()
        if python is None:
            return {
                "python": None,
                "installed": False,
                "package_checks": {
                    "robocasa": False,
                    "robosuite": False,
                    "mujoco": False,
                },
            }
        code = (
            "import importlib.util, json; "
            "checks={name: importlib.util.find_spec(name) is not None "
            "for name in ['robocasa','robosuite','mujoco']}; "
            "print(json.dumps(checks, sort_keys=True))"
        )
        completed = subprocess.run(
            [str(python), "-c", code],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=repo_root(),
        )
        if completed.returncode != 0:
            return {
                "python": str(python),
                "installed": False,
                "package_checks": {
                    "robocasa": False,
                    "robosuite": False,
                    "mujoco": False,
                },
                "error": completed.stderr,
            }
        checks = json.loads(completed.stdout)
        return {
            "python": str(python),
            "installed": all(checks.values()),
            "package_checks": checks,
        }

    def _import_script(self) -> str:
        return (
            "import json, robocasa, robosuite, mujoco; "
            "print(json.dumps({"
            "'robocasa': getattr(robocasa, '__version__', 'unknown'), "
            "'robosuite': getattr(robosuite, '__version__', 'unknown'), "
            "'mujoco': getattr(mujoco, '__version__', 'unknown')"
            "}, sort_keys=True))"
        )

    def _render_script(self, scene: str, artifact: Path, width: int, height: int) -> str:
        return textwrap.dedent(
            f"""
            from pathlib import Path
            import numpy as np
            from PIL import Image
            import robocasa  # noqa: F401
            import robosuite
            from robosuite.controllers import load_composite_controller_config

            out = Path({str(artifact)!r})
            robot = "PandaOmron"
            env = robosuite.make(
                env_name={scene!r},
                robots=robot,
                controller_configs=load_composite_controller_config(robot=robot),
                has_renderer=False,
                has_offscreen_renderer=True,
                render_camera="robot0_agentview_center",
                ignore_done=True,
                use_camera_obs=True,
                camera_names="robot0_agentview_center",
                camera_heights={height},
                camera_widths={width},
                control_freq=20,
            )
            obs = env.reset()
            image = obs["robot0_agentview_center_image"]
            if image.dtype != np.uint8:
                image = (np.clip(image, 0, 1) * 255).astype("uint8")
            Image.fromarray(np.flipud(image)).save(out)
            env.close()
            print(out)
            """
        )
