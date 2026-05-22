"""Artifact path helpers."""

from __future__ import annotations

from pathlib import Path

from simtools.core.config_loader import repo_root


class ArtifactStore:
    """Store artifacts under the repository-local `.simtools` directory."""

    def __init__(self, root: Path | None = None):
        self.root = (root or repo_root() / ".simtools" / "artifacts").resolve()

    def tool_dir(self, tool_id: str) -> Path:
        path = (self.root / tool_id).resolve()
        if self.root not in path.parents and path != self.root:
            raise ValueError(f"Artifact path escaped artifact root: {path}")
        path.mkdir(parents=True, exist_ok=True)
        return path

    def path_for(self, tool_id: str, filename: str) -> Path:
        return self.tool_dir(tool_id) / filename
