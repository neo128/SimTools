from simtools.ui.streamlit_app import (
    artifact_preview,
    load_dashboard_data,
    run_metric_summary,
    summarize_artifacts,
)


def test_dashboard_data_loads_from_registry():
    data = load_dashboard_data()
    assert data["tool_count"] == 7
    assert "matrix" in data
    assert data["readiness"]["ready_tools"] == [
        "ai2thor",
        "behavior1k",
        "habitat",
        "maniskill",
        "molmospaces",
        "omnigibson",
        "robocasa365",
    ]
    assert any(row["id"] == "ai2thor" for row in data["matrix"])


def test_artifact_summary_counts_by_tool():
    summary = summarize_artifacts(
        [
            {"tool_id": "ai2thor"},
            {"tool_id": "ai2thor"},
            {"tool_id": "habitat"},
        ]
    )
    assert summary == {"ai2thor": 2, "habitat": 1}


def test_run_metric_summary_extracts_benchmark_fields():
    summary = run_metric_summary(
        {
            "report_path": "/tmp/report.json",
            "artifacts": ["frame.ppm", "metadata.json"],
            "metrics": {
                "schema_version": "simtools.metrics.v1",
                "artifact_count": 2,
            },
            "benchmark_result": {"status": "not_scored"},
        }
    )

    assert summary == {
        "metrics_schema": "simtools.metrics.v1",
        "artifact_count": 2,
        "benchmark_status": "not_scored",
        "report_path": "/tmp/report.json",
    }


def test_artifact_preview_reads_json(tmp_path):
    path = tmp_path / "report.json"
    path.write_text('{"status": "skipped"}', encoding="utf-8")
    preview = artifact_preview(str(path))
    assert preview["kind"] == "json"
    assert preview["content"]["status"] == "skipped"
