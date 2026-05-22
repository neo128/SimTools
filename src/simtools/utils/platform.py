"""Platform helpers."""

from __future__ import annotations

import platform as _platform


def normalized_os() -> str:
    system = _platform.system().lower()
    if system == "darwin":
        return "macos"
    return system
