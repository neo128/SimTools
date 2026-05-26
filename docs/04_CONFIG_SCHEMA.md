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
- `readiness`: real local runnable and visualization verification status

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
readiness:
  stage: real_viewer
  local_environment: .venv-ai2thor
  local_runnable: true
  smoke_verified: true
  visualization_verified: true
  validation_command: ./scripts/view_ai2thor.sh FloorPlan1 --max-actions 0
  viewer_command: ./scripts/view_ai2thor_ui.sh FloorPlan1 --port 8502
  artifact_examples:
    - .simtools/artifacts/ai2thor/smoke_20260522T092610Z.ppm
  blockers: []
  last_verified: "2026-05-22"
  notes:
    - Terminal Unity viewer and mouse UI are wired.
```

## Readiness Stages

- `real_viewer`: package smoke and local visualization were verified.
- `package_smoke`: package/import checks exist, but real visualization is not
  verified yet.
- `planned`: manifest, install plan, and adapter plan exist, but the tool is
  not locally runnable through SimTools yet.

Use `python -m simtools real-status` to inspect this field. Use
`python -m simtools real-status --strict` as a release gate when every
registered tool must be locally runnable and visualized.

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

## Experiment Files

Experiment specs live under `configs/experiments/` and are validated by
`ExperimentSpec` in `src/simtools/core/experiments.py`.

Required fields:

- `id`: stable lowercase experiment id, matching the filename stem
- `tool_id`: existing simulator id from the tool registry
- `scene`: scene or environment name
- `task`: task label
- `seed`: integer seed recorded in the run report
- `max_steps`: positive integer step budget
- `output`: structured output expectations
- `notes`: list of setup or interpretation notes

The YAML filename stem must match `id`, and `tool_id` must exist in the same
registry used by the CLI and dashboard. Loading errors include the config path
and the invalid id so malformed experiments are easy to locate.

Example:

```yaml
id: maniskill_pickcube_visual_rollout
tool_id: maniskill
scene: PickCube-v1
task: visual_rollout
seed: 0
max_steps: 8
output:
  artifact_kinds:
    - mp4
  primary: rollout_video
notes:
  - Non-dry-run uses the existing ManiSkill visual rollout path.
```

## Run Report Files

Experiment run reports are generated under `.simtools/runs/<run_id>/`; they are
not user-authored config files, but they are a stable machine-readable contract
for CLI and dashboard views.

Minimum `report.json` keys:

- `run_id`
- `experiment_id`
- `tool_id`
- `scene`
- `task`
- `seed`
- `max_steps`
- `dry_run`
- `status`
- `message`
- `started_at`
- `finished_at`
- `duration_seconds`
- `command`
- `metrics`
- `artifacts`
- `output`
- `notes`
- `adapter_result`

`metrics` uses schema version `simtools.metrics.v1`:

```json
{
  "schema_version": "simtools.metrics.v1",
  "success": false,
  "dry_run": true,
  "duration_seconds": 0.002,
  "artifact_count": 0,
  "stdout_bytes": 0,
  "stderr_bytes": 0,
  "max_steps": 1
}
```

Older reports without `metrics` are normalized on read by the run-store helpers
so `simtools runs compare` and the dashboard can still inspect historical runs.

## Run Comparison Payload

`simtools runs compare --json` returns schema version
`simtools.run_comparison.v1`. The payload contains:

- `filters`: selected experiment, tool, status, and dry-run filters
- `summary`: run count, experiment count, tool count, status counts, dry-run
  count, success count, total artifact count, and average duration
- `runs`: normalized run rows with metrics, paths, status, and artifact counts

Run comparison is read-only. It uses `.simtools/runs/` metadata and must not
launch adapters or import heavyweight simulator packages.
