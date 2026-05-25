# Architecture

SimTools uses a layered architecture:

1. CLI layer: Typer commands for list, info, status, profiles, compare, doctor,
   run, view, artifacts, experiments, runs, validate, ui, and install-plan.
2. UI layer: Streamlit dashboard that reads the same registry, experiment
   library, and run history as the CLI.
3. Core service layer: registry, config loading, environment inspection,
   process planning, artifact storage, experiment runs, run metrics/comparison,
   and capability matrix generation.
4. Adapter layer: one light adapter per simulator.
5. Manifest/config layer: YAML manifests, profiles, and experiment specs.
6. Artifact/log layer: `.simtools/` output for screenshots, logs, smoke reports,
   run records, and future benchmark artifacts.

## Module Responsibilities

- `registry`: loads manifests and provides lookup/filter APIs.
- `config_loader`: parses YAML and validates it with Pydantic models.
- `environment`: reports local Python, OS, executable, and selected env data.
- `process_runner`: provides dry-run and subprocess execution helpers.
- `artifact_store`: keeps outputs under `.simtools/artifacts/`.
- `experiments`: loads experiment YAML, creates `.simtools/runs/` records,
  records standard metrics, compares run history, and routes first-phase real
  runs through existing adapter paths.
- `capability_matrix`: converts manifests into comparison rows and markdown.
- `status`: aggregates adapter diagnostics into local status views.
- `readiness`: reports whether each registered tool has verified local smoke
  and visualization.
- `validation`: checks manifest/profile/experiment/adapter wiring without heavy
  imports.

## Extension Mechanism

To add a simulator:

1. Add `configs/tools/<tool_id>.yaml`.
2. Add `src/simtools/adapters/<tool_id>.py`.
3. Register the adapter in `src/simtools/adapters/__init__.py`.
4. Add or update contract tests.
5. Update `docs/07_TOOL_MATRIX.md` and `docs/08_INSTALLATION_PROFILES.md`.
6. Add a dry-run smoke command and sample manual commands.
7. Add readiness metadata that truthfully marks planned, package-smoke, or
   real-viewer status.

## Local Run Modes

- Metadata-only mode: list and compare tools without installed simulators.
- Smoke mode: run a minimal non-destructive test when a simulator is installed.
- Full install mode: future opt-in workflow that executes an install profile.
- Viewer mode: opt-in GUI launch, dry-run by default.
- Real readiness mode: strict release gate for local smoke and visualization.
- Experiment mode: config-driven dry-runs and opt-in first-phase real runs with
  records under `.simtools/runs/`.
- Metrics mode: repository-local run comparison without simulator imports or
  adapter execution.
- Benchmark mode: future metrics-oriented task execution and artifact capture.

## Risks

- GPU availability varies across machines.
- Datasets and simulator assets can be very large.
- GUI and headless behavior varies across Linux, macOS, Windows, and remote
  sessions.
- Simulator APIs change over time.
- Some tools require strict versions of Python, CUDA, MuJoCo, Isaac Sim, or
  system packages.
