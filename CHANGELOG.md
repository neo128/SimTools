# Changelog

All notable changes to SimTools will be documented here.

## 0.1.0 - 2026-05-22

- Added docs-first project constraints and architecture.
- Added manifest-driven registry for six initial simulators.
- Added CLI commands for list, info, status, profiles, compare, doctor, run,
  view, artifacts, validate, install-plan, and ui.
- Added adapter stubs and AI2-THOR opt-in smoke path.
- Added project-local Superpowers workflows.
- Added local validation script and tests that pass without real simulators.

## Unreleased

- Added GitHub Actions test workflow.
- Added project contribution and release docs.
- Added AI2-THOR isolated validation docs and script.
- Added AI2-THOR terminal-controlled Unity viewer execution path.
- Hardened Habitat as the second real-tool path with import-only smoke.
- Added ManiSkill manifest, adapter, install-plan, and package-only smoke path.
- Added planned dry-run adapters for RoboCasa365, MolmoSpaces, OmniGibson, and
  BEHAVIOR-1K.
- Added real local run readiness metadata and `simtools real-status` gate.
- Promoted ManiSkill to a real visual path that renders a PickCube-v1 MP4
  artifact in `.venv-maniskill`.
- Promoted Habitat to a real visual path that renders an RGB PNG from the
  official Habitat test scenes in `.venv-habitat`.
- Promoted RoboCasa365 to a real visual path that renders a Kitchen RGB PNG
  through MuJoCo EGL after explicit kitchen asset setup.
- Promoted MolmoSpaces to a real visual path that renders an iTHOR FloorPlan1
  RGB PNG through MuJoCo EGL after explicit scene asset setup.
- Added OmniGibson and BEHAVIOR-1K package/runtime verification through
  `.venv-omnigibson`, with full viewer execution blocked on the user-accepted
  BEHAVIOR Data Bundle EULA and dataset installation.
- Promoted OmniGibson to `real_viewer` after dataset/assets, CUDA discovery,
  and interactive viewer readiness markers were verified.
- Promoted BEHAVIOR-1K to `real_viewer` with visualization delegated to the
  verified OmniGibson viewer gate.
- Improved dashboard artifact previews.
