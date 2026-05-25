from typer.testing import CliRunner

from simtools.cli.main import app


runner = CliRunner()


def test_cli_status_profiles_validate_and_artifacts():
    for args in (
        ["status"],
        ["real-status"],
        ["profiles"],
        ["validate"],
        ["artifacts"],
    ):
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output


def test_cli_run_smoke_dry_run_and_no_save_report():
    result = runner.invoke(
        app,
        ["run", "ai2thor", "--mode", "smoke", "--dry-run", "--no-save-report"],
    )
    assert result.exit_code == 0, result.output
    assert "planned" in result.output


def test_cli_view_ai2thor_dry_run_with_scene_options():
    result = runner.invoke(
        app,
        [
            "view",
            "ai2thor",
            "--dry-run",
            "--scene",
            "FloorPlan1",
            "--width",
            "300",
            "--height",
            "300",
            "--max-actions",
            "0",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "--execute" in result.output
    assert "--max-actions 0" in result.output


def test_cli_view_ai2thor_ui_dry_run():
    result = runner.invoke(
        app,
        [
            "view",
            "ai2thor",
            "--ui",
            "--dry-run",
            "--scene",
            "FloorPlan1",
            "--width",
            "300",
            "--height",
            "300",
            "--port",
            "8502",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "--ui --execute" in result.output
    assert "--port 8502" in result.output


def test_cli_install_plan_all_tools():
    result = runner.invoke(app, ["install-plan"])
    assert result.exit_code == 0, result.output
    assert "ai2thor" in result.output
    assert "Dry-run only" in result.output


def test_cli_maniskill_plan_doctor_smoke_and_view():
    cases = (
        ["install-plan", "maniskill"],
        ["doctor", "maniskill"],
        ["run", "maniskill", "--mode", "smoke", "--dry-run", "--no-save-report"],
        ["view", "maniskill", "--dry-run"],
    )
    for args in cases:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert "maniskill" in result.output.lower()


def test_cli_robocasa365_plan_doctor_smoke_and_view():
    cases = (
        ["install-plan", "robocasa365"],
        ["doctor", "robocasa365"],
        ["run", "robocasa365", "--mode", "smoke", "--dry-run", "--no-save-report"],
        ["view", "robocasa365", "--dry-run"],
    )
    for args in cases:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert "robocasa365" in result.output.lower()


def test_cli_molmospaces_plan_doctor_smoke_and_view():
    cases = (
        ["install-plan", "molmospaces"],
        ["doctor", "molmospaces"],
        ["run", "molmospaces", "--mode", "smoke", "--dry-run", "--no-save-report"],
        ["view", "molmospaces", "--dry-run"],
    )
    for args in cases:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, result.output
        assert "molmospaces" in result.output.lower()


def test_cli_planned_heavy_tool_dry_runs():
    for tool_id in ("behavior1k", "omnigibson"):
        result = runner.invoke(
            app,
            ["run", tool_id, "--mode", "smoke", "--dry-run", "--no-save-report"],
        )
        assert result.exit_code == 0, result.output
        assert "planned" in result.output


def test_cli_install_plan_preserves_extras_markup():
    result = runner.invoke(app, ["install-plan", "molmospaces", "--profile", "conda"])
    assert result.exit_code == 0, result.output
    assert 'pip install -e ".[mujoco]"' in result.output


def test_cli_real_status_strict_passes_when_all_viewers_verified():
    result = runner.invoke(app, ["real-status", "--strict"])
    assert result.exit_code == 0, result.output
    assert "Real-ready tools" in result.output


def test_cli_real_status_json_reports_all_tools_ready():
    result = runner.invoke(app, ["real-status", "--json"])
    assert result.exit_code == 0, result.output
    assert '"ready_tools": [' in result.output
    assert '"ai2thor"' in result.output
    assert '"behavior1k"' in result.output
    assert '"habitat"' in result.output
    assert '"maniskill"' in result.output
    assert '"molmospaces"' in result.output
    assert '"omnigibson"' in result.output
    assert '"robocasa365"' in result.output
    assert '"not_ready_count": 0' in result.output
