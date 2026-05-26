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
- Benchmark Runner v0.4 adds metadata-only `simtools.task_metrics.v1`,
  `simtools.benchmark_result.v1`, `simtools.reproducibility.v1`, and
  `simtools.run_export.v1`.
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
registry, a lightweight experiment/metrics layer, and a metadata/report-driven
benchmark export layer.

## Non-goals

- installing all simulators into one Python environment
- downloading large assets
- launching GUI windows in tests
- assuming GPU availability
- running system package managers

## Current Evaluation

See `docs/19_PROJECT_EVALUATION.md` for the current engineering assessment,
risks, documentation map, and next development priorities. Benchmark Runner
v0.4 is implemented as the current metadata/report-driven benchmark slice; the
remaining benchmark work is task-specific scoring, real benchmark execution,
artifact previews, and aggregation policy.
