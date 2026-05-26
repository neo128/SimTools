# Benchmark Runner v0.4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use Superpowers-style
> verification before completion. Steps use checkbox (`- [ ]`) syntax for
> tracking.

**Goal:** Add the first benchmark-ready layer on top of Experiment Workbench
without turning SimTools into a real simulator executor or heavyweight
dependency bundle.

**Architecture:** Keep benchmark logic metadata/report-driven. Split
task-specific scoring, reproducibility metadata, and export helpers out of
`src/simtools/core/experiments.py` into focused core modules. CLI and dashboard
must consume the same benchmark/run helpers and must not call adapters during
comparison, export, or dashboard inspection.

**Tech Stack:** Python 3.11+, Pydantic v2, PyYAML, Typer, Rich, pytest,
standard-library `csv` and `json`.

**Status:** Implemented on main as the first metadata/report-driven Benchmark
Runner slice. Remaining benchmark work is future task-specific scoring,
adapter-owned benchmark execution, artifact preview, and aggregation policy.

---

## Scope

This plan adds a benchmark-ready contract, not a full scientific leaderboard.
It should produce durable run metadata that future real benchmark tasks can
score consistently.

In scope:

- `task_metrics` schema for task-specific scores and measurements
- `benchmark_result` schema for per-run benchmark state
- run reproducibility metadata
- `simtools runs export` for JSON and CSV snapshots
- dashboard helpers for metrics/artifact inspection
- module split so future benchmark code does not overgrow
  `core/experiments.py`

Out of scope:

- executing new real simulator tasks
- downloading datasets or assets
- launching GUI viewers
- adding new simulator integrations
- defining leaderboard statistics or significance tests

## Task 1: Benchmark Schema Module

**Files:**

- Create: `src/simtools/core/benchmarking.py`
- Create: `tests/test_benchmarking.py`
- Modify: `docs/04_CONFIG_SCHEMA.md`

- [x] **Step 1: Write failing tests for normalized task metrics**

```python
from simtools.core.benchmarking import normalize_task_metrics


def test_task_metrics_defaults_to_unscored_result():
    metrics = normalize_task_metrics({})

    assert metrics == {
        "schema_version": "simtools.task_metrics.v1",
        "success": None,
        "score": None,
        "steps_completed": None,
        "collisions": None,
        "custom": {},
    }
```

Run:

```bash
pytest tests/test_benchmarking.py::test_task_metrics_defaults_to_unscored_result -q
```

Expected: fail because `simtools.core.benchmarking` does not exist.

- [x] **Step 2: Implement minimal schema helpers**

Add:

- `TASK_METRICS_SCHEMA_VERSION = "simtools.task_metrics.v1"`
- `BENCHMARK_RESULT_SCHEMA_VERSION = "simtools.benchmark_result.v1"`
- `normalize_task_metrics(payload: dict[str, object]) -> dict[str, object]`
- `build_benchmark_result(status: str, task_metrics: dict[str, object] | None)`

- [x] **Step 3: Verify targeted tests pass**

```bash
pytest tests/test_benchmarking.py -q
```

- [x] **Step 4: Document the schema**

Add `task_metrics` and `benchmark_result` examples to
`docs/04_CONFIG_SCHEMA.md`.

## Task 2: Reproducibility Metadata

**Files:**

- Modify: `src/simtools/core/benchmarking.py`
- Modify: `src/simtools/core/experiments.py`
- Test: `tests/test_experiments.py`

- [x] **Step 1: Write a failing dry-run report test**

```python
def test_dry_run_report_includes_reproducibility_metadata(tmp_path):
    result = run_experiment(
        get_experiment("ai2thor_floorplan1_navigation_smoke"),
        run_store=RunStore(root=tmp_path / "runs"),
        dry_run=True,
    )
    report = RunStore(root=tmp_path / "runs").load_report(result["run_id"])

    assert report["reproducibility"]["schema_version"] == "simtools.reproducibility.v1"
    assert "python" in report["reproducibility"]
    assert "platform" in report["reproducibility"]
    assert "git_commit" in report["reproducibility"]
    assert report["benchmark_result"]["schema_version"] == "simtools.benchmark_result.v1"
```

Expected: fail because reports do not include these fields.

- [x] **Step 2: Implement lightweight metadata collection**

Use existing environment data where possible. Add only local, non-mutating
fields:

