# Benchmark Runner v0.4

Benchmark Runner v0.4 is the next layer after Experiment Workbench v0.2 and
Experiment Metrics v0.3. It is intentionally metadata/report-driven first: it
prepares benchmark-ready schemas, exports, and dashboard inspection without
executing new real simulator tasks.

The implementation plan is `plans/008-benchmark-runner-v0.4.md`.

## Purpose

The current metrics layer records operational facts such as status, duration,
artifact count, and log byte counts. Benchmark Runner v0.4 will add a place for
task-specific scoring and reproducibility metadata so future benchmark tasks can
be compared without changing the core run directory contract again.

## Boundaries

Benchmark Runner v0.4 must not:

- install simulator packages
- download datasets or assets
- accept EULAs
- launch GUI viewers during tests
- import heavy simulator packages at module import time
- add new simulator integrations
- treat operational metrics as benchmark success criteria

It should read existing run records, normalize benchmark metadata, export run
snapshots, and help the dashboard inspect benchmark fields.

## Schemas

### `task_metrics`

`task_metrics` holds task-specific measurements. The default unscored form is:

```json
{
  "schema_version": "simtools.task_metrics.v1",
  "success": null,
  "score": null,
  "steps_completed": null,
  "collisions": null,
  "custom": {}
}
```

`custom` is reserved for simulator- or task-specific metrics that do not yet
belong in the common schema.

### `benchmark_result`

`benchmark_result` describes benchmark state for a run:

```json
{
  "schema_version": "simtools.benchmark_result.v1",
  "status": "not_scored",
  "task_metrics": {
    "schema_version": "simtools.task_metrics.v1",
    "success": null,
    "score": null,
    "steps_completed": null,
    "collisions": null,
    "custom": {}
  }
}
```

Initial statuses stay simple:

- `not_scored`: metadata exists, but no benchmark scoring has run
- `scored`: task metrics were computed
- `failed`: scoring failed and should include a message

### `reproducibility`

`reproducibility` records local, non-mutating provenance:

```json
{
  "schema_version": "simtools.reproducibility.v1",
  "python": "3.11.x",
  "executable": "/path/to/python",
  "platform": "linux",
  "git_commit": "<commit-or-empty>",
  "simtools_version": "<version-or-empty>"
}
```

This metadata should come from local process state and existing helper data. It
must not call external package managers or real simulator code.

## CLI

`runs compare` remains the interactive summary command. Benchmark Runner v0.4
adds export commands:

```bash
python -m simtools runs export --format json
python -m simtools runs export --format csv
```

`runs export` reads `.simtools/runs/` only. It does not execute experiments,
call adapters, launch viewers, or mutate artifacts. JSON output uses
`simtools.run_export.v1`; CSV output includes run identity, status, metrics
schema, benchmark status, and report path.

## Dashboard Behavior

The dashboard exposes benchmark-oriented fields in Run Detail and Run History
without importing Streamlit at module import time:

- metrics schema
- artifact count
- benchmark status
- report path
- artifact references
- future task-specific metrics

The dashboard may preview existing artifacts, but it must not generate new
simulator outputs.

## Module Split

Benchmark logic should not keep growing `src/simtools/core/experiments.py`.
The split is:

- `experiments.py`: experiment config loading, run creation, run-store helpers
- `benchmarking.py`: task metrics, benchmark result, reproducibility metadata,
  export helpers
- `streamlit_app.py`: dashboard helper wrappers and Streamlit rendering only
- `main.py`: CLI wiring only

## Verification Gate

When Benchmark Runner v0.4 is implemented, run:

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

`real-status --strict` must remain 7/7.
