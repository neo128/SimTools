# Experiment Workbench v0.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use Superpowers-style verification before completion. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a lightweight, config-driven experiment layer over the seven real-viewer simulator adapters.

**Architecture:** Experiments are YAML configs under `configs/experiments/` loaded into typed Pydantic models by `simtools.core.experiments`. Runs are repository-local records under `.simtools/runs/<timestamp>_<experiment_id>/`, with manifest snapshots, environment metadata, logs, reports, and artifact references. CLI and dashboard read the same experiment/run helpers.

**Tech Stack:** Python 3.11, Pydantic v2, PyYAML, Typer, Rich, pytest, Streamlit helper functions without importing Streamlit at module import time.

---

### Task 1: Experiment Models And Config Loading

**Files:**
- Create: `src/simtools/core/experiments.py`
- Create: `configs/experiments/*.yaml`
- Test: `tests/test_experiments.py`

- [x] Write failing tests for loading all experiment YAML files and enforcing the required fields.
- [x] Implement `ExperimentSpec`, experiment directory helpers, `load_experiment`, and `load_experiments`.
- [x] Add the three requested experiment YAML files for AI2-THOR, Habitat, and ManiSkill.
- [x] Run `pytest tests/test_experiments.py`.

### Task 2: Run Artifact Store

**Files:**
- Modify: `src/simtools/core/experiments.py`
- Test: `tests/test_experiments.py`

- [x] Write failing tests for dry-run artifact creation under `.simtools/runs/<timestamp>_<experiment_id>/`.
- [x] Implement run ID sanitization, run directory creation, `run.yaml`, `manifest_snapshot.yaml`, `environment.json`, `stdout.log`, `stderr.log`, `report.json`, and `artifacts/`.
- [x] Include `duration_seconds` and the originating CLI `command` in `report.json`.
- [x] Add run listing and report loading helpers.
- [x] Run `pytest tests/test_experiments.py`.

### Task 3: Experiment Execution Strategy

**Files:**
- Modify: `src/simtools/core/experiments.py`
- Test: `tests/test_experiments.py`

- [x] Write failing tests proving dry-runs do not execute real GUI/viewer paths.
- [x] Implement `run_experiment` so dry-run records metadata only.
- [x] Route non-dry-run AI2-THOR to adapter smoke, Habitat to visual render, and ManiSkill to visual rollout; other tools stay metadata-only until expanded.
- [x] Capture adapter stdout/stderr fields into run logs and artifact references into `report.json`.
- [x] Run `pytest tests/test_experiments.py`.

### Task 4: CLI Commands

**Files:**
- Modify: `src/simtools/cli/main.py`
- Test: `tests/test_cli.py` or `tests/test_experiments.py`

- [x] Write failing CLI tests for `experiments list`, `experiments info`, `experiments run --dry-run`, `experiments report`, and `runs list`.
- [x] Add Typer subcommands that call the experiment helpers without hardcoding simulator metadata in CLI handlers.
- [x] Run targeted CLI tests.

### Task 5: Dashboard Helpers And Views

**Files:**
- Modify: `src/simtools/ui/streamlit_app.py`
- Test: `tests/test_dashboard.py` or `tests/test_experiments.py`

- [x] Write failing tests for dashboard run history helper behavior.
- [x] Add Experiment Library, Run History, and Run Detail tabs.
- [x] Render `report.json` content and artifact paths from `.simtools/runs/`.
- [x] Run dashboard tests without importing Streamlit at module import time.

### Task 6: Documentation And Verification

**Files:**
- Create: `docs/17_EXPERIMENT_WORKBENCH.md`
- Modify: `README.md`
- Modify: `QuickStart.md`
- Modify: `docs/10_ROADMAP.md`

- [x] Document the experiment schema, run directory contract, CLI examples, dashboard additions, and first-phase real-run limits.
- [x] Run the required verification commands from the goal.
- [x] Review `git diff --check` and summarize risks and next-stage work.
