"""
Tests for path utilities.
"""

import calendar
from datetime import datetime
from pathlib import Path

from mealplan_mcp.utils.paths import dish_path, grocery_path


def test_mealplan_root_from_env(monkeypatch):
    """Test that mealplan_root uses the MEALPLANPATH environment variable."""

    test_path = "/test/mealplan/path"
    monkeypatch.setenv("MEALPLANPATH", test_path)

    # We need to reload the module to re-evaluate mealplan_root with the new env var
    import importlib
    import mealplan_mcp.utils.paths

    importlib.reload(mealplan_mcp.utils.paths)

    assert mealplan_mcp.utils.paths.mealplan_root == Path(test_path)

    # Clean up after ourselves - restore the original module state
    monkeypatch.undo()
    importlib.reload(mealplan_mcp.utils.paths)


def test_dish_path():
    """Test that dish_path generates correct paths for dish JSON files."""

    slug = "chili-con-carne"

    result = dish_path(slug)
    assert result.name == f"{slug}.json"
    assert "dishes" in str(result)


def test_grocery_path():
    """Test that grocery_path correctly formats paths for grocery lists."""
    start_date = "2025-05-10"
    end_date = "2025-05-17"

    # Parse the date to get components for verification
    start = datetime.strptime(start_date, "%Y-%m-%d")
    year = start.strftime("%Y")
    month_num = start.strftime("%m")
    month_name = calendar.month_name[start.month]

    result = grocery_path(start_date, end_date)

    # Verify the structure of the path
    assert result.name == f"{start_date}_to_{end_date}.md"
    assert str(result.parent).endswith(f"{year}/{month_num}-{month_name}")

    # Test for the specific example mentioned in Prompt 24
    assert (
        grocery_path("2025-05-10", "2025-05-17").name == "2025-05-10_to_2025-05-17.md"
    )
    assert str(grocery_path("2025-05-10", "2025-05-17")).endswith(
        "2025/05-May/2025-05-10_to_2025-05-17.md"
    )
