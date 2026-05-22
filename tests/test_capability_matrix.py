from simtools.core.capability_matrix import matrix_markdown, matrix_rows
from simtools.core.registry import ToolRegistry


def test_matrix_rows_include_initial_tools():
    registry = ToolRegistry.from_configs()
    rows = matrix_rows(registry)
    ids = {row["id"] for row in rows}
    assert "ai2thor" in ids
    assert "maniskill" in ids
    assert "robocasa365" in ids


def test_matrix_markdown_has_header_and_ai2thor():
    registry = ToolRegistry.from_configs()
    markdown = matrix_markdown(registry)
    assert "| ID | Tool | Backend |" in markdown
    assert "| ai2thor | AI2-THOR | Unity |" in markdown
