"""MolmoSpaces adapter."""

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


class MolmoSpacesAdapter(ManifestOnlyAdapter):
    tool_id = "molmospaces"

    def package_status(self) -> dict[str, bool]:
        return {
            "molmo_spaces": importlib.util.find_spec("molmo_spaces") is not None,
            "mujoco": importlib.util.find_spec("mujoco") is not None,
            "molmospaces_resources": (
                importlib.util.find_spec("molmospaces_resources") is not None
            ),
        }

    def check_installed(self) -> bool:
        return all(self.package_status().values()) or self._external_package_status()[
            "installed"
        ]

    def doctor(self) -> dict[str, Any]:
        external = self._external_package_status()
        assets = self._asset_status()
        installed = all(self.package_status().values()) or external["installed"]
        assets_ready = bool(assets["scene_exists"])
        ready = installed and assets_ready
        return {
            "tool_id": self.tool_id,
            "status": "installed" if ready else "partial" if installed else "missing",
            "installed": installed,
            "assets_ready": assets_ready,
            "package_checks": self.package_status(),
            "external_environment": external,
            "assets": assets,
            "message": (
                "MolmoSpaces packages and local iTHOR assets are available."
                if ready
                else "MolmoSpaces needs packages and fetched local assets before visual execution."
            ),
            "next_steps": (
                [
                    "Run: python -m simtools run molmospaces --mode smoke",
                    "Run: python -m simtools view molmospaces --execute --scene FloorPlan1",
                ]
                if ready
                else [
                    "Run: python -m simtools install-plan molmospaces",
                    "Install MolmoSpaces in .venv-molmospaces.",
                    "Fetch a scene with scripts/datagen/fetch_assets.py before rendering.",
                ]
            ),
            "notes": [
                "The SimTools viewer path uses MuJoCo EGL offscreen rendering.",
                "Scene XML mesh paths are resolved from the scene directory.",
            ],
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": (
                    "MolmoSpaces smoke would lazy import molmo_spaces, mujoco, "
                    "and molmospaces_resources in the active environment or .venv-molmospaces."
                ),
                "commands": self.sample_commands(),
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "MolmoSpaces, MuJoCo, and/or MolmoSpaces resources are not installed.",
                "next_steps": [
                    "Run: python -m simtools install-plan molmospaces",
                    "Install dependencies in .venv-molmospaces.",
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
                    "message": "MolmoSpaces external smoke failed.",
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "MolmoSpaces external import smoke completed.",
                "modules": json.loads(completed.stdout.splitlines()[-1]),
                "python": str(external),
                "stderr": completed.stderr,
            }

        try:
            molmo_spaces = importlib.import_module("molmo_spaces")
            mujoco = importlib.import_module("mujoco")
            resources = importlib.import_module("molmospaces_resources")
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "MolmoSpaces import smoke completed.",
                "modules": {
                    "molmo_spaces": getattr(molmo_spaces, "__version__", "unknown"),
                    "mujoco": getattr(mujoco, "__version__", "unknown"),
                    "molmospaces_resources": getattr(
                        resources, "__version__", "unknown"
                    ),
                },
            }
        except Exception as exc:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": f"MolmoSpaces import smoke failed: {exc}",
                "next_steps": [
                    "Check .venv-molmospaces package compatibility.",
                    "Run: python -m simtools doctor molmospaces",
                ],
            }

    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
        **options: Any,
    ) -> dict[str, Any]:
        scene = str(options.get("scene") or "FloorPlan1")
        width = int(options.get("width") or 640)
        height = int(options.get("height") or 480)
        artifact = ArtifactStore().path_for(
            self.tool_id, f"{self._artifact_stem(scene)}_rgb.png"
        )
        commands = [
            f"python -m simtools view molmospaces --execute --scene {scene} --width {width} --height {height}",
            (
                "MLSPACES_CACHE_DIR=$PWD/.simtools/molmospaces-cache "
                "MLSPACES_ASSETS_DIR=$PWD/.simtools/molmospaces-assets "
                "MLSPACES_FORCE_INSTALL=True .venv-molmospaces/bin/python "
                ".simtools/external/molmospaces/scripts/datagen/fetch_assets.py "
                "scene ithor 1 --split train"
            ),
            f"Open generated image: {artifact}",
        ]
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "MolmoSpaces viewer execution renders one MuJoCo EGL RGB frame.",
                "commands": commands,
                "next_steps": [
                    "Install MolmoSpaces into .venv-molmospaces.",
                    "Fetch at least one official scene into .simtools/molmospaces-assets.",
                    "Run with --execute to create the PNG artifact.",
                ],
            }
        python = self._external_python()
        if python is None and not all(self.package_status().values()):
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "MolmoSpaces is not installed in the active environment or .venv-molmospaces.",
                "commands": commands,
                "next_steps": [
                    "Run: python -m simtools install-plan molmospaces",
                    "Create .venv-molmospaces and install the source checkout.",
                ],
            }
        scene_path = self._scene_path(scene)
        if not scene_path.exists():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": f"MolmoSpaces scene asset is missing: {scene_path}",
                "commands": commands,
                "next_steps": [
                    "Fetch official scene assets before rendering.",
                    "Run the fetch_assets.py command shown in commands.",
                ],
            }
        artifact.parent.mkdir(parents=True, exist_ok=True)
        runner = str(python or sys.executable)
        env = os.environ.copy()
        env.setdefault("MUJOCO_GL", "egl")
        env.setdefault("MLSPACES_CACHE_DIR", str(repo_root() / ".simtools/molmospaces-cache"))
        env.setdefault("MLSPACES_ASSETS_DIR", str(repo_root() / ".simtools/molmospaces-assets"))
        completed = subprocess.run(
            [runner, "-c", self._render_script(scene_path, artifact, width, height)],
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
                "message": "MolmoSpaces visual render failed.",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "commands": commands,
            }
        return {
            "tool_id": self.tool_id,
            "status": "passed",
            "message": "MolmoSpaces visual render completed.",
            "scene": scene,
            "artifacts": [str(artifact)],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "commands": commands,
        }

    def _external_python(self) -> Path | None:
        candidate = repo_root() / ".venv-molmospaces" / "bin" / "python"
        return candidate if candidate.exists() else None

    def _external_package_status(self) -> dict[str, Any]:
        python = self._external_python()
        if python is None:
            return {
                "python": None,
                "installed": False,
                "package_checks": {
                    "molmo_spaces": False,
                    "mujoco": False,
                    "molmospaces_resources": False,
                },
            }
        code = (
            "import importlib.util, json; "
            "checks={name: importlib.util.find_spec(name) is not None "
            "for name in ['molmo_spaces','mujoco','molmospaces_resources']}; "
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
                    "molmo_spaces": False,
                    "mujoco": False,
                    "molmospaces_resources": False,
                },
                "error": completed.stderr,
            }
        checks = json.loads(completed.stdout)
        return {
            "python": str(python),
            "installed": all(checks.values()),
            "package_checks": checks,
        }

    def _asset_status(self) -> dict[str, Any]:
        scene = self._scene_path("FloorPlan1")
        return {
            "assets_dir": str(repo_root() / ".simtools/molmospaces-assets"),
            "cache_dir": str(repo_root() / ".simtools/molmospaces-cache"),
            "sample_scene": str(scene),
            "scene_exists": scene.exists(),
        }

    def _scene_path(self, scene: str) -> Path:
        candidate = Path(scene)
        if candidate.suffix == ".xml":
            return candidate if candidate.is_absolute() else repo_root() / candidate
        scene_id = scene.removesuffix("_physics")
        return (
            repo_root()
            / ".simtools"
            / "molmospaces-assets"
            / "scenes"
            / "ithor"
            / f"{scene_id}_physics.xml"
        )

    def _artifact_stem(self, scene: str) -> str:
        stem = Path(scene).stem if Path(scene).suffix else scene
        return stem.removesuffix("_physics").lower().replace("/", "_").replace(" ", "_")

    def _import_script(self) -> str:
        return (
            "import json, molmo_spaces, mujoco, molmospaces_resources; "
            "print(json.dumps({"
            "'molmo_spaces': getattr(molmo_spaces, '__version__', 'unknown'), "
            "'mujoco': getattr(mujoco, '__version__', 'unknown'), "
            "'molmospaces_resources': getattr(molmospaces_resources, '__version__', 'unknown')"
            "}, sort_keys=True))"
        )

    def _render_script(
        self, scene: Path, artifact: Path, width: int, height: int
    ) -> str:
        return textwrap.dedent(
            f"""
            from pathlib import Path
            import os
            import numpy as np
            from PIL import Image
            import mujoco

            scene = Path({str(scene)!r})
            out = Path({str(artifact)!r})
            old_cwd = Path.cwd()
            os.chdir(scene.parent)
            try:
                model = mujoco.MjModel.from_xml_path(scene.name)
            finally:
                os.chdir(old_cwd)
            data = mujoco.MjData(model)
            mujoco.mj_forward(model, data)
            camera = mujoco.MjvCamera()
            camera.type = mujoco.mjtCamera.mjCAMERA_FREE
            camera.lookat[:] = model.stat.center
            camera.distance = max(2.0, model.stat.extent * 0.75)
            camera.azimuth = 135
            camera.elevation = -35
            renderer = mujoco.Renderer(model, height={height}, width={width})
            try:
                renderer.update_scene(data, camera=camera)
                image = renderer.render()
                Image.fromarray(image).save(out)
                unique = len(np.unique(image.reshape(-1, 3), axis=0))
                print({{"artifact": str(out), "shape": image.shape, "min": int(image.min()), "max": int(image.max()), "mean": float(image.mean()), "unique_colors": unique}})
            finally:
                renderer.close()
            """
        )
