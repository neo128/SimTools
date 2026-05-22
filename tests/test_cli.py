from typer.testing import CliRunner

from simtools.cli.main import app


runner = CliRunner()


def test_cli_status_profiles_validate_and_artifacts():
    for args in (
        ["status"],
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
