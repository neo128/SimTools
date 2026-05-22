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
- Habitat dry-run viewer plan
- ManiSkill manifest and adapter
- ManiSkill package-only smoke path
- ManiSkill dry-run viewer plan

Status: complete for safe planning and package-level validation. Next real work
is choosing one opt-in rendered viewer path after confirming local GPU/display
requirements.

Hard gate: neither tool is complete under the real-local requirement until
`python -m simtools real-status --strict` can pass with both marked
`real_viewer`.

## v0.4 RoboCasa365

- RoboCasa365 manifest with minimal and asset profiles
- Planned adapter with install, smoke, and viewer dry-runs
- Quick-use documentation that separates code install from asset download

Status: complete for dry-run planning. A real adapter should first check
`robocasa` and `robosuite` imports, then add a no-download smoke.

Hard gate: not complete under the real-local requirement until code install,
asset policy, smoke, and MuJoCo viewer are locally verified.

## v0.5 MolmoSpaces

- MolmoSpaces manifest with source and conda profiles
- Planned adapter with MuJoCo/debug-viewer guidance
- Quick-use documentation that warns about automatic asset downloads

Status: complete for dry-run planning. A real adapter should first validate
`molmo_spaces` and `mujoco` imports, then add cache-directory checks.

Hard gate: not complete under the real-local requirement until cache policy,
smoke, and MuJoCo debug viewer are locally verified.

## v0.6 OmniGibson and BEHAVIOR-1K

- OmniGibson and BEHAVIOR-1K manifests with source/headless plans
- Planned adapters with Isaac/Omniverse viewer guidance
- License, GPU, display, and dataset-download constraints documented

Status: complete for dry-run planning. Real execution remains intentionally
deferred until local hardware, Isaac Sim, license, and asset policies are
confirmed.

Hard gate: not complete under the real-local requirement until Isaac/Omniverse,
assets, smoke, and viewer commands are locally verified.

## Later

- Isaac Lab, MuJoCo/MJX, Gazebo, Webots, CoppeliaSim, CARLA, AirSim, Genesis,
  and Newton
- Structured benchmark runner
- Rich artifact viewer
- Profile-specific environment creation
- Per-tool environment validation reports
