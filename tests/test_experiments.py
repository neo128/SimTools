import json
from pathlib import Path

from typer.testing import CliRunner

from simtools.cli.main import app
from simtools.core.errors import ConfigError
from simtools.core.experiments import (
    ExperimentSpec,
    RunStore,
    compare_runs,
    get_experiment,
    load_experiment,
    load_experiments,
    run_experiment,
)
from simtools.core.registry import ToolRegistry
from simtools.ui.streamlit_app import (
    load_experiment_library,
    load_run_comparison,
    load_run_history,
)


runner = CliRunner()


def test_load_experiment_configs_from_default_directory():
    experiments = load_experiments()
    ids = [experiment.id for experiment in experiments]

    assert ids == [
        "ai2thor_floorplan1_navigation_smoke",
        "habitat_skokloster_visual_observation",
        "maniskill_pickcube_visual_rollout",
    ]
    for experiment in experiments:
        assert experiment.tool_id in ToolRegistry.from_configs().ids()
        assert experiment.scene
        assert experiment.task
        assert isinstance(experiment.seed, int)
        assert experiment.max_steps > 0
        assert isinstance(experiment.output, dict)
        assert isinstance(experiment.notes, list)


def test_experiment_filename_must_match_id(tmp_path):
    path = tmp_path / "expected_id.yaml"
    path.write_text(
        """
id: different_id
tool_id: ai2thor
scene: FloorPlan1
task: navigation_smoke
seed: 0
max_steps: 1
output:
  primary: smoke_frame
notes: []
""".lstrip(),
        encoding="utf-8",
    )

    try:
        load_experiment(path)
    except ConfigError as exc:
        message = str(exc)
    else:
        raise AssertionError("load_experiment should reject filename/id mismatch")

    assert "different_id" in message
    assert "expected_id" in message
    assert "filename stem" in message


def test_experiment_tool_id_must_exist_in_registry(tmp_path):
    path = tmp_path / "unknown_tool_experiment.yaml"
    path.write_text(
        """
id: unknown_tool_experiment
tool_id: missing_simulator
scene: sample_scene
task: sample_task
seed: 0
max_steps: 1
output:
  primary: sample
notes: []
""".lstrip(),
        encoding="utf-8",
    )

    try:
        load_experiments(tmp_path)
    except ConfigError as exc:
        message = str(exc)
    else:
        raise AssertionError("load_experiments should reject unknown tool_id")

    assert "unknown_tool_experiment.yaml" in message
    assert "missing_simulator" in message
    assert "unknown tool_id" in message
    assert "Valid tool ids" in message


def test_dry_run_experiment_creates_required_run_files(tmp_path):
    registry = ToolRegistry.from_configs()
    experiment = get_experiment("ai2thor_floorplan1_navigation_smoke")
    store = RunStore(root=tmp_path / "runs")

    result = run_experiment(
        experiment,
        registry=registry,
        run_store=store,
        dry_run=True,
    )

    run_dir = Path(result["run_dir"])
    assert run_dir.name.endswith("_ai2thor_floorplan1_navigation_smoke")
    assert (run_dir / "run.yaml").is_file()
    assert (run_dir / "manifest_snapshot.yaml").is_file()
    assert (run_dir / "environment.json").is_file()
    assert (run_dir / "stdout.log").is_file()
    assert (run_dir / "stderr.log").is_file()
    assert (run_dir / "report.json").is_file()
    assert (run_dir / "artifacts").is_dir()

    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    assert {
        "run_id",
        "experiment_id",
        "tool_id",
        "scene",
        "task",
        "dry_run",
        "status",
        "started_at",
        "finished_at",
        "duration_seconds",
        "artifacts",
        "command",
        "message",
    } <= set(report)
    assert report["experiment_id"] == experiment.id
    assert report["tool_id"] == "ai2thor"
    assert report["dry_run"] is True
    assert report["status"] == "planned"
    assert report["artifacts"] == []
    assert isinstance(report["duration_seconds"], float)
    assert report["duration_seconds"] >= 0
    assert report["command"] == (
        "python -m simtools experiments run "
        "ai2thor_floorplan1_navigation_smoke --dry-run"
    )
    assert report["metrics"]["schema_version"] == "simtools.metrics.v1"
    assert report["metrics"]["duration_seconds"] == report["duration_seconds"]
    assert report["metrics"]["artifact_count"] == 0
    assert report["metrics"]["stdout_bytes"] == 0
    assert report["metrics"]["stderr_bytes"] == 0
    assert report["metrics"]["dry_run"] is True
    assert report["metrics"]["success"] is False


