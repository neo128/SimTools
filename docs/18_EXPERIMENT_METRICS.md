# Experiment Metrics v0.3

SimTools v0.3 adds a small standard metrics layer to Experiment Workbench run
reports. The goal is comparison and filtering, not a full benchmark scoring
system.

## Metrics Schema

Each new `report.json` contains:

```json
{
  "metrics": {
    "schema_version": "simtools.metrics.v1",
    "success": false,
    "dry_run": true,
    "duration_seconds": 0.002,
    "artifact_count": 0,
    "stdout_bytes": 0,
    "stderr_bytes": 0,
    "max_steps": 1
  }
}
```

Rules:

- `schema_version` is fixed at `simtools.metrics.v1` for this release.
- `success` is true only for completed real-run statuses such as `passed`.
- Dry-runs usually have `status: planned` and `success: false`.
- `artifact_count` counts artifact references recorded in the run report.
- `stdout_bytes` and `stderr_bytes` measure the captured log files.
- Older v0.2 reports are normalized on read so dashboards and CLI comparison
  can still inspect historical runs.

## Run Comparison Payload

`compare_runs` returns:

```json
{
  "schema_version": "simtools.run_comparison.v1",
  "filters": {
    "experiment_id": null,
    "tool_id": null,
    "status": null,
    "dry_run": null
  },
  "summary": {
    "run_count": 1,
    "experiment_count": 1,
    "tool_count": 1,
    "status_counts": {"planned": 1},
    "dry_run_count": 1,
    "success_count": 0,
    "total_artifacts": 0,
    "average_duration_seconds": 0.002
  },
  "runs": []
}
```

Comparison rows include run id, experiment id, tool id, status, dry-run flag,
duration, artifact count, success flag, metrics, run directory, and report path.

## CLI

```bash
python -m simtools runs compare
python -m simtools runs compare --json
python -m simtools runs compare --tool ai2thor
python -m simtools runs compare --experiment ai2thor_floorplan1_navigation_smoke
python -m simtools runs compare --status planned --dry-run
```

The command reads only `.simtools/runs/` metadata and log files. It does not
invoke adapters or import simulator packages.

## Dashboard

The Run History tab exposes filters for tool, experiment, status, and dry-run
state, then renders comparison rows plus the summary payload. Dashboard helper
functions remain importable without Streamlit.

## Limits

- v0.3 metrics are operational metrics, not benchmark scores.
- No leaderboard, statistical significance, or task-specific success criteria
  are defined yet.
- Large artifacts are still referenced rather than copied into run directories.
