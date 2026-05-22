"""Local environment inspection."""

from __future__ import annotations

import os
import platform
import shutil
import sys
from pathlib import Path

from simtools.core.config_loader import repo_root


def collect_system_info() -> dict[str, str | bool]:
    root = repo_root()
    return {
        "python_version": sys.version.split()[0],
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "system": platform.system().lower(),
        "machine": platform.machine(),
        "cwd": str(Path.cwd()),
        "repo_root": str(root),
        "inside_repo": str(Path.cwd().resolve()).startswith(str(root.resolve())),
        "nvidia_smi_on_path": shutil.which("nvidia-smi") is not None,
        "display": os.environ.get("DISPLAY", ""),
    }
