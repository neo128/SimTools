from simtools.core.artifact_store import ArtifactStore


def test_artifact_store_writes_and_lists_json_reports(tmp_path):
    store = ArtifactStore(root=tmp_path / "artifacts")
    report = store.write_json_report(
        "fake_tool",
        "smoke_report",
        {"tool_id": "fake_tool", "status": "skipped"},
    )

    assert report.exists()
    artifacts = store.list_artifacts()
    assert len(artifacts) == 1
    assert artifacts[0]["tool_id"] == "fake_tool"
    assert artifacts[0]["relative_path"].startswith("fake_tool/")


def test_artifact_report_prefix_is_sanitized(tmp_path):
    store = ArtifactStore(root=tmp_path / "artifacts")
    report = store.write_json_report(
        "fake_tool",
        "../bad prefix",
        {"status": "failed"},
    )

    assert report.parent == tmp_path / "artifacts" / "fake_tool"
    assert ".." not in report.name
    assert "/" not in report.name
