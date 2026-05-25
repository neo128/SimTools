"""Habitat adapter."""

from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter
from simtools.core.artifact_store import ArtifactStore
from simtools.core.config_loader import repo_root


class HabitatAdapter(ManifestOnlyAdapter):
    tool_id = "habitat"

    def package_status(self) -> dict[str, bool]:
        return {
            "habitat": importlib.util.find_spec("habitat") is not None,
            "habitat_sim": importlib.util.find_spec("habitat_sim") is not None,
        }

    def check_installed(self) -> bool:
        status = self.package_status()
        return all(status.values()) or self._external_package_status()["installed"]

    def doctor(self) -> dict[str, Any]:
        status = self.package_status()
        external = self._external_package_status()
        installed = all(status.values()) or external["installed"]
        return {
            "tool_id": self.tool_id,
            "status": "installed" if installed else "missing",
            "installed": installed,
            "package_checks": status,
            "external_environment": external,
            "message": (
                "Habitat and Habitat-Sim are available. Smoke and visual render can run."
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
                    "Habitat smoke would lazy import habitat and habitat_sim in the "
                    "active environment or probe the dedicated .venv-habitat profile."
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

        external = self._external_python()
        if external and not all(self.package_status().values()):
            code = (
                "import habitat, habitat_sim; "
                "print(getattr(habitat, '__version__', 'unknown')); "
                "print(getattr(habitat_sim, '__version__', 'unknown'))"
            )
            completed = subprocess.run(
                [str(external), "-c", code],
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if completed.returncode != 0:
                return {
                    "tool_id": self.tool_id,
                    "status": "failed",
                    "message": "Habitat external smoke failed.",
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                    "next_steps": [
                        "Check .venv-habitat package compatibility.",
                        "Run: python -m simtools doctor habitat",
                    ],
                }
            versions = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "Habitat external import-only smoke completed.",
                "modules": {
                    "habitat": versions[-2] if len(versions) >= 2 else "unknown",
                    "habitat_sim": versions[-1] if versions else "unknown",
                },
                "python": str(external),
                "stderr": completed.stderr,
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

    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
        **options: Any,
    ) -> dict[str, Any]:
        scene_name = str(options.get("scene") or "skokloster-castle")
        width = int(options.get("width") or 640)
        height = int(options.get("height") or 480)
        artifact = self._artifact_path(scene_name)
        commands = [
            f"python -m simtools view habitat --execute --scene {scene_name} --width {width} --height {height}",
            "PATH=\"$PWD/.venv-habitat/bin:$PATH\" .venv-habitat/bin/python -m habitat_sim.utils.datasets_download --uids habitat_test_scenes --data-path .simtools/habitat-data --no-replace",
            f"Open generated image: {artifact}",
        ]
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": (
                    "Habitat viewer execution renders one RGB frame from an official "
                    "Habitat test scene into a repository-local artifact."
                ),
                "commands": commands,
                "next_steps": [
                    "Run: python -m simtools install-plan habitat",
                    "Install Habitat and Habitat-Sim in .venv-habitat.",
                    "Download habitat_test_scenes into .simtools/habitat-data.",
                    "Run with --execute to render the PNG artifact.",
                ],
            }
        python = self._external_python()
        if python is None and not all(self.package_status().values()):
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "Habitat is not installed in the active environment or .venv-habitat.",
                "commands": commands,
                "next_steps": [
                    "Run: python -m simtools install-plan habitat",
                    "Create .venv-habitat and install habitat-sim plus habitat-lab.",
                ],
            }
        scene_path = self._scene_path(scene_name)
        if not scene_path.exists() or scene_path.stat().st_size < 1024:
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": f"Habitat scene asset is missing or incomplete: {scene_path}",
                "commands": commands,
                "next_steps": [
                    "Install git-lfs inside .venv-habitat if needed.",
                    "Run the habitat_test_scenes download command shown in commands.",
                ],
            }
        artifact.parent.mkdir(parents=True, exist_ok=True)
        runner = str(python or sys.executable)
        completed = subprocess.run(
            [runner, "-c", self._render_script(scene_path, artifact, width, height)],
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
            cwd=repo_root(),
        )
        if completed.returncode != 0:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": "Habitat visual render failed.",
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "commands": commands,
            }
        return {
            "tool_id": self.tool_id,
            "status": "passed",
            "message": "Habitat visual render completed.",
            "scene": str(scene_path),
            "artifacts": [str(artifact)],
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "commands": commands,
        }

    def _external_python(self) -> Path | None:
        candidate = repo_root() / ".venv-habitat" / "bin" / "python"
        return candidate if candidate.exists() else None

    def _external_package_status(self) -> dict[str, Any]:
        python = self._external_python()
        if python is None:
            return {
                "python": None,
                "installed": False,
                "package_checks": {"habitat": False, "habitat_sim": False},
            }
        code = (
            "import importlib.util, json; "
            "checks={name: importlib.util.find_spec(name) is not None "
            "for name in ['habitat','habitat_sim']}; "
            "print(json.dumps(checks, sort_keys=True))"
        )
        completed = subprocess.run(
            [str(python), "-c", code],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if completed.returncode != 0:
            return {
                "python": str(python),
                "installed": False,
                "package_checks": {"habitat": False, "habitat_sim": False},
                "error": completed.stderr,
            }
        import json

        checks = json.loads(completed.stdout)
        return {
            "python": str(python),
            "installed": all(checks.values()),
            "package_checks": checks,
        }

    def _scene_path(self, scene_name: str) -> Path:
        root = repo_root() / ".simtools" / "habitat-data" / "scene_datasets" / "habitat-test-scenes"
        path = Path(scene_name)
        if path.suffix:
            return path if path.is_absolute() else (repo_root() / path).resolve()
        normalized = scene_name.replace(".glb", "")
        return (root / f"{normalized}.glb").resolve()

    def _artifact_path(self, scene_name: str) -> Path:
        normalized = Path(scene_name).stem.replace(" ", "_").replace("/", "_")
        return ArtifactStore().path_for(self.tool_id, f"{normalized}_rgb.png")

    def _render_script(self, scene_path: Path, artifact: Path, width: int, height: int) -> str:
        return textwrap.dedent(
            f"""
            from pathlib import Path
            import numpy as np
            from PIL import Image
            import habitat_sim

            scene = Path({str(scene_path)!r})
            out = Path({str(artifact)!r})

            sim_cfg = habitat_sim.SimulatorConfiguration()
            sim_cfg.scene_id = str(scene)
            sim_cfg.enable_physics = False

            sensor_spec = habitat_sim.CameraSensorSpec()
            sensor_spec.uuid = "color_sensor"
            sensor_spec.sensor_type = habitat_sim.SensorType.COLOR
            sensor_spec.resolution = [{height}, {width}]
            sensor_spec.position = [0.0, 1.5, 0.0]

            agent_cfg = habitat_sim.agent.AgentConfiguration()
            agent_cfg.sensor_specifications = [sensor_spec]

            cfg = habitat_sim.Configuration(sim_cfg, [agent_cfg])
            sim = habitat_sim.Simulator(cfg)
            observations = sim.get_sensor_observations()
            rgb = observations["color_sensor"][:, :, :3]
            Image.fromarray(np.asarray(rgb)).save(out)
            sim.close()
            print(out)
            """
        )
