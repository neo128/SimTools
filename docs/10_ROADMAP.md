# Roadmap

## v0.1 Scaffold

- Docs-first project constraints
- Manifest schema and initial manifests
- Registry and capability matrix
- CLI list/info/status/profiles/compare/doctor/run/view/artifacts/validate/install-plan/ui
- Adapter stubs and dry-run plans
- Dashboard MVP
- Tests that pass with no real simulators installed
- Artifact report path under `.simtools/artifacts/`
- Project-local Superpowers workflows

Status: complete for the local metamanager MVP.

## v0.2 AI2-THOR

- Opt-in AI2-THOR smoke test
- Artifact capture under `.simtools/artifacts/ai2thor/`
- Terminal-controlled Unity viewer execution path
- Mouse-driven Streamlit control UI
- iTHOR scene catalog and scene-switching quick-use docs

Status: complete for the first real simulator path. SimTools still does not
install AI2-THOR automatically.

## v0.3 Habitat and ManiSkill

- Habitat import-only smoke path
- Habitat external `.venv-habitat` profile
- Habitat test-scene RGB render path
- ManiSkill manifest and adapter
- ManiSkill package-only smoke path
- ManiSkill MP4 visual render path

Status: ManiSkill is real-viewer ready through `.venv-maniskill` and the
official `demo_random_action` renderer. Habitat is real-viewer ready through
`.venv-habitat` and the official `habitat_test_scenes` package.

Global hard gate: all seven registered tools must remain at `real_viewer` for
`python -m simtools real-status --strict` to pass.

## v0.4 RoboCasa365

- RoboCasa365 manifest with minimal and asset profiles
- External `.venv-robocasa365` adapter with package smoke
- MuJoCo EGL Kitchen RGB render path
- Quick-use documentation that separates code install from asset download

Status: real-viewer ready. Kitchen assets were installed explicitly, and the
verified artifact is `.simtools/artifacts/robocasa365/kitchen_rgb.png`.

## v0.5 MolmoSpaces

- MolmoSpaces manifest with source and conda profiles
- External `.venv-molmospaces` adapter with package smoke
- Explicit iTHOR scene asset fetch policy
- MuJoCo EGL FloorPlan1 RGB render path
- Quick-use documentation that warns about automatic asset downloads

Status: real-viewer ready for the fetched iTHOR scene. The verified artifact is
`.simtools/artifacts/molmospaces/floorplan1_rgb.png`.

## v0.6 OmniGibson and BEHAVIOR-1K

- OmniGibson and BEHAVIOR-1K manifests with source/headless plans
- External `.venv-omnigibson` package smoke for OmniGibson, BDDL, and Isaac Sim
- Isaac Sim pip installation path verified after fixing PATH/CONDA_PREFIX
- License, GPU, display, and dataset-download constraints documented
- BEHAVIOR/OmniGibson dataset/assets verified after user EULA acceptance
- OmniGibson interactive viewer gate verified through readiness markers
- BEHAVIOR-1K visualization delegated to the verified OmniGibson viewer gate

Status: real-viewer ready. `python -m simtools view omnigibson --execute`
reaches the interactive OmniGibson loop and is stopped by the verification
timeout after readiness markers appear. `python -m simtools view behavior1k
--execute` reports `delegated_to_omnigibson`.

Hard gate: complete for the current seven-tool registry, while preserving the
rule that SimTools must not auto-accept the BEHAVIOR Data Bundle EULA or launch
real GUI viewers from pytest.

## Experiment Workbench v0.2

- `ExperimentSpec` typed model and YAML configs under `configs/experiments/`
- Run records under `.simtools/runs/<timestamp>_<experiment_id>/`
- CLI groups for `experiments` and `runs`
- Dashboard Experiment Library, Run History, and Run Detail views
- First-phase real execution for AI2-THOR smoke, Habitat PNG render, and
  ManiSkill MP4 rollout through existing adapter paths
- Dry-run and metadata reports for RoboCasa365, MolmoSpaces, OmniGibson, and
  BEHAVIOR-1K

Status: complete for the lightweight v0.2 workbench scope. The experiment
layer validates YAML ids and registry-backed `tool_id` values, writes
repository-local run records, keeps dry-run as the default, and requires
`--no-dry-run` before adapter-owned real execution paths are used.

## Experiment Metrics v0.3

- Standard `metrics` block in `report.json`
- Legacy v0.2 report normalization on read
- `simtools runs compare` with experiment, tool, status, and dry-run filters
- Run comparison summary for counts, statuses, artifacts, success, and average
  duration
- Dashboard Run History filtering and comparison summary

Status: complete for the first operational metrics and run comparison layer.
Task-specific benchmark scoring remains a later layer.

## Later

- Benchmark Runner v0.4 as planned in
  `plans/008-benchmark-runner-v0.4.md`: task-specific metrics schema,
  benchmark result metadata, run export, reproducibility metadata, and dashboard
  metrics/artifact inspection without new real simulator execution.
- Isaac Lab, MuJoCo/MJX, Gazebo, Webots, CoppeliaSim, CARLA, AirSim, Genesis,
  and Newton
- Structured benchmark runner with task-specific metrics aggregation
- Rich artifact viewer
- Profile-specific environment creation
- Per-tool environment validation reports
