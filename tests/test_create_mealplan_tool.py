"""
Tests for the simplified create_mealplan tool function.
"""

import sys
import os
import tempfile
from pathlib import Path
import pytest
from datetime import datetime

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.models.meal_type import MealType


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_create_mealplan_tool_basic(monkeypatch):
    """Test the create_mealplan tool function with basic input."""
    # Import the tool function
    from main import create_mealplan

    # Create a temp directory to use as the meal plan storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the path functions
        def mock_mealplan_directory_path(date):
            return Path(temp_dir) / "2023" / "06-June" / "06-15-2023"

        def mock_mealplan_path(date, meal_type):
            return mock_mealplan_directory_path(date) / f"06-15-2023-{meal_type}.md"

        # Replace the path function in the store module
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_path",
            mock_mealplan_path,
        )

        # Create a test meal plan
        date = datetime(2023, 6, 15, 18, 30)
        meal_plan = MealPlan(
            date=date,
            meal_type=MealType.DINNER,
            title="Italian Night",
            cook="Chef Mario",
            dishes=[],
        )

        # Call the tool function
        result = await create_mealplan(meal_plan)

        # Check that result is a string
        assert isinstance(result, str)

        # Check that the result contains expected elements
        assert "Italian Night" in result
        assert "dinner" in result
        assert "Chef Mario" in result
        assert "2023-06-15" in result
        assert "Meal plan saved to:" in result

        # Check that both files were actually created
        expected_dir = mock_mealplan_directory_path(date)
        expected_md_file = expected_dir / "06-15-2023-dinner.md"
        expected_json_file = expected_dir / "06-15-2023-dinner.json"
        assert expected_md_file.exists()
        assert expected_json_file.exists()


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_create_mealplan_tool_with_defaults(monkeypatch):
    """Test the create_mealplan tool with default values."""
    from main import create_mealplan

    # Create a temp directory to use as the meal plan storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the mealplan_directory_path function
        def mock_mealplan_directory_path(date):
            year = date.strftime("%Y")
            month_num = date.strftime("%m")
            month_name = [
                "",
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ][date.month]
            day = date.strftime("%d")
            return (
                Path(temp_dir)
                / year
                / f"{month_num}-{month_name}"
                / f"{month_num}-{day}-{year}"
            )

        def mock_mealplan_path(date, meal_type):
            date_str = (
                f"{date.strftime('%m')}-{date.strftime('%d')}-{date.strftime('%Y')}"
            )
            return mock_mealplan_directory_path(date) / f"{date_str}-{meal_type}.md"

        # Replace the path function
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_path",
            mock_mealplan_path,
        )

        # Create a meal plan with minimal data (using defaults)
        date = datetime.now()
        meal_plan = MealPlan(
            date=date,
            meal_type=MealType.LUNCH,
            # title and cook will use defaults
        )

        # Call the tool function
        result = await create_mealplan(meal_plan)

        # Check that result contains default values
        assert "Untitled Meal" in result
        assert "Unknown" in result
        assert "lunch" in result
        assert "Meal plan saved to:" in result


@pytest.mark.anyio
@pytest.mark.parametrize("anyio_backend", ["asyncio"])
async def test_create_mealplan_tool_return_format(monkeypatch):
    """Test that the create_mealplan tool returns the expected format."""
    from main import create_mealplan

    # Create a temp directory to use as the meal plan storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Mock the mealplan_directory_path function
        def mock_mealplan_directory_path(date):
            return Path(temp_dir) / "2023" / "06-June" / "06-15-2023"

        def mock_mealplan_path(date, meal_type):
            date_str = (
                f"{date.strftime('%m')}-{date.strftime('%d')}-{date.strftime('%Y')}"
            )
            return mock_mealplan_directory_path(date) / f"{date_str}-{meal_type}.md"

        # Replace the path function
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_path",
            mock_mealplan_path,
        )

        # Create a test meal plan
        date = datetime(2023, 6, 15)
        meal_plan = MealPlan(
            date=date,
            meal_type=MealType.BREAKFAST,
            title="Morning Feast",
            cook="Home Cook",
            dishes=[],
        )

        # Call the tool function
        result = await create_mealplan(meal_plan)

        # Check the structure of the result
        lines = result.split("\n")

        # Should start with markdown task
        assert lines[0].startswith(
            "Markdown Task: - [ ] Morning Feast (breakfast,Home Cook)"
        )

        # Should contain meal plan summary
        assert any(
            "Meal Plan: Morning Feast (breakfast) on 2023-06-15" in line
            for line in lines
        )

        # Should contain dishes section
        assert any("Dishes (0):" in line for line in lines)

        # Should end with file path
        assert any("Meal plan saved to:" in line for line in lines)
