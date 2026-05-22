"""Lightweight AI2-THOR scene metadata.

These constants mirror the public iTHOR scene naming scheme without importing
AI2-THOR itself.
"""

from __future__ import annotations


ITHOR_SCENE_GROUPS: dict[str, list[str]] = {
    "Kitchens": [f"FloorPlan{i}" for i in range(1, 31)],
    "Living rooms": [f"FloorPlan{200 + i}" for i in range(1, 31)],
    "Bedrooms": [f"FloorPlan{300 + i}" for i in range(1, 31)],
    "Bathrooms": [f"FloorPlan{400 + i}" for i in range(1, 31)],
}


def ithor_scenes() -> list[str]:
    """Return the 120 public iTHOR scene names in standard order."""

    scenes: list[str] = []
    for group in ITHOR_SCENE_GROUPS.values():
        scenes.extend(group)
    return scenes


def room_type_for_scene(scene: str) -> str | None:
    """Return the iTHOR room type for a scene name, if known."""

    normalized = scene.removesuffix("_physics")
    for room_type, scenes in ITHOR_SCENE_GROUPS.items():
        if normalized in scenes:
            return room_type
    return None
