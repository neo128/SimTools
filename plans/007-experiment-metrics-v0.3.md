# Experiment Metrics v0.3 Implementation Plan

**Goal:** Add operational metrics and run comparison on top of Experiment
Workbench v0.2 while preserving SimTools' lightweight core boundary.

**Scope**

- Standard `metrics` block in new `report.json` files.
- Compatibility normalization for older reports without metrics.
- Core `compare_runs` helper shared by CLI and dashboard.
- `python -m simtools runs compare` with JSON/table output and filters.
- Dashboard Run History filters and comparison summary.
- Docs for metrics schema, CLI, dashboard, roadmap, and quick start.

**Verification**

- `pytest`
- `python -m compileall -q src simtools tests`
- `python -m simtools validate --json`
- `python -m simtools real-status --strict`
- `python -m simtools experiments run ai2thor_floorplan1_navigation_smoke --dry-run`
- `python -m simtools runs compare --json`
- `git diff --check`

**Status:** complete for the first operational metrics and run comparison
slice.
