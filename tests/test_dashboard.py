from simtools.ui.streamlit_app import load_dashboard_data


def test_dashboard_data_loads_from_registry():
    data = load_dashboard_data()
    assert data["tool_count"] == 6
    assert "matrix" in data
    assert any(row["id"] == "ai2thor" for row in data["matrix"])
