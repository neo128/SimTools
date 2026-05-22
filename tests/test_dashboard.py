from simtools.ui.streamlit_app import artifact_preview, load_dashboard_data, summarize_artifacts


def test_dashboard_data_loads_from_registry():
    data = load_dashboard_data()
    assert data["tool_count"] == 7
    assert "matrix" in data
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


def test_artifact_preview_reads_json(tmp_path):
    path = tmp_path / "report.json"
    path.write_text('{"status": "skipped"}', encoding="utf-8")
    preview = artifact_preview(str(path))
    assert preview["kind"] == "json"
    assert preview["content"]["status"] == "skipped"
