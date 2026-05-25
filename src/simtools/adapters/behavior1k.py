"""BEHAVIOR-1K adapter."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter
from simtools.core.config_loader import repo_root


class Behavior1KAdapter(ManifestOnlyAdapter):
    tool_id = "behavior1k"

    def package_status(self) -> dict[str, bool]:
        return {
            "bddl": importlib.util.find_spec("bddl") is not None,
            "omnigibson": importlib.util.find_spec("omnigibson") is not None,
            "isaacsim": importlib.util.find_spec("isaacsim") is not None,
        }

    def check_installed(self) -> bool:
        return all(self.package_status().values()) or self._external_package_status()[
            "installed"
        ]

    def doctor(self) -> dict[str, Any]:
        external = self._external_package_status()
        dataset = self._dataset_status()
        installed = all(self.package_status().values()) or external["installed"]
        status = (
            "blocked"
            if installed and not dataset["dataset_ready"]
            else "installed"
            if installed
            else "missing"
        )
        return {
            "tool_id": self.tool_id,
            "status": status,
            "installed": installed,
            "package_checks": self.package_status(),
            "external_environment": external,
            "dataset": dataset,
            "message": (
                "BEHAVIOR-1K package-level dependencies are present, but task scenes are blocked by the licensed dataset."
                if installed and not dataset["dataset_ready"]
                else "BEHAVIOR-1K task dependencies appear installed."
                if installed
                else "BEHAVIOR-1K dependencies are not installed."
            ),
            "next_steps": [
                "Run: python -m simtools doctor omnigibson",
                "Personally accept the BEHAVIOR Data Bundle EULA before downloading dataset assets.",
                "After data is present, run an OmniGibson task/viewer command.",
            ],
            "notes": [
                "BEHAVIOR-1K uses OmniGibson for visualization.",
                "SimTools will not auto-accept the dataset EULA.",
            ],
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": (
                    "BEHAVIOR-1K smoke would verify package discovery and "
                    "distribution metadata in .venv-omnigibson without "
                    "initializing CUDA-bound OmniGibson modules."
                ),
                "commands": self.sample_commands(),
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "BDDL, OmniGibson, and/or Isaac Sim are not installed.",
                "next_steps": [
                    "Run: python -m simtools install-plan behavior1k",
                    "Use .venv-omnigibson or an equivalent isolated BEHAVIOR environment.",
                ],
            }
        dataset = self._dataset_status()
        viewer_status = (
            "delegated_to_omnigibson"
            if dataset["dataset_ready"]
            else "blocked_until_dataset_eula_is_accepted"
        )
        python = self._external_python()
        if python and not all(self.package_status().values()):
            completed = subprocess.run(
                [str(python), "-c", self._import_script()],
                check=False,
                capture_output=True,
                text=True,
                timeout=240,
                cwd=repo_root(),
                env=self._external_env(),
            )
            if completed.returncode != 0:
                return {
                    "tool_id": self.tool_id,
                    "status": "failed",
                    "message": "BEHAVIOR-1K external import smoke failed.",
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "BEHAVIOR-1K package-level smoke completed.",
                "modules": json.loads(completed.stdout.splitlines()[-1]),
                "python": str(python),
                "dataset": dataset,
                "viewer_status": viewer_status,
            }
        return {
            "tool_id": self.tool_id,
            "status": "passed",
            "message": "BEHAVIOR-1K package checks passed in the active environment.",
            "package_checks": self.package_status(),
            "dataset": dataset,
            "viewer_status": viewer_status,
        }

    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
        **options: Any,
    ) -> dict[str, Any]:
        commands = self.sample_commands()
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "BEHAVIOR-1K viewer is routed through OmniGibson after dataset setup.",
                "commands": commands,
                "next_steps": [
                    "Run: python -m simtools doctor behavior1k",
                    "Install the licensed BEHAVIOR/OmniGibson dataset only after personal EULA acceptance.",
                    "Use python -m simtools view omnigibson --execute for the runtime viewer.",
                ],
            }
        dataset = self._dataset_status()
        if not dataset["dataset_ready"]:
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "BEHAVIOR-1K viewer remains blocked until the licensed dataset is installed.",
                "dataset": dataset,
                "commands": commands,
                "next_steps": [
                    "Run PYTHONNOUSERSITE=1 CONDA_PREFIX=\"$PWD/.venv-omnigibson\" PATH=\"$PWD/.venv-omnigibson/bin:$PATH\" .venv-omnigibson/bin/python -s -m omnigibson.download_datasets yourself.",
                    "Respond to the BEHAVIOR Data Bundle EULA only if you personally agree.",
                ],
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "BEHAVIOR-1K dataset is present, but package-level dependencies are missing.",
                "dataset": dataset,
                "commands": commands,
                "next_steps": [
                    "Run: python -m simtools doctor behavior1k",
                    "Run: python -m simtools install-plan behavior1k",
                ],
            }
        return {
            "tool_id": self.tool_id,
            "status": "passed",
            "message": (
                "BEHAVIOR-1K visualization is delegated to OmniGibson; "
                "the local dataset and package-level dependencies are ready."
            ),
            "viewer_status": "delegated_to_omnigibson",
            "dataset": dataset,
            "commands": commands,
            "next_steps": [
                "Run: python -m simtools view omnigibson --execute",
                "Use the OmniGibson viewer as the BEHAVIOR-1K task visualization surface.",
            ],
        }

    def _external_python(self) -> Path | None:
        candidate = repo_root() / ".venv-omnigibson" / "bin" / "python"
        return candidate if candidate.exists() else None

    def _external_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PATH"] = (
            f"{repo_root() / '.venv-omnigibson' / 'bin'}:{env.get('PATH', '')}"
        )
        env["CONDA_PREFIX"] = str(repo_root() / ".venv-omnigibson")
        env["PYTHONNOUSERSITE"] = "1"
        env["OMNI_KIT_ACCEPT_EULA"] = "YES"
        return env

    def _external_package_status(self) -> dict[str, Any]:
        python = self._external_python()
        if python is None:
            return {
                "python": None,
                "installed": False,
                "package_checks": {
                    "bddl": False,
                    "omnigibson": False,
                    "isaacsim": False,
                },
            }
        code = (
            "import importlib.util, json; "
            "checks={name: importlib.util.find_spec(name) is not None "
            "for name in ['bddl','omnigibson','isaacsim']}; "
            "print(json.dumps(checks, sort_keys=True))"
        )
        completed = subprocess.run(
            [str(python), "-c", code],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=repo_root(),
            env=self._external_env(),
        )
        if completed.returncode != 0:
            return {
                "python": str(python),
                "installed": False,
                "package_checks": {
                    "bddl": False,
                    "omnigibson": False,
                    "isaacsim": False,
                },
                "error": completed.stderr,
            }
        checks = json.loads(completed.stdout)
        return {
            "python": str(python),
            "installed": all(checks.values()),
            "package_checks": checks,
        }

    def _dataset_status(self) -> dict[str, Any]:
        data_root = (
            repo_root()
            / ".venv-omnigibson"
            / "lib"
            / "python3.10"
            / "site-packages"
            / "omnigibson"
            / "data"
        )
        scenes = data_root / "og_dataset" / "scenes"
        assets = data_root / "assets"
        return {
            "data_root": str(data_root),
            "scenes_path": str(scenes),
            "assets_path": str(assets),
            "scenes_exists": scenes.exists(),
            "assets_exists": assets.exists(),
            "dataset_ready": scenes.exists() and assets.exists(),
            "requires_eula": not scenes.exists(),
        }

    def _import_script(self) -> str:
        return (
            "import importlib.metadata as metadata\n"
            "import importlib.util\n"
            "import json\n"
            "modules = ['bddl', 'omnigibson', 'isaacsim']\n"
            "missing = [name for name in modules if importlib.util.find_spec(name) is None]\n"
            "if missing:\n"
            "    raise SystemExit('missing packages: ' + ', '.join(missing))\n"
            "versions = {}\n"
            "for distribution in ['bddl', 'omnigibson', 'isaacsim']:\n"
            "    try:\n"
            "        versions[distribution] = metadata.version(distribution)\n"
            "    except metadata.PackageNotFoundError:\n"
            "        versions[distribution] = 'unknown'\n"
            "print(json.dumps(versions, sort_keys=True))\n"
        )