def test_dry_run_report_includes_benchmark_and_reproducibility_metadata(tmp_path):
    store = RunStore(root=tmp_path / "runs")

    result = run_experiment(
        get_experiment("ai2thor_floorplan1_navigation_smoke"),
        run_store=store,
        dry_run=True,
    )

    report = store.load_report(result["run_id"])
    assert report["benchmark_result"] == {
        "schema_version": "simtools.benchmark_result.v1",
        "status": "not_scored",
        "task_metrics": {
            "schema_version": "simtools.task_metrics.v1",
            "success": None,
            "score": None,
            "steps_completed": None,
            "collisions": None,
            "custom": {},
        },
    }
    assert report["reproducibility"]["schema_version"] == "simtools.reproducibility.v1"
    assert "python" in report["reproducibility"]
    assert "executable" in report["reproducibility"]
    assert "platform" in report["reproducibility"]
    assert "git_commit" in report["reproducibility"]
    assert "simtools_version" in report["reproducibility"]


def test_run_store_lists_and_loads_reports(tmp_path):
    store = RunStore(root=tmp_path / "runs")
    experiment = get_experiment("habitat_skokloster_visual_observation")
    first = run_experiment(experiment, run_store=store, dry_run=True)

    runs = store.list_runs()

    assert [run["run_id"] for run in runs] == [first["run_id"]]
    assert runs[0]["experiment_id"] == experiment.id
    assert runs[0]["status"] == "planned"
    assert store.load_report(first["run_id"])["experiment_id"] == experiment.id


def test_run_store_comparison_summarizes_and_filters_runs(tmp_path):
    store = RunStore(root=tmp_path / "runs")
    ai2thor = get_experiment("ai2thor_floorplan1_navigation_smoke")
    maniskill = get_experiment("maniskill_pickcube_visual_rollout")
    run_experiment(ai2thor, run_store=store, dry_run=True)
    run_experiment(maniskill, run_store=store, dry_run=True)

    comparison = compare_runs(store)

    assert comparison["schema_version"] == "simtools.run_comparison.v1"
    assert comparison["summary"]["run_count"] == 2
    assert comparison["summary"]["experiment_count"] == 2
    assert comparison["summary"]["tool_count"] == 2
    assert comparison["summary"]["status_counts"] == {"planned": 2}
    assert comparison["summary"]["dry_run_count"] == 2
    assert comparison["summary"]["success_count"] == 0
    assert comparison["summary"]["total_artifacts"] == 0
    assert comparison["summary"]["average_duration_seconds"] >= 0
    assert {row["experiment_id"] for row in comparison["runs"]} == {
        ai2thor.id,
        maniskill.id,
    }
    assert all(row["metrics"]["schema_version"] == "simtools.metrics.v1" for row in comparison["runs"])

    filtered = compare_runs(store, tool_id="ai2thor")

    assert filtered["filters"]["tool_id"] == "ai2thor"
    assert filtered["summary"]["run_count"] == 1
    assert filtered["runs"][0]["experiment_id"] == ai2thor.id


