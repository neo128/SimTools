# Project Evaluation

This evaluation summarizes the current SimTools state after the seven-tool
real-viewer baseline, Experiment Workbench v0.2, and Experiment Metrics v0.3.

## Executive Summary

SimTools is now a usable local metamanager for embodied AI simulator tooling.
The project has a stable manifest + adapter architecture, a shared registry for
CLI and dashboard views, real local readiness metadata for seven tools, and a
lightweight experiment layer that records dry-runs and opt-in real runs without
pulling simulator dependencies into the base package.

The strongest next move is not adding another simulator immediately. The
highest leverage work is to harden the experiment layer into a benchmark-ready
workflow: task-specific metrics, richer artifact inspection, comparison
exports, and stronger reproducibility metadata.

## Current Capabilities

- Seven simulator tools are represented by YAML manifests under
  `configs/tools/`.
- Each simulator has a lightweight adapter under `src/simtools/adapters/`.
- `real-status --strict` is the release gate for the current registry.
- Experiment specs live under `configs/experiments/`.
- Runs are written under `.simtools/runs/<run_id>/`.
- New run reports include `simtools.metrics.v1`.
- `simtools runs compare` returns `simtools.run_comparison.v1`.
- Dashboard helpers can read tools, experiments, runs, metrics, and comparison
  summaries without importing Streamlit or heavy simulator packages at module
  import time.

## Architecture Assessment

The core architecture is healthy:

- The manifest + adapter boundary keeps simulator-specific logic out of the
  CLI.
- The registry is the shared source of truth for CLI, dashboard, validation,
  and experiment loading.
- Heavy simulator imports are confined to opt-in adapter execution paths.
- `.simtools/` keeps generated artifacts and run records repository-local.
- The base test suite remains suitable for machines without GPU, datasets,
  Unity, Isaac Sim, MuJoCo, or simulator-specific Python packages.

The main architectural pressure is `src/simtools/core/experiments.py`, which now
owns experiment loading, run creation, report normalization, metrics, and run
comparison. It is still manageable, but future benchmark logic should be split
before this file becomes the place for every experiment concern.

## Documentation Assessment

The documentation set is now broadly aligned with the implementation:

- `README.md`: primary project entry and command overview.
- `QuickStart.md`: Chinese local usage path.
- `docs/01_CONSTRAINTS.md`: project guardrails and testing boundary.
- `docs/02_ARCHITECTURE.md`: system layers and module responsibilities.
- `docs/03_ADAPTER_CONTRACT.md`: adapter and experiment execution contract.
- `docs/04_CONFIG_SCHEMA.md`: manifest, experiment, report, and comparison
  schemas.
- `docs/05_CLI_SPEC.md`: command surface.
- `docs/06_DASHBOARD_SPEC.md`: dashboard tabs and helper boundaries.
- `docs/10_ROADMAP.md`: completed milestones and later work.
- `docs/17_EXPERIMENT_WORKBENCH.md`: experiment/run directory contract.
- `docs/18_EXPERIMENT_METRICS.md`: metrics and run comparison contract.

The remaining documentation gap is benchmark semantics. The project documents
operational metrics, but it does not yet define task-specific benchmark scores,
success criteria, or aggregation policies.

## Risks

- Real simulator environments are large and fragile across machines, GPU
  drivers, display servers, and Python/CUDA versions.
- `real_viewer` readiness is a truthful local state, not a guarantee that every
  user can reproduce the setup without manual asset and license steps.
- The current metrics layer is operational. It records run duration, status,
  artifacts, and log sizes, but it does not prove task success.
- Run artifacts are referenced rather than copied into `.simtools/runs/`; this
  keeps the core lightweight but limits portable replay packages.
- Dashboard views are inspection-oriented. They do not yet provide rich
  artifact previews, comparison exports, or benchmark report generation.

## Recommended Next Priorities

1. Define `benchmark_result` or `task_metrics` for task-specific scoring.
2. Split experiment concerns into focused modules before adding benchmark
   runners.
3. Add `simtools runs export` for JSON/CSV comparison snapshots.
4. Add dashboard comparison filters for time windows and experiment groups.
5. Add richer artifact previews for run-linked screenshots, videos, logs, and
   metadata.
6. Add reproducibility metadata such as git commit, SimTools version, active
   profile, and adapter readiness snapshot to run reports.
7. Keep new simulator integrations behind the same manifest + adapter + test +
   docs contract.

The concrete next implementation plan is
`plans/008-benchmark-runner-v0.4.md`. It intentionally keeps the first
Benchmark Runner slice metadata/report-driven: no new real simulator execution,
no asset downloads, no GUI launches, and no heavyweight imports in the base
environment.

## Release Gates

Before claiming a release-quality state, run:

```bash
pytest
python -m compileall -q src simtools tests
python -m simtools validate --json
python -m simtools real-status --strict
python -m simtools experiments list
python -m simtools experiments run ai2thor_floorplan1_navigation_smoke --dry-run
python -m simtools runs compare --json
git diff --check
```

These commands prove the lightweight test boundary, repository validation,
seven-tool readiness gate, experiment run path, metrics comparison path, and
basic formatting hygiene.