- schema version
- Python executable/version
- platform
- current git commit or empty string if unavailable
- SimTools package version if available

- [x] **Step 3: Verify experiment tests**

```bash
pytest tests/test_experiments.py tests/test_benchmarking.py -q
```

## Task 3: Run Export CLI

**Files:**

- Modify: `src/simtools/core/benchmarking.py`
- Modify: `src/simtools/cli/main.py`
- Test: `tests/test_experiments.py` or `tests/test_cli.py`
- Docs: `docs/05_CLI_SPEC.md`

- [x] **Step 1: Write failing CLI tests for JSON and CSV export**

```python
def test_runs_export_json_and_csv(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMTOOLS_RUNS_DIR", str(tmp_path / "runs"))
    run = runner.invoke(app, ["experiments", "run", "ai2thor_floorplan1_navigation_smoke"])
    assert run.exit_code == 0

    json_result = runner.invoke(app, ["runs", "export", "--format", "json"])
    assert json_result.exit_code == 0
    assert '"schema_version": "simtools.run_export.v1"' in json_result.output

    csv_result = runner.invoke(app, ["runs", "export", "--format", "csv"])
    assert csv_result.exit_code == 0
    assert "run_id,experiment_id,tool_id,status,dry_run" in csv_result.output
```

Expected: fail because `runs export` does not exist.

- [x] **Step 2: Implement export helpers**

Add:

- `RUN_EXPORT_SCHEMA_VERSION = "simtools.run_export.v1"`
- `export_runs_json(comparison: dict[str, object])`
- `export_runs_csv(comparison: dict[str, object])`

CSV must use only standard-library `csv` and in-memory `io.StringIO`.

- [x] **Step 3: Add CLI command**

Add:

```bash
python -m simtools runs export --format json
python -m simtools runs export --format csv
```

The command must read `.simtools/runs/` only.

## Task 4: Dashboard Metrics And Artifact Inspection

**Files:**

- Modify: `src/simtools/ui/streamlit_app.py`
- Test: `tests/test_dashboard.py`
- Docs: `docs/06_DASHBOARD_SPEC.md`

- [x] **Step 1: Write helper tests**

```python
from simtools.ui.streamlit_app import run_metric_summary


def test_run_metric_summary_extracts_benchmark_fields():
    summary = run_metric_summary({
        "metrics": {"schema_version": "simtools.metrics.v1", "artifact_count": 2},
        "benchmark_result": {"status": "not_scored"},
    })

    assert summary["metrics_schema"] == "simtools.metrics.v1"
    assert summary["artifact_count"] == 2
    assert summary["benchmark_status"] == "not_scored"
```

- [x] **Step 2: Add dashboard helper and view wiring**

Expose benchmark status, metrics schema, artifact count, and report path in Run
Detail without importing Streamlit at module import time.

## Task 5: Documentation And Release Verification

**Files:**

- Modify: `docs/20_BENCHMARK_RUNNER.md`
- Modify: `README.md`
- Modify: `QuickStart.md`
- Modify: `docs/10_ROADMAP.md`
- Modify: `docs/12_RELEASE_CHECKLIST.md`

- [x] **Step 1: Keep the benchmark boundary current**

Update `docs/20_BENCHMARK_RUNNER.md` with any schema or command changes made
during implementation. It must continue to state that v0.4 is
metadata/report-driven and does not execute new real simulator tasks.

- [x] **Step 2: Run full verification**

```bash
pytest
python -m compileall -q src simtools tests
python -m simtools validate --json
python -m simtools real-status --strict
python -m simtools experiments list
python -m simtools experiments run ai2thor_floorplan1_navigation_smoke --dry-run
python -m simtools runs list
python -m simtools runs compare --json
python -m simtools runs export --format json
python -m simtools runs export --format csv
git diff --check
```

Expected: all commands exit 0, and `real-status --strict` remains 7/7.

## Completion Criteria

- New benchmark fields are present in dry-run reports.
- Legacy v0.2/v0.3 reports can still be read.
- `runs compare` remains backward-compatible.
- `runs export` works for JSON and CSV.
- Dashboard helpers expose benchmark/metrics inspection data.
- No heavy simulator package is imported at module import time.
- Tests do not launch GUI windows or download assets.
- Documentation explains the benchmark boundary and future scoring limits.