def test_legacy_run_report_without_v04_fields_still_loads_and_compares(tmp_path):
    run_dir = tmp_path / "runs" / "20260526T000000000000Z_legacy_experiment"
    run_dir.mkdir(parents=True)
    (run_dir / "stdout.log").write_text("", encoding="utf-8")
    (run_dir / "stderr.log").write_text("", encoding="utf-8")
    (run_dir / "report.json").write_text(
        json.dumps(
            {
                "experiment_id": "legacy_experiment",
                "tool_id": "ai2thor",
                "status": "planned",
                "dry_run": True,
                "started_at": "2026-05-26T00:00:00+00:00",
                "finished_at": "2026-05-26T00:00:00+00:00",
                "duration_seconds": 0.0,
                "command": "python -m simtools experiments run legacy_experiment --dry-run",
                "artifacts": [],
                "max_steps": 1,
            }
        ),
        encoding="utf-8",
    )
    store = RunStore(root=tmp_path / "runs")

    report = store.load_report(run_dir.name)
    comparison = compare_runs(store)

    assert report["metrics"]["schema_version"] == "simtools.metrics.v1"
    assert report["experiment_id"] == "legacy_experiment"
    assert comparison["summary"]["run_count"] == 1
    assert comparison["runs"][0]["experiment_id"] == "legacy_experiment"
    assert comparison["runs"][0]["metrics"]["schema_version"] == "simtools.metrics.v1"


def test_experiment_dry_run_does_not_call_real_adapter_paths(tmp_path, monkeypatch):
    class ExplodingAdapter:
        tool_id = "maniskill"

        def smoke(self, *, dry_run=False):
            raise AssertionError("smoke should not run during experiment dry-run")

        def launch_viewer(self, *, dry_run=True, execute=False, **options):
            raise AssertionError("viewer should not run during experiment dry-run")

    import simtools.core.experiments as experiments_module

    monkeypatch.setattr(experiments_module, "get_adapter", lambda manifest: ExplodingAdapter())
    spec = ExperimentSpec(
        id="maniskill_pickcube_visual_rollout",
        tool_id="maniskill",
        scene="PickCube-v1",
        task="visual_rollout",
        seed=0,
        max_steps=8,
        output={"kind": "mp4"},
        notes=[],
    )

    result = run_experiment(spec, run_store=RunStore(root=tmp_path / "runs"), dry_run=True)

    assert result["status"] == "planned"
    assert result["dry_run"] is True


def test_failed_real_experiment_still_writes_report(tmp_path, monkeypatch):
    class FailingAdapter:
        tool_id = "habitat"

        def launch_viewer(self, *, dry_run=True, execute=False, **options):
            raise RuntimeError("viewer exploded")

    import simtools.core.experiments as experiments_module

    monkeypatch.setattr(experiments_module, "get_adapter", lambda manifest: FailingAdapter())
    store = RunStore(root=tmp_path / "runs")

    result = run_experiment(
        get_experiment("habitat_skokloster_visual_observation"),
        run_store=store,
        dry_run=False,
    )

    report = store.load_report(result["run_id"])
    assert result["status"] == "failed"
    assert report["status"] == "failed"
    assert "viewer exploded" in report["message"]
    assert Path(result["run_dir"], "stderr.log").read_text(encoding="utf-8")


