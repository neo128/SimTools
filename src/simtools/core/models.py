"""Typed configuration models for SimTools."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    """Base model that rejects unknown manifest fields."""

    model_config = ConfigDict(extra="forbid")


class BackendSpec(StrictModel):
    engine: str
    runtime: str


class GpuRequirement(StrictModel):
    required: bool = False
    recommended: bool = False


class RequirementsSpec(StrictModel):
    python: str
    recommended_python: str | None = None
    os: list[str] = Field(default_factory=list)
    gpu: GpuRequirement = Field(default_factory=GpuRequirement)
    disk_gb_min: int | float = 0
    notes: list[str] = Field(default_factory=list)


class CapabilitiesSpec(StrictModel):
    visualization: bool = False
    visualization_label: str | None = None
    viewer_modes: list[str] = Field(default_factory=list)
    tasks: list[str] = Field(default_factory=list)
    sensors: list[str] = Field(default_factory=list)
    robot_types: list[str] = Field(default_factory=list)
    supports_headless: bool | str = False
    supports_gpu: bool | str = "optional"
    large_assets_required: bool | str = False


class InstallProfile(StrictModel):
    manager: str
    commands: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class CommandSpec(StrictModel):
    description: str
    command: str


class AdapterSpec(StrictModel):
    module: str
    class_name: str
    package_checks: list[str] = Field(default_factory=list)


class ToolManifest(StrictModel):
    id: str
    name: str
    category: list[str] = Field(default_factory=list)
    backend: BackendSpec
    homepage: str
    summary: str
    install_level: str = "unknown"
    capabilities: CapabilitiesSpec
    requirements: RequirementsSpec
    install_profiles: dict[str, InstallProfile] = Field(default_factory=dict)
    commands: dict[str, CommandSpec] = Field(default_factory=dict)
    adapter: AdapterSpec
    notes: list[str] = Field(default_factory=list)
    source_path: str | None = None

    @field_validator("id")
    @classmethod
    def validate_id(cls, value: str) -> str:
        if not value:
            raise ValueError("tool id cannot be empty")
        if value != value.lower():
            raise ValueError("tool id must be lowercase")
        allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_-")
        if any(char not in allowed for char in value):
            raise ValueError("tool id may contain only lowercase letters, numbers, '-' and '_'")
        return value

    def as_metadata(self) -> dict[str, Any]:
        return self.model_dump(mode="json")


class InstallPolicy(StrictModel):
    automatic_system_packages: bool = False
    automatic_large_downloads: bool = False
    viewer_launch_default: str = "dry-run"


class ProfileConfig(StrictModel):
    id: str
    name: str
    description: str = ""
    python: str
    gpu: GpuRequirement = Field(default_factory=GpuRequirement)
    install_policy: InstallPolicy = Field(default_factory=InstallPolicy)
    source_path: str | None = None


class ProjectInfo(StrictModel):
    name: str
    version: str
    artifact_dir: str = ".simtools/artifacts"


class RegistryConfig(StrictModel):
    tools_dir: str = "configs/tools"
    profiles_dir: str = "configs/profiles"


class DefaultConfig(StrictModel):
    profile: str = "local"
    dry_run: bool = True
    require_explicit_execute: bool = True


class SimToolsConfig(StrictModel):
    project: ProjectInfo
    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    defaults: DefaultConfig = Field(default_factory=DefaultConfig)
