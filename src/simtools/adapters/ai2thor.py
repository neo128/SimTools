"""AI2-THOR adapter."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from simtools.adapters.base import ManifestOnlyAdapter
from simtools.core.artifact_store import ArtifactStore
from simtools.core.config_loader import repo_root


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
        **options: Any,
    ) -> dict[str, Any]:
        scene = str(options.get("scene") or "FloorPlan1")
        width = int(options.get("width") or 800)
        height = int(options.get("height") or 600)
        ui = bool(options.get("ui"))
        port = int(options.get("port") or 8502)
        max_actions = options.get("max_actions")
        if ui:
            return self._launch_mouse_ui(
                dry_run=dry_run,
                execute=execute,
                scene=scene,
                width=width,
                height=height,
                port=port,
            )
        command = (
            "python -m simtools view ai2thor --execute "
            f"--scene {scene} --width {width} --height {height}"
        )
        if max_actions is not None:
            command = f"{command} --max-actions {int(max_actions)}"
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "AI2-THOR Unity viewer launch is dry-run by default.",
                "commands": [command],
                "next_steps": [
                    "Install AI2-THOR in an isolated environment.",
                    "Run with --execute to open a Unity window and control it from the terminal.",
                ],
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "AI2-THOR is not installed.",
                "commands": [command],
                "next_steps": [
                    "Run: python -m simtools install-plan ai2thor",
                    "Install AI2-THOR in an isolated environment.",
                ],
            }
        if max_actions is None and not sys.stdin.isatty():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "Interactive viewer execution requires a TTY.",
                "commands": [command],
                "next_steps": [
                    "Run the command from a local terminal.",
                    "Use --max-actions 0 for launch-and-close validation.",
                ],
            }

        return self._run_interactive_viewer(
            scene=scene,
            width=width,
            height=height,
            max_actions=max_actions,
        )

    def _launch_mouse_ui(
        self,
        *,
        dry_run: bool,
        execute: bool,
        scene: str,
        width: int,
        height: int,
        port: int,
    ) -> dict[str, Any]:
        command = (
            "python -m simtools view ai2thor --ui --execute "
            f"--scene {scene} --width {width} --height {height} --port {port}"
        )
        if dry_run or not execute:
            return {
                "tool_id": self.tool_id,
                "status": "planned",
                "message": "AI2-THOR mouse UI launch is dry-run by default.",
                "commands": [command],
                "next_steps": [
                    "Install AI2-THOR and Streamlit in the isolated environment.",
                    "Run with --ui --execute to open the browser-based control panel.",
                ],
            }
        if not self.check_installed():
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "AI2-THOR is not installed.",
                "commands": [command],
                "next_steps": [
                    "Run: python -m simtools install-plan ai2thor",
                    "Install AI2-THOR in an isolated environment.",
                ],
            }
        if importlib.util.find_spec("streamlit") is None:
            return {
                "tool_id": self.tool_id,
                "status": "skipped",
                "message": "Streamlit is not installed in this environment.",
                "commands": [command],
                "next_steps": [
                    "Install the dashboard extra in the isolated AI2-THOR environment.",
                    "Example: .venv-ai2thor/bin/python -m pip install streamlit",
                ],
            }

        app_path = repo_root() / "src" / "simtools" / "ui" / "ai2thor_app.py"
        env = os.environ.copy()
        env.update(
            {
                "SIMTOOLS_AI2THOR_SCENE": scene,
                "SIMTOOLS_AI2THOR_WIDTH": str(width),
                "SIMTOOLS_AI2THOR_HEIGHT": str(height),
                "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
                "STREAMLIT_SERVER_HEADLESS": "true",
                "STREAMLIT_SERVER_SHOW_EMAIL_PROMPT": "false",
            }
        )
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app_path),
                "--server.port",
                str(port),
                "--server.headless",
                "true",
                "--server.showEmailPrompt",
                "false",
                "--browser.gatherUsageStats",
                "false",
            ],
            check=False,
            env=env,
        )
        status = "closed" if completed.returncode == 0 else "failed"
        message = (
            "AI2-THOR mouse UI process exited."
            if completed.returncode == 0
            else "AI2-THOR mouse UI failed to start or exited with an error."
        )
        result: dict[str, Any] = {
            "tool_id": self.tool_id,
            "status": status,
            "message": message,
            "scene": scene,
            "port": port,
            "return_code": completed.returncode,
        }
        if completed.returncode != 0:
            result["next_steps"] = [
                "Check whether the selected Streamlit port is already in use.",
                f"Try: python -m simtools view ai2thor --ui --execute --scene {scene} --port {port + 1}",
            ]
        return result

    def _run_interactive_viewer(
        self,
        *,
        scene: str,
        width: int,
        height: int,
        max_actions: Any,
    ) -> dict[str, Any]:
        controller = None
        actions_run = 0
        latest_frame: Path | None = None
        action_limit = None if max_actions is None else int(max_actions)

        try:
            from ai2thor.controller import Controller

            if action_limit is None:
                print(
                    (
                        "Starting AI2-THOR Unity viewer "
                        f"(scene={scene}, size={width}x{height}). "
                        "This can take a few seconds; first launch may take longer."
                    ),
                    file=sys.stderr,
                    flush=True,
                )
            controller = Controller(scene=scene, width=width, height=height)
            if action_limit == 0:
                return {
                    "tool_id": self.tool_id,
                    "status": "passed",
                    "message": "AI2-THOR Unity viewer launched and closed.",
                    "scene": scene,
                    "actions_run": actions_run,
                }

            print("AI2-THOR Unity viewer is ready.", file=sys.stderr, flush=True)
            print(self._viewer_help(scene, width, height), flush=True)
            while True:
                if action_limit is not None and actions_run >= action_limit:
                    break
                user_input = input("ai2thor> ").strip()
                if not user_input:
                    continue
                if user_input in {"q", "quit", "exit"}:
                    break
                if user_input in {"h", "help", "?"}:
                    print(self._viewer_help(scene, width, height))
                    continue
                if user_input in {"shot", "screenshot"}:
                    latest_frame = self._save_viewer_frame(controller.last_event.frame)
                    print(f"saved {latest_frame}")
                    continue

                action = self._viewer_action(user_input)
                if action is None:
                    print(f"unknown command: {user_input}")
                    print("type 'help' for controls")
                    continue
                event = controller.step(action=action)
                actions_run += 1
                success = event.metadata.get("lastActionSuccess", False)
                error = event.metadata.get("errorMessage") or ""
                status = "ok" if success else "failed"
                print(f"{action}: {status} {error}".strip())

            if getattr(controller, "last_event", None) is not None:
                latest_frame = self._save_viewer_frame(controller.last_event.frame)
            return {
                "tool_id": self.tool_id,
                "status": "closed",
                "message": "AI2-THOR Unity viewer closed.",
                "scene": scene,
                "actions_run": actions_run,
                "artifact": str(latest_frame) if latest_frame else None,
            }
        except KeyboardInterrupt:
            return {
                "tool_id": self.tool_id,
                "status": "closed",
                "message": "AI2-THOR Unity viewer interrupted and closed.",
                "scene": scene,
                "actions_run": actions_run,
                "artifact": str(latest_frame) if latest_frame else None,
            }
        except Exception as exc:
            return {
                "tool_id": self.tool_id,
                "status": "failed",
                "message": f"AI2-THOR Unity viewer failed: {exc}",
                "scene": scene,
                "next_steps": [
                    "Confirm the AI2-THOR runtime can launch on this OS/display setup.",
                    "Try: python -m simtools view ai2thor --execute --max-actions 0",
                ],
            }
        finally:
            if controller is not None:
                try:
                    controller.stop()
                except Exception:
                    pass

    def _viewer_action(self, command: str) -> str | None:
        aliases = {
            "w": "MoveAhead",
            "forward": "MoveAhead",
            "back": "MoveBack",
            "s": "MoveBack",
            "a": "RotateLeft",
            "left": "RotateLeft",
            "d": "RotateRight",
            "right": "RotateRight",
            "u": "LookUp",
            "up": "LookUp",
            "j": "LookDown",
            "down": "LookDown",
        }
        if command in aliases:
            return aliases[command]
        if command[:1].isupper():
            return command
        return None

    def _viewer_help(self, scene: str, width: int, height: int) -> str:
        return (
            f"AI2-THOR Unity viewer: scene={scene}, size={width}x{height}\n"
            "Controls: w=MoveAhead, s=MoveBack, a=RotateLeft, d=RotateRight, "
            "u=LookUp, j=LookDown\n"
            "Other commands: shot, help, quit\n"
            "You may also type a raw AI2-THOR action name such as RotateRight."
        )

    def _save_viewer_frame(self, frame: Any) -> Path:
        artifact_dir = ArtifactStore().tool_dir(self.tool_id)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        frame_path = artifact_dir / f"viewer_{timestamp}.ppm"
        self._write_frame(frame, frame_path)
        return frame_path

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
