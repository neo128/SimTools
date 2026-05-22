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


def test_cli_install_plan_all_tools():
    result = runner.invoke(app, ["install-plan"])
    assert result.exit_code == 0, result.output
    assert "ai2thor" in result.output
    assert "Dry-run only" in result.output
