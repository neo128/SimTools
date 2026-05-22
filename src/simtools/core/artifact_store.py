"""Artifact path helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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

    def list_artifacts(self, tool_id: str | None = None) -> list[dict[str, Any]]:
        if tool_id:
            roots = [self.root / tool_id]
        elif self.root.exists():
            roots = sorted(self.root.glob("*"))
        else:
            roots = []
        artifacts: list[dict[str, Any]] = []
        for root in roots:
            if not root.exists() or not root.is_dir():
                continue
            current_tool = root.name
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    stat = path.stat()
                    artifacts.append(
                        {
                            "tool_id": current_tool,
                            "path": str(path),
                            "relative_path": str(path.relative_to(self.root)),
                            "size_bytes": stat.st_size,
                            "modified": datetime.fromtimestamp(
                                stat.st_mtime,
                                tz=timezone.utc,
                            ).isoformat(),
                        }
                    )
        return artifacts

    def write_json_report(
        self,
        tool_id: str,
        prefix: str,
        payload: dict[str, Any],
    ) -> Path:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_prefix = self._safe_filename_part(prefix)
        path = self.tool_dir(tool_id) / f"{safe_prefix}_{timestamp}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        return path

    def _safe_filename_part(self, value: str) -> str:
        cleaned = "".join(
            char if char.isalnum() or char in {"-", "_"} else "_"
            for char in value
        ).strip("_")
        return cleaned or "report"
