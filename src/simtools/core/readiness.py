"""Real local run and visualization readiness helpers."""

from __future__ import annotations

from typing import Any

from simtools.core.models import ToolManifest
from simtools.core.registry import ToolRegistry


def is_real_ready(manifest: ToolManifest) -> bool:
    readiness = manifest.readiness
    return (
        readiness.stage == "real_viewer"
        and readiness.local_runnable
        and readiness.smoke_verified
        and readiness.visualization_verified
        and not readiness.blockers
        and bool(readiness.last_verified)
    )


def readiness_row(manifest: ToolManifest) -> dict[str, Any]:
    readiness = manifest.readiness
    return {
        "id": manifest.id,
        "name": manifest.name,
        "stage": readiness.stage,
        "local_environment": readiness.local_environment or "-",
        "local_runnable": readiness.local_runnable,
        "smoke_verified": readiness.smoke_verified,
        "visualization_verified": readiness.visualization_verified,
        "real_ready": is_real_ready(manifest),
        "validation_command": readiness.validation_command or "",
        "viewer_command": readiness.viewer_command or "",
        "blockers": readiness.blockers,
        "last_verified": readiness.last_verified or "",
    }


def readiness_rows(registry: ToolRegistry) -> list[dict[str, Any]]:
    return [readiness_row(manifest) for manifest in registry.all()]


def readiness_summary(registry: ToolRegistry) -> dict[str, Any]:
    rows = readiness_rows(registry)
    ready = [row for row in rows if row["real_ready"]]
    not_ready = [row for row in rows if not row["real_ready"]]
    return {
        "status": "passed" if not not_ready else "failed",
        "tool_count": len(rows),
        "ready_count": len(ready),
        "not_ready_count": len(not_ready),
        "ready_tools": [row["id"] for row in ready],
        "not_ready_tools": [row["id"] for row in not_ready],
        "tools": rows,
    }
