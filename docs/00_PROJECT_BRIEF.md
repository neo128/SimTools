# SimTools Project Brief

SimTools is a local, config-driven management layer for embodied AI simulation
tools. It manages metadata, installation profiles, launch plans, smoke tests,
viewer commands, artifacts, experiment specs, run records, operational metrics,
and comparison matrices across multiple simulators.

Current tools:

- Habitat
- AI2-THOR
- ManiSkill
- BEHAVIOR-1K
- OmniGibson
- MolmoSpaces
- RoboCasa365

SimTools is not a simulator and is not a monolithic installer. It is a
metamanager that keeps each simulator isolated behind a manifest, adapter, and
profile. The core package must remain lightweight enough to test without any
real simulator installed.

## Current Baseline

- Seven registered tools are at `readiness.stage: real_viewer`.
- `python -m simtools validate --json` is the repository validation gate.
- `python -m simtools real-status --strict` is the real local readiness gate.
- Experiment Workbench v0.2 records experiment runs under `.simtools/runs/`.
- Experiment Metrics v0.3 adds `simtools.metrics.v1` and
  `simtools.run_comparison.v1`.
- CLI and dashboard views read shared registry, experiment, run-store, and
  comparison helpers.

## Completed Foundation

The original v0.1 goal was to build a reproducible local metamanager MVP:

- project documentation and constraints
- typed manifest schema
- registry loaded from YAML manifests
- lightweight CLI
- adapter stubs
- dashboard MVP
- status, profile, artifact, install-plan, and validation views
- tests that pass without real simulators installed

That foundation now includes real-viewer readiness for the current seven-tool
registry and a lightweight experiment/metrics layer.

## Non-goals

- installing all simulators into one Python environment
- downloading large assets
- launching GUI windows in tests
- assuming GPU availability
- running system package managers

## Current Evaluation

See `docs/19_PROJECT_EVALUATION.md` for the current engineering assessment,
risks, documentation map, and next development priorities. The next planned
engineering slice is `plans/008-benchmark-runner-v0.4.md`, which keeps
benchmark work metadata/report-driven before adding task-specific real
simulator execution.
