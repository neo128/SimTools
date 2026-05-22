"""Mouse-driven AI2-THOR viewer.

This module avoids importing Streamlit and AI2-THOR at module import time so
base tests can import helpers without optional simulator dependencies.
"""

from __future__ import annotations

import importlib.util
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from simtools.adapters.ai2thor_scenes import ithor_scenes, room_type_for_scene
from simtools.core.artifact_store import ArtifactStore


def visible_object_options(objects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return visible AI2-THOR object metadata ready for a UI select box."""

    options: list[dict[str, Any]] = []
    for obj in objects:
        object_id = str(obj.get("objectId") or "")
        if not object_id or not obj.get("visible"):
            continue
        object_type = str(obj.get("objectType") or "object")
        name = str(obj.get("name") or object_type)
        distance = obj.get("distance")
        distance_label = f"{distance:.2f}m" if isinstance(distance, (int, float)) else "nearby"
        options.append(
            {
                "label": f"{object_type} - {name} - {distance_label}",
                "object_id": object_id,
                "object_type": object_type,
                "pickupable": bool(obj.get("pickupable")),
                "openable": bool(obj.get("openable")),
                "is_open": bool(obj.get("isOpen")),
                "toggleable": bool(obj.get("toggleable")),
                "is_toggled": bool(obj.get("isToggled")),
                "receptacle": bool(obj.get("receptacle")),
                "sliceable": bool(obj.get("sliceable")),
                "breakable": bool(obj.get("breakable")),
            }
        )
    return sorted(options, key=lambda item: item["label"])


def object_action_specs(option: dict[str, Any]) -> list[dict[str, str]]:
    """Return object action button specs for selected object metadata."""

    actions: list[dict[str, str]] = []
    if option.get("pickupable"):
        actions.append({"label": "Pick up", "action": "PickupObject"})
    if option.get("openable"):
        actions.append(
            {
                "label": "Close" if option.get("is_open") else "Open",
                "action": "CloseObject" if option.get("is_open") else "OpenObject",
            }
        )
    if option.get("toggleable"):
        actions.append(
            {
                "label": "Toggle off" if option.get("is_toggled") else "Toggle on",
                "action": "ToggleObjectOff" if option.get("is_toggled") else "ToggleObjectOn",
            }
        )
    if option.get("receptacle"):
        actions.append({"label": "Put held object", "action": "PutObject"})
    if option.get("sliceable"):
        actions.append({"label": "Slice", "action": "SliceObject"})
    if option.get("breakable"):
        actions.append({"label": "Break", "action": "BreakObject"})
    return actions


def action_status(metadata: dict[str, Any]) -> str:
    """Return a compact status line for the last AI2-THOR action."""

    action = metadata.get("lastAction") or "action"
    success = metadata.get("lastActionSuccess")
    error = metadata.get("errorMessage") or ""
    if success is True:
        return f"{action}: ok"
    if success is False:
        return f"{action}: failed {error}".strip()
    return "No action has run yet."


def write_ppm_frame(frame: Any, prefix: str = "viewer_ui") -> Path:
    """Write an RGB frame as PPM without adding image-writing dependencies."""

    artifact_dir = ArtifactStore().tool_dir("ai2thor")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    frame_path = artifact_dir / f"{prefix}_{timestamp}.ppm"
    height, width = frame.shape[:2]
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    with frame_path.open("wb") as handle:
        handle.write(header)
        handle.write(frame[:, :, :3].tobytes())
    return frame_path


def _default_scene() -> str:
    return os.environ.get("SIMTOOLS_AI2THOR_SCENE", "FloorPlan1")


def _default_width() -> int:
    return int(os.environ.get("SIMTOOLS_AI2THOR_WIDTH", "800"))


def _default_height() -> int:
    return int(os.environ.get("SIMTOOLS_AI2THOR_HEIGHT", "600"))


def main() -> None:
    import streamlit as st

    st.set_page_config(page_title="AI2-THOR Viewer", layout="wide")
    st.title("AI2-THOR Viewer")

    if importlib.util.find_spec("ai2thor") is None:
        st.error("AI2-THOR is not installed in this Python environment.")
        st.code(
            "conda create -p ./.venv-ai2thor python=3.11 pip -y\n"
            ".venv-ai2thor/bin/python -m pip install -e . ai2thor streamlit",
            language="bash",
        )
        return

    if "ai2thor_controller" not in st.session_state:
        st.session_state.ai2thor_controller = None
        st.session_state.ai2thor_event = None
        st.session_state.ai2thor_actions_run = 0

    with st.sidebar:
        st.header("Session")
        scene_options = ithor_scenes()
        default_scene = _default_scene()
        default_index = scene_options.index(default_scene) if default_scene in scene_options else 0
        selected_scene = st.selectbox("iTHOR scene", scene_options, index=default_index)
        custom_scene = st.text_input("Custom scene", value="" if default_scene in scene_options else default_scene)
        scene = custom_scene.strip() or selected_scene
        room_type = room_type_for_scene(scene)
        st.caption(room_type or "Custom scene")
        width = st.number_input("Width", min_value=64, max_value=4096, value=_default_width())
        height = st.number_input("Height", min_value=64, max_value=4096, value=_default_height())
        start = st.button("Start / Reset", use_container_width=True)
        stop = st.button("Stop", use_container_width=True)

    if stop:
        _stop_controller(st)
        st.success("Viewer stopped.")

    if start:
        _stop_controller(st)
        try:
            from ai2thor.controller import Controller

            controller = Controller(scene=scene, width=int(width), height=int(height))
            st.session_state.ai2thor_controller = controller
            st.session_state.ai2thor_event = controller.last_event
            st.session_state.ai2thor_actions_run = 0
            st.success("Viewer started.")
        except Exception as exc:
            st.error(f"Failed to start AI2-THOR: {exc}")

    controller = st.session_state.ai2thor_controller
    event = st.session_state.ai2thor_event

    if controller is None or event is None:
        st.info("Press Start / Reset to launch AI2-THOR.")
        return

    metadata = event.metadata
    agent = metadata.get("agent", {})
    visible_objects = visible_object_options(metadata.get("objects", []))

    move_col, object_col = st.columns([1, 1])
    with move_col:
        st.subheader("Move")
        row1 = st.columns(3)
        if row1[1].button("Forward", use_container_width=True):
            _step(st, "MoveAhead")
        row2 = st.columns(3)
        if row2[0].button("Left", use_container_width=True):
            _step(st, "RotateLeft")
        if row2[1].button("Back", use_container_width=True):
            _step(st, "MoveBack")
        if row2[2].button("Right", use_container_width=True):
            _step(st, "RotateRight")
        row3 = st.columns(2)
        if row3[0].button("Look up", use_container_width=True):
            _step(st, "LookUp")
        if row3[1].button("Look down", use_container_width=True):
            _step(st, "LookDown")

    with object_col:
        st.subheader("Object")
        if visible_objects:
            labels = [item["label"] for item in visible_objects]
            selected_label = st.selectbox("Visible object", labels)
            selected = next(item for item in visible_objects if item["label"] == selected_label)
            specs = object_action_specs(selected)
            if specs:
                columns = st.columns(min(3, len(specs)))
                for index, spec in enumerate(specs):
                    if columns[index % len(columns)].button(
                        spec["label"],
                        key=f"object_action_{spec['action']}",
                        use_container_width=True,
                    ):
                        _step(st, spec["action"], objectId=selected["object_id"])
            else:
                st.caption("No supported actions for this visible object.")
        else:
            st.caption("No visible objects reported by AI2-THOR.")

        if st.button("Save screenshot", use_container_width=True):
            path = write_ppm_frame(st.session_state.ai2thor_event.frame)
            st.success(f"Saved {path}")

    event = st.session_state.ai2thor_event
    metadata = event.metadata
    agent = metadata.get("agent", {})

    st.subheader("Camera")
    st.image(event.frame, channels="RGB", use_container_width=True)
    status_col, agent_col = st.columns([1, 1])
    status_col.code(action_status(metadata), language="text")
    agent_col.json(
        {
            "scene": scene,
            "actions_run": st.session_state.ai2thor_actions_run,
            "position": agent.get("position"),
            "rotation": agent.get("rotation"),
            "camera_horizon": agent.get("cameraHorizon"),
        }
    )


def _step(st: Any, action: str, **kwargs: Any) -> None:
    controller = st.session_state.ai2thor_controller
    if controller is None:
        st.warning("Start the viewer first.")
        return
    event = controller.step(action=action, **kwargs)
    st.session_state.ai2thor_event = event
    st.session_state.ai2thor_actions_run += 1


def _stop_controller(st: Any) -> None:
    controller = st.session_state.get("ai2thor_controller")
    if controller is not None:
        try:
            controller.stop()
        except Exception:
            pass
    st.session_state.ai2thor_controller = None
    st.session_state.ai2thor_event = None
    st.session_state.ai2thor_actions_run = 0


if __name__ == "__main__":
    main()
