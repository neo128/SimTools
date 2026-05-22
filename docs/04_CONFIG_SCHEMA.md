# Config Schema

Tool manifests are YAML files under `configs/tools/`. They are validated by
Pydantic models in `src/simtools/core/models.py`.

## Required Fields

- `id`: stable lowercase tool id
- `name`: display name
- `category`: list of category strings
- `backend.engine`: primary engine or runtime
- `backend.runtime`: runtime type
- `homepage`: project website
- `summary`: short description
- `capabilities`: viewer, task, sensor, robot, headless, GPU, and asset flags
- `requirements`: Python, OS, GPU, disk, and notes
- `install_profiles`: named install plans
- `commands`: dry-run command descriptions
- `adapter`: adapter module/class metadata

## Example

```yaml
id: ai2thor
name: AI2-THOR
category:
  - embodied_ai
  - indoor_interaction
backend:
  engine: Unity
  runtime: Python package
homepage: https://ai2thor.allenai.org
summary: Interactive indoor 3D environments for embodied AI tasks.
capabilities:
  visualization: true
  viewer_modes: [unity_window, headless_rgb]
  tasks: [object_navigation, pickup_place]
  sensors: [rgb, depth, metadata]
  robot_types: [mobile_agent]
  supports_headless: true
  supports_gpu: optional
  large_assets_required: false
requirements:
  python: ">=3.9"
  recommended_python: "3.11"
  os: [linux, macos, windows]
  gpu:
    required: false
    recommended: false
  disk_gb_min: 1
install_profiles:
  minimal:
    manager: pip
    commands:
      - pip install ai2thor
commands:
  smoke:
    description: Launch FloorPlan1 and perform one action.
    command: python -m simtools run ai2thor --mode smoke
adapter:
  module: simtools.adapters.ai2thor
  class_name: AI2ThorAdapter
  package_checks: [ai2thor]
```

## Profile Files

Environment profiles live under `configs/profiles/`.

```yaml
id: local
name: Local Metadata Profile
description: Default profile for local metadata-only use.
python: ">=3.11"
gpu:
  required: false
  recommended: false
install_policy:
  automatic_system_packages: false
  automatic_large_downloads: false
  viewer_launch_default: dry-run
```

Profiles document local assumptions and guardrails. They do not create
environments by themselves.