def test_cli_experiments_and_runs_dry_run(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMTOOLS_RUNS_DIR", str(tmp_path / "runs"))

    list_result = runner.invoke(app, ["experiments", "list"])
    assert list_result.exit_code == 0, list_result.output
    assert "ai2thor_floorplan1_navigation_smoke" in list_result.output

    info_result = runner.invoke(
        app,
        ["experiments", "info", "ai2thor_floorplan1_navigation_smoke"],
    )
    assert info_result.exit_code == 0, info_result.output
    assert "FloorPlan1" in info_result.output

    run_result = runner.invoke(
        app,
        ["experiments", "run", "ai2thor_floorplan1_navigation_smoke", "--dry-run"],
    )
    assert run_result.exit_code == 0, run_result.output
    run_payload = json.loads(run_result.output)
    assert run_payload["status"] == "planned"

    runs_result = runner.invoke(app, ["runs", "list", "--json"])
    assert runs_result.exit_code == 0, runs_result.output
    assert run_payload["run_id"] in runs_result.output

    report_result = runner.invoke(
        app,
        ["experiments", "report", run_payload["run_id"]],
    )
    assert report_result.exit_code == 0, report_result.output
    assert "ai2thor_floorplan1_navigation_smoke" in report_result.output

    compare_result = runner.invoke(app, ["runs", "compare", "--json"])
    assert compare_result.exit_code == 0, compare_result.output
    compare_payload = json.loads(compare_result.output)
    assert compare_payload["summary"]["run_count"] == 1
    assert compare_payload["runs"][0]["metrics"]["schema_version"] == "simtools.metrics.v1"


def test_cli_runs_export_json_and_csv(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMTOOLS_RUNS_DIR", str(tmp_path / "runs"))

    run_result = runner.invoke(
        app,
        ["experiments", "run", "ai2thor_floorplan1_navigation_smoke"],
    )
    assert run_result.exit_code == 0, run_result.output

    json_result = runner.invoke(app, ["runs", "export", "--format", "json"])
    assert json_result.exit_code == 0, json_result.output
    json_payload = json.loads(json_result.output)
    assert json_payload["schema_version"] == "simtools.run_export.v1"
    assert json_payload["comparison"]["schema_version"] == "simtools.run_comparison.v1"
    assert json_payload["comparison"]["summary"]["run_count"] == 1

    csv_result = runner.invoke(app, ["runs", "export", "--format", "csv"])
    assert csv_result.exit_code == 0, csv_result.output
    assert csv_result.output.splitlines()[0] == (
        "run_id,experiment_id,tool_id,status,dry_run,duration_seconds,"
        "artifact_count,success,metrics_schema,benchmark_status,report_path"
    )
    assert "ai2thor_floorplan1_navigation_smoke" in csv_result.output


def test_cli_experiment_run_defaults_to_dry_run_for_safety(tmp_path, monkeypatch):
    monkeypatch.setenv("SIMTOOLS_RUNS_DIR", str(tmp_path / "runs"))

    result = runner.invoke(
        app,
        ["experiments", "run", "ai2thor_floorplan1_navigation_smoke"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["dry_run"] is True
    assert payload["status"] == "planned"


def test_dashboard_helper_reads_run_history(tmp_path):
    store = RunStore(root=tmp_path / "runs")
    experiment = get_experiment("maniskill_pickcube_visual_rollout")
    run_experiment(experiment, run_store=store, dry_run=True)

    history = load_run_history(tmp_path / "runs")

    assert len(history) == 1
    assert history[0]["experiment_id"] == experiment.id
    assert history[0]["report"]["tool_id"] == "maniskill"


def test_dashboard_helpers_read_experiments_and_runs(tmp_path):
    experiments = load_experiment_library()
    store = RunStore(root=tmp_path / "runs")
    run_experiment(
        get_experiment("ai2thor_floorplan1_navigation_smoke"),
        run_store=store,
        dry_run=True,
    )
    runs = load_run_history(tmp_path / "runs")

    assert [experiment["id"] for experiment in experiments] == [
        "ai2thor_floorplan1_navigation_smoke",
        "habitat_skokloster_visual_observation",
        "maniskill_pickcube_visual_rollout",
    ]
    assert len(runs) == 1
    assert runs[0]["experiment_id"] == "ai2thor_floorplan1_navigation_smoke"


def test_dashboard_helper_reads_filtered_run_comparison(tmp_path):
    store = RunStore(root=tmp_path / "runs")
    run_experiment(
        get_experiment("ai2thor_floorplan1_navigation_smoke"),
        run_store=store,
        dry_run=True,
    )
    run_experiment(
        get_experiment("maniskill_pickcube_visual_rollout"),
        run_store=store,
        dry_run=True,
    )

    comparison = load_run_comparison(tmp_path / "runs", tool_id="maniskill")

    assert comparison["summary"]["run_count"] == 1
    assert comparison["runs"][0]["tool_id"] == "maniskill"
    assert comparison["runs"][0]["metrics"]["artifact_count"] == 0
