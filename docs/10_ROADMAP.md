# Roadmap

## v0.1 Scaffold

- Docs-first project constraints
- Manifest schema and six initial manifests
- Registry and capability matrix
- CLI list/info/status/profiles/compare/doctor/run/view/artifacts/validate/install-plan/ui
- Adapter stubs
- Dashboard MVP
- Tests that pass with no real simulators installed
- Artifact report path under `.simtools/artifacts/`
- Project-local Superpowers workflows

Status: complete for the local metamanager MVP.

## v0.2 AI2-THOR

- Opt-in AI2-THOR smoke test
- Artifact capture under `.simtools/artifacts/ai2thor/`
- Better headless guidance
- Terminal-controlled Unity viewer execution path
- Mouse-driven Streamlit control UI

Status: isolated Python 3.11 validation passed, terminal-controlled Unity
viewer is available, mouse UI support is documented, and screenshot/report
artifacts are produced. See `docs/13_AI2THOR_VALIDATION.md` and
`docs/14_QUICK_USE.md`.

## v0.3 RoboCasa365 and Habitat

- Real installation profile validation
- Smoke tests that stay skipped by default
- Artifact normalization

Status: Habitat has an import-only opt-in smoke path; RoboCasa365 remains a
dry-run adapter.

## v0.4 Heavy Tools

- MolmoSpaces, OmniGibson, and BEHAVIOR-1K opt-in integration
- GPU/display diagnostics
- Large asset presence checks

## Later

- ManiSkill, Isaac Lab, MuJoCo/MJX, Gazebo, Webots, CoppeliaSim, CARLA, AirSim,
  Genesis, and Newton
- Structured benchmark runner
- Rich artifact viewer
- Profile-specific environment creation
