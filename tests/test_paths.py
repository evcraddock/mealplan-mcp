"""
Tests for path utilities.
"""

import calendar
from datetime import datetime
from pathlib import Path

from mealplan_mcp.utils.paths import (
    dish_path,
    grocery_path,
    mealplan_path,
    mealplan_directory_path,
)


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


def test_mealplan_path():
    """Test that mealplan_path generates correct paths for meal plan markdown files."""
    date = datetime(2023, 6, 15, 18, 30)
    meal_type = "dinner"

    result = mealplan_path(date, meal_type)

    # Should be: YYYY/MM-MonthName/MM-DD-YYYY/meal_type.md
    assert result.name == f"{meal_type}.md"
    assert "2023" in str(result)
    assert "06-June" in str(result)
    assert "06-15-2023" in str(result)


def test_mealplan_path_different_meal_types():
    """Test mealplan_path with different meal types."""
    date = datetime(2023, 6, 15)

    for meal_type in ["breakfast", "lunch", "dinner", "snack"]:
        result = mealplan_path(date, meal_type)
        assert result.name == f"{meal_type}.md"
        assert "06-15-2023" in str(result)


def test_mealplan_directory_path():
    """Test that mealplan_directory_path generates correct directory paths."""
    date = datetime(2023, 6, 15)

    result = mealplan_directory_path(date)

    # Should end with: 2023/06-June/06-15-2023
    assert str(result).endswith("2023/06-June/06-15-2023")


def test_mealplan_path_single_digit_day():
    """Test mealplan_path with single digit day."""
    date = datetime(2023, 6, 5)  # 5th day of month
    meal_type = "breakfast"

    result = mealplan_path(date, meal_type)

    # Should format as 06-05-2023
    assert "06-05-2023" in str(result)
    assert result.name == "breakfast.md"


def test_mealplan_path_different_months():
    """Test mealplan_path with different months."""
    # Test December (month 12)
    date_dec = datetime(2023, 12, 25)
    result_dec = mealplan_path(date_dec, "dinner")
    assert "12-December" in str(result_dec)
    assert "12-25-2023" in str(result_dec)

    # Test January (month 1)
    date_jan = datetime(2023, 1, 1)
    result_jan = mealplan_path(date_jan, "breakfast")
    assert "01-January" in str(result_jan)
    assert "01-01-2023" in str(result_jan)


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
