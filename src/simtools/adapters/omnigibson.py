"""OmniGibson adapter."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter
from simtools.core.config_loader import repo_root


class OmniGibsonAdapter(ManifestOnlyAdapter):
    tool_id = "omnigibson"

    def package_status(self) -> dict[str, bool]:
        return {
            "omnigibson": importlib.util.find_spec("omnigibson") is not None,
            "isaacsim": importlib.util.find_spec("isaacsim") is not None,
            "omni": importlib.util.find_spec("omni") is not None,
            "bddl": importlib.util.find_spec("bddl") is not None,
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
            "partial"
            if installed and not dataset["dataset_ready"]
            else "installed"
            if installed
            else "missing"
        )
        return {
            "tool_id": self.tool_id,
            "status": status,
            "installed": installed,
            "viewer_ready": installed and dataset["dataset_ready"],
            "package_checks": self.package_status(),
            "external_environment": external,
            "dataset": dataset,
            "message": (
                "OmniGibson and Isaac Sim packages are discoverable, but the local dataset is missing."
                if installed and not dataset["dataset_ready"]
                else "OmniGibson runtime appears installed."
                if installed
                else "OmniGibson is not installed in this environment."
            ),
            "next_steps": (
                [
                    "Run: python -m simtools run omnigibson --mode smoke",
                    "Only run dataset download after personally accepting the BEHAVIOR Data Bundle EULA.",
                    "After data is present, run: python -m simtools view omnigibson --execute",
                ]
                if installed
                else [
                    "Run: python -m simtools install-plan omnigibson",
                    "Install OmniGibson and Isaac Sim in .venv-omnigibson.",
                ]
            ),
            "notes": [
                "Isaac Sim startup was manually verified on 2026-05-22.",
                "Dataset download requires an explicit EULA response by the user.",
                "The current host reports a low inotify watch limit during Isaac startup.",
            ],
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": (
                    "OmniGibson smoke would verify package discovery and "
                    "distribution metadata in .venv-omnigibson without "
                    "initializing CUDA-bound OmniGibson modules."
                ),
                "commands": self.sample_commands(),
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "OmniGibson, Isaac Sim, and/or BDDL are not installed.",
                "next_steps": [
                    "Run: python -m simtools install-plan omnigibson",
                    "Create .venv-omnigibson and install the runtime there.",
                ],
            }
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
                    "message": "OmniGibson external import smoke failed.",
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "OmniGibson external package metadata smoke completed.",
                "modules": json.loads(completed.stdout.splitlines()[-1]),
                "python": str(python),
                "dataset": self._dataset_status(),
            }
        return {
            "tool_id": self.tool_id,
            "status": "passed",
            "message": "OmniGibson package checks passed in the active environment.",
            "package_checks": self.package_status(),
            "dataset": self._dataset_status(),
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
                "message": (
                    "OmniGibson viewer uses Isaac Sim and is only executable after "
                    "the BEHAVIOR/OmniGibson dataset is installed."
                ),
                "commands": commands,
                "next_steps": [
                    "Run: python -m simtools doctor omnigibson",
                    "Personally accept the data EULA before downloading the dataset.",
                    "Raise fs.inotify.max_user_watches if Isaac reports errno=28.",
                ],
            }
        dataset = self._dataset_status()
        if not dataset["dataset_ready"]:
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "OmniGibson viewer is blocked by the missing licensed dataset.",
                "dataset": dataset,
                "commands": commands,
                "next_steps": [
                    "Run PYTHONNOUSERSITE=1 CONDA_PREFIX=\"$PWD/.venv-omnigibson\" PATH=\"$PWD/.venv-omnigibson/bin:$PATH\" .venv-omnigibson/bin/python -s -m omnigibson.download_datasets yourself.",
                    "Respond to the BEHAVIOR Data Bundle EULA only if you personally agree.",
                    "Re-run python -m simtools view omnigibson --execute after scenes exist.",
                ],
            }
        python = self._external_python()
        if python is None and not all(self.package_status().values()):
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "OmniGibson is not installed in the active environment or .venv-omnigibson.",
                "commands": commands,
            }
        command = [
            str(python),
            "-m",
            "omnigibson.examples.robots.robot_control_example",
            "--quickstart",
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=repo_root(),
                env=self._external_env(),
            )
        except subprocess.TimeoutExpired as exc:
            stdout = self._to_text(exc.stdout)
            stderr = self._to_text(exc.stderr)
            output = self._tail(stdout)
            errors = self._tail(stderr)
            ready_markers = (
                "Simulation App Startup Complete",
                "Welcome to OmniGibson",
                "Pressed None. Action:",
            )
            reached_viewer = any(
                marker in stdout or marker in stderr for marker in ready_markers
            )
            return {
                "tool_id": self.tool_id,
                "status": "passed" if reached_viewer else "timeout",
                "message": (
                    "OmniGibson viewer reached the interactive loop and was stopped after the verification timeout."
                    if reached_viewer
                    else "OmniGibson viewer timed out before a readiness marker appeared."
                ),
                "timed_out": True,
                "timeout_seconds": 300,
                "stdout_tail": output,
                "stderr_tail": errors,
                "commands": commands,
            }
        return {
            "tool_id": self.tool_id,
            "status": "passed" if completed.returncode == 0 else "failed",
            "message": "OmniGibson viewer command completed.",
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
            "commands": commands,
        }

    def _tail(self, value: str | bytes | None, limit: int = 4000) -> str:
        value = self._to_text(value)
        return value[-limit:]

    def _to_text(self, value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        return value

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
                    "omnigibson": False,
                    "isaacsim": False,
                    "omni": False,
                    "bddl": False,
                },
            }
        code = (
            "import importlib.util, json; "
            "checks={name: importlib.util.find_spec(name) is not None "
            "for name in ['omnigibson','isaacsim','omni','bddl']}; "
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
                    "omnigibson": False,
                    "isaacsim": False,
                    "omni": False,
                    "bddl": False,
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
            "modules = ['omnigibson', 'isaacsim', 'omni', 'bddl']\n"
            "missing = [name for name in modules if importlib.util.find_spec(name) is None]\n"
            "if missing:\n"
            "    raise SystemExit('missing packages: ' + ', '.join(missing))\n"
            "versions = {'omni': 'namespace'}\n"
            "for distribution in ['omnigibson', 'isaacsim', 'bddl']:\n"
            "    try:\n"
            "        versions[distribution] = metadata.version(distribution)\n"
            "    except metadata.PackageNotFoundError:\n"
            "        versions[distribution] = 'unknown'\n"
            "print(json.dumps(versions, sort_keys=True))\n"
        )
