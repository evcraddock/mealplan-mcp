"""
Tests for the list_mealplans_by_date_range MCP tool.

These tests verify that the FastMCP tool correctly:
1. Accepts proper JSON input format
2. Validates date range parameters
3. Returns properly formatted JSON response
4. Handles various error conditions
"""

import sys
import os
import tempfile
import pytest
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.models.meal_type import MealType
from mealplan_mcp.models.dish import Dish
from mealplan_mcp.services.mealplan.store import store_mealplan


def _setup_test_environment(monkeypatch, temp_dir):
    """Set up the test environment with temporary directory."""
    # Mock the mealplan_root in both services
    monkeypatch.setattr(
        "mealplan_mcp.services.mealplan.list_service.mealplan_root", Path(temp_dir)
    )

    # Mock the path functions for store service
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
        date_str = f"{date.strftime('%m')}-{date.strftime('%d')}-{date.strftime('%Y')}"
        return mock_mealplan_directory_path(date) / f"{date_str}-{meal_type}.md"

    monkeypatch.setattr(
        "mealplan_mcp.services.mealplan.store.mealplan_path",
        mock_mealplan_path,
    )


class TestListMealplansTool:
    """Test cases for the list_mealplans_by_date_range MCP tool."""

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_valid_date_range(self, monkeypatch):
        """Test the tool with a valid date range input."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create and store a test meal plan
            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.DINNER,
                title="Test Meal",
                cook="Test Cook",
                dishes=[Dish(name="Test Dish")],
            )
            store_mealplan(meal_plan)

            # Call the tool
            result = await list_mealplans_by_date_range(
                {"start": "2023-06-10", "end": "2023-06-20"}
            )

            # Parse the result as JSON
            content = json.loads(result)
            assert len(content) == 1

            meal = content[0]
            assert meal["title"] == "Test Meal"
            assert meal["date"] == "2023-06-15"
            assert meal["meal_type"] == "dinner"
            assert meal["cook"] == "Test Cook"
            assert meal["dishes"] == ["Test Dish"]

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_empty_result(self, monkeypatch):
        """Test the tool when no meal plans are found in the date range."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await list_mealplans_by_date_range(
                {"start": "2023-01-01", "end": "2023-01-07"}
            )

            # Parse the content as JSON
            content = json.loads(result)
            assert content == []

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_multiple_meal_plans(self, monkeypatch):
        """Test the tool with multiple meal plans in the date range."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create multiple meal plans
            meal_plans = [
                MealPlan(
                    date=datetime(2023, 6, 15),
                    meal_type=MealType.BREAKFAST,
                    title="Breakfast",
                    cook="Alice",
                    dishes=[Dish(name="Eggs"), Dish(name="Toast")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 16),
                    meal_type=MealType.LUNCH,
                    title="Lunch",
                    cook="Bob",
                    dishes=[Dish(name="Sandwich")],
                ),
            ]

            for meal_plan in meal_plans:
                store_mealplan(meal_plan)

            # Call the tool
            result = await list_mealplans_by_date_range(
                {"start": "2023-06-15", "end": "2023-06-16"}
            )

            # Parse the content as JSON
            content = json.loads(result)
            assert len(content) == 2

            # Verify chronological order
            assert content[0]["date"] == "2023-06-15"
            assert content[0]["title"] == "Breakfast"
            assert content[1]["date"] == "2023-06-16"
            assert content[1]["title"] == "Lunch"

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_missing_date_range(self, monkeypatch):
        """Test the tool with missing date_range parameter."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await list_mealplans_by_date_range({})

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "date_range" in error_response["message"]

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_missing_start_date(self, monkeypatch):
        """Test the tool with missing start date."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await list_mealplans_by_date_range({"end": "2023-06-20"})

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "start" in error_response["message"]

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_missing_end_date(self, monkeypatch):
        """Test the tool with missing end date."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await list_mealplans_by_date_range({"start": "2023-06-10"})

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "end" in error_response["message"]

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_invalid_date_format(self, monkeypatch):
        """Test the tool with invalid date format."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await list_mealplans_by_date_range(
                {"start": "invalid-date", "end": "2023-06-20"}
            )

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "date format" in error_response["message"].lower()

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_end_before_start(self, monkeypatch):
        """Test the tool when end date is before start date."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await list_mealplans_by_date_range(
                {"start": "2023-06-20", "end": "2023-06-10"}
            )

            # Should succeed but return empty array
            content = json.loads(result)
            assert content == []

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_same_start_and_end_date(self, monkeypatch):
        """Test the tool with the same start and end date."""
        from main import list_mealplans_by_date_range

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create a meal plan on the target date
            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.LUNCH,
                title="Single Day Meal",
                cook="Chef",
                dishes=[Dish(name="Soup")],
            )
            store_mealplan(meal_plan)

            result = await list_mealplans_by_date_range(
                {"start": "2023-06-15", "end": "2023-06-15"}
            )

            # Parse the content as JSON
            content = json.loads(result)
            assert len(content) == 1
            assert content[0]["title"] == "Single Day Meal"
