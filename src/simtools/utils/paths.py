"""Path utilities."""

from __future__ import annotations

from pathlib import Path

from simtools.core.config_loader import repo_root


def project_path(*parts: str) -> Path:
    return repo_root().joinpath(*parts)
