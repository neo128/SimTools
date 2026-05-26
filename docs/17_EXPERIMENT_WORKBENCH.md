# Experiment Workbench v0.2/v0.3

SimTools Experiment Workbench adds a lightweight experiment layer over the
existing seven-tool registry. It does not install simulators, download assets,
accept licenses, or launch GUI windows during tests.

## Design

The workbench is config-driven and adapter-backed:

1. YAML files in `configs/experiments/` describe experiment intent.
2. `ExperimentSpec` validates the schema, filename/id match, and registry-backed
   `tool_id` references.
3. `RunStore` creates repository-local run directories under `.simtools/runs/`.
4. CLI and dashboard views read the same experiment and run helpers.
5. Dry-run records metadata only; real execution is opt-in through
   `--no-dry-run` and is routed through existing adapter-owned methods.

## Experiment Specs

Experiment configs live under `configs/experiments/` and are validated by
`ExperimentSpec` in `src/simtools/core/experiments.py`.

Required fields:

- `id`: stable lowercase experiment id, matching the YAML filename stem.
- `tool_id`: simulator tool id from `configs/tools/`.
- `scene`: scene or environment identifier passed to the adapter path.
- `task`: short task label, such as `navigation_smoke` or `visual_rollout`.
- `seed`: integer seed recorded in run metadata.
- `max_steps`: positive integer step budget.
- `output`: structured output expectations, such as artifact kinds.
- `notes`: list of human-readable constraints or setup notes.

The YAML filename stem must match `id`. A config that references an unknown
`tool_id` fails loading with a message that includes the experiment path, the
bad id, and the valid tool ids.

Initial configs:

- `ai2thor_floorplan1_navigation_smoke`
- `habitat_skokloster_visual_observation`
- `maniskill_pickcube_visual_rollout`

## Run Directory Contract

Each experiment run creates:

```text
.simtools/runs/<timestamp>_<experiment_id>/
  run.yaml
  manifest_snapshot.yaml
  environment.json
  stdout.log
  stderr.log
  report.json
  artifacts/
```

`report.json` is the primary machine-readable summary. It includes the run id,
experiment id, tool id, scene, task, seed, max steps, dry-run flag, status,
message, start/end timestamps, duration, CLI command, standard metrics, output
expectations, notes, adapter result, benchmark metadata, reproducibility
metadata, and artifact references. Workbench records artifact references
instead of copying large files into the run directory.

Minimum `report.json` keys:

- `run_id`
- `experiment_id`
- `tool_id`
- `scene`
- `task`
- `dry_run`
- `status`
- `started_at`
- `finished_at`
- `duration_seconds`
- `artifacts`
- `command`
- `message`
- `metrics`
- `benchmark_result`
- `reproducibility`

`metrics.schema_version` is `simtools.metrics.v1`. See
`docs/18_EXPERIMENT_METRICS.md` for the metrics and run-comparison contract.
`benchmark_result.schema_version` is `simtools.benchmark_result.v1`. See
`docs/20_BENCHMARK_RUNNER.md` for the benchmark metadata and export boundary.

## CLI

```bash
python -m simtools experiments list
python -m simtools experiments info ai2thor_floorplan1_navigation_smoke
python -m simtools experiments run ai2thor_floorplan1_navigation_smoke --dry-run
python -m simtools experiments run habitat_skokloster_visual_observation --no-dry-run
python -m simtools experiments report <run_id>
python -m simtools runs list
python -m simtools runs compare --json
python -m simtools runs export --format json
python -m simtools runs export --format csv
```

`experiments run` is dry-run by default. `--dry-run` writes the same
run-directory structure as a real run, but it does not call adapter execution
paths. Use `--no-dry-run` to opt in to real execution.

Errors are intended to be actionable: unknown experiments list valid
experiment ids, invalid experiment configs include the YAML path, and unknown
tool ids list the valid registry ids.

## First-Phase Real Run Strategy

- AI2-THOR: non-dry-run calls the existing `smoke` path and records the PPM
  artifact reference when the local AI2-THOR environment is ready.
- Habitat: non-dry-run calls the existing visual render path and records the
  PNG artifact reference when Habitat and test scenes are already available.
- ManiSkill: non-dry-run calls the existing visual rollout path and records the
  MP4 artifact reference when ManiSkill is installed.
- RoboCasa365, MolmoSpaces, OmniGibson, and BEHAVIOR-1K: Workbench v0.2 records
  experiment metadata and supports dry-run reporting first. Real experiment
  execution can be added later through adapter-owned paths.

## Dashboard

The Streamlit dashboard now includes:

- Experiment Library: loaded configs from `configs/experiments/`.
- Run History: run rows from `.simtools/runs/`.
- Run History comparison: filters for tool, experiment, status, and dry-run
  state plus standard metrics summary.
- Run Detail: selected `report.json` content, run/report/artifact paths, and
  artifact references.

The dashboard helper functions remain importable without Streamlit and without
heavy simulator imports.

## Validation

`python -m simtools validate --json` validates tool manifests, profiles,
adapters, and experiment configs. It reports `experiment_count` and fails if an
experiment references an unknown tool id.

## Limits

- Workbench v0.3 defines operational metrics, not benchmark scores.
- It does not copy large simulator artifacts into `.simtools/runs/`; it records
  references so existing adapter artifact stores remain the source of truth.
- It does not auto-install simulator packages, download datasets, accept EULAs,
  assume a GPU, or launch real GUI windows from tests.
- Real experiment execution is intentionally limited to existing adapter paths
  for AI2-THOR, Habitat, and ManiSkill in this slice.
