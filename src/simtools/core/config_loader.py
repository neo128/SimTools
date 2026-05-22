"""Load SimTools YAML configuration files."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from simtools.core.errors import ConfigError
from simtools.core.models import ToolManifest


def repo_root() -> Path:
    """Return the current repository root.

    The project is currently designed for local checkouts. `SIMTOOLS_REPO_ROOT`
    can override auto-detection for tests or embedded use.
    """

    override = os.environ.get("SIMTOOLS_REPO_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[3]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config file does not exist: {path}")
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"YAML root must be a mapping: {path}")
    return data


def load_tool_manifest(path: Path) -> ToolManifest:
    data = load_yaml(path)
    data["source_path"] = str(path)
    try:
        manifest = ToolManifest.model_validate(data)
    except ValidationError as exc:
        raise ConfigError(f"Invalid tool manifest {path}: {exc}") from exc
    if manifest.id != path.stem:
        raise ConfigError(
            f"Manifest id '{manifest.id}' must match filename stem '{path.stem}'"
        )
    return manifest


def default_tools_dir() -> Path:
    return repo_root() / "configs" / "tools"


def default_profiles_dir() -> Path:
    return repo_root() / "configs" / "profiles"


def load_tool_manifests(tools_dir: Path | None = None) -> list[ToolManifest]:
    directory = tools_dir or default_tools_dir()
    if not directory.exists():
        raise ConfigError(f"Tools directory does not exist: {directory}")
    manifests = [load_tool_manifest(path) for path in sorted(directory.glob("*.yaml"))]
    if not manifests:
        raise ConfigError(f"No tool manifests found in {directory}")
    return manifests


def load_global_config(path: Path | None = None) -> dict[str, Any]:
    return load_yaml(path or repo_root() / "configs" / "simtools.yaml")


def load_profile(profile_id: str = "local", profiles_dir: Path | None = None) -> dict[str, Any]:
    directory = profiles_dir or default_profiles_dir()
    return load_yaml(directory / f"{profile_id}.yaml")
