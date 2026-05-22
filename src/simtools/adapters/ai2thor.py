"""AI2-THOR adapter."""

from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter
from simtools.core.artifact_store import ArtifactStore


class AI2ThorAdapter(ManifestOnlyAdapter):
    tool_id = "ai2thor"

    def check_installed(self) -> bool:
        return importlib.util.find_spec("ai2thor") is not None

    def doctor(self) -> dict[str, Any]:
        installed = self.check_installed()
        return {
            "tool_id": self.tool_id,
            "status": "installed" if installed else "missing",
            "installed": installed,
            "package_checks": {"ai2thor": installed},
            "message": (
                "AI2-THOR is importable. Real smoke can be run explicitly."
                if installed
                else "AI2-THOR is not installed in this environment."
            ),
            "next_steps": (
                [
                    "Run: python -m simtools run ai2thor --mode smoke --dry-run",
                    "Then run without --dry-run if you accept any first-run runtime downloads.",
                ]
                if installed
                else [
                    "Run: python -m simtools install-plan ai2thor",
                    "Install AI2-THOR in an isolated environment before real smoke tests.",
                ]
            ),
        }

    def smoke(self, *, dry_run: bool = False) -> dict[str, Any]:
        if dry_run:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "AI2-THOR smoke would launch FloorPlan1 and run MoveAhead.",
                "commands": self.sample_commands(),
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "AI2-THOR is not installed.",
                "next_steps": [
                    "Run: python -m simtools install-plan ai2thor",
                    "Install AI2-THOR in an isolated environment.",
                ],
            }

        artifact_dir = ArtifactStore().tool_dir(self.tool_id)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        frame_path = artifact_dir / f"smoke_{timestamp}.ppm"
        controller = None

        try:
            from ai2thor.controller import Controller

            try:
                from ai2thor.platform import CloudRendering

                controller = Controller(scene="FloorPlan1", platform=CloudRendering)
            except Exception:
                controller = Controller(scene="FloorPlan1")

            event = controller.step(action="MoveAhead")
            self._write_frame(event.frame, frame_path)
            return {
                "tool_id": self.tool_id,
                "status": "passed",
                "message": "AI2-THOR FloorPlan1 smoke completed.",
                "artifact": str(frame_path),
            }
        except Exception as exc:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": f"AI2-THOR smoke failed: {exc}",
                "next_steps": [
                    "Confirm the runtime can launch on this OS/display setup.",
                    "Try: python -m simtools run ai2thor --mode smoke --dry-run",
                ],
            }
        finally:
            if controller is not None:
                try:
                    controller.stop()
                except Exception:
                    pass

    def launch_viewer(
        self,
        *,
        dry_run: bool = True,
        execute: bool = False,
    ) -> dict[str, Any]:
        command = "python -m simtools run ai2thor --mode smoke"
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "Viewer launch is dry-run by default.",
                "commands": [command],
                "next_steps": [
                    "Install AI2-THOR in an isolated environment.",
                    "Use an explicit future --execute path to launch GUI behavior.",
                ],
            }
        return {
            "tool_id": self.tool_id,
            "status": "skipped",
            "message": "Direct AI2-THOR viewer execution is not implemented yet.",
            "commands": [command],
        }

    def _write_frame(self, frame: Any, path: Path) -> None:
        """Write an RGB frame as PPM without adding image dependencies."""

        height, width = frame.shape[:2]
        header = f"P6\n{width} {height}\n255\n".encode("ascii")
        with path.open("wb") as handle:
            handle.write(header)
            handle.write(frame[:, :, :3].tobytes())


if __name__ == "__main__":
    from simtools.core.registry import ToolRegistry

    adapter = AI2ThorAdapter(ToolRegistry.from_configs().get("ai2thor"))
    print(adapter.smoke(dry_run=True))
