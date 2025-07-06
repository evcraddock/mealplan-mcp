"""
Tests for the meal plan list service.

These tests verify that the list service correctly:
1. Lists meal plans within a date range
2. Extracts dish names from meal plan files
3. Handles missing files gracefully
4. Sorts results chronologically
5. Returns proper JSON structure
"""

import sys
import os
import tempfile
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.models.meal_type import MealType
from mealplan_mcp.models.dish import Dish
from mealplan_mcp.services.mealplan.store import store_mealplan
from mealplan_mcp.services.mealplan.list_service import list_mealplans_by_date_range


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


class TestListMealplansService:
    """Test cases for the list_mealplans_by_date_range service."""

    def test_empty_date_range_returns_empty_list(self, monkeypatch):
        """Test that an empty date range returns an empty list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = list_mealplans_by_date_range("2023-06-01", "2023-06-07")
            assert result == []

    def test_single_meal_plan_in_range(self, monkeypatch):
        """Test that a single meal plan in range is returned correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create a test meal plan
            dish1 = Dish(name="Spaghetti Carbonara")
            dish2 = Dish(name="Caesar Salad")

            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.DINNER,
                title="Italian Night",
                cook="Chef Mario",
                dishes=[dish1, dish2],
            )

            # Store the meal plan
            store_mealplan(meal_plan)

            # Query for the meal plan
            result = list_mealplans_by_date_range("2023-06-10", "2023-06-20")

            assert len(result) == 1
            meal = result[0]
            assert meal["title"] == "Italian Night"
            assert meal["date"] == "2023-06-15"
            assert meal["meal_type"] == "dinner"
            assert meal["cook"] == "Chef Mario"
            assert meal["dishes"] == ["Spaghetti Carbonara", "Caesar Salad"]

    def test_multiple_meal_plans_sorted_chronologically(self, monkeypatch):
        """Test that multiple meal plans are sorted chronologically."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create multiple meal plans on different dates
            meal_plans = [
                MealPlan(
                    date=datetime(2023, 6, 17),
                    meal_type=MealType.LUNCH,
                    title="Late Lunch",
                    cook="Bob",
                    dishes=[Dish(name="Sandwich")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 15),
                    meal_type=MealType.BREAKFAST,
                    title="Early Breakfast",
                    cook="Alice",
                    dishes=[Dish(name="Oatmeal")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 16),
                    meal_type=MealType.DINNER,
                    title="Middle Dinner",
                    cook="Charlie",
                    dishes=[Dish(name="Steak")],
                ),
            ]

            # Store all meal plans
            for meal_plan in meal_plans:
                store_mealplan(meal_plan)

            # Query for all meal plans
            result = list_mealplans_by_date_range("2023-06-14", "2023-06-18")

            assert len(result) == 3

            # Verify chronological order
            assert result[0]["date"] == "2023-06-15"
            assert result[0]["title"] == "Early Breakfast"
            assert result[1]["date"] == "2023-06-16"
            assert result[1]["title"] == "Middle Dinner"
            assert result[2]["date"] == "2023-06-17"
            assert result[2]["title"] == "Late Lunch"

    def test_date_range_filtering_inclusive(self, monkeypatch):
        """Test that date range filtering is inclusive of start and end dates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create meal plans on boundary dates and outside
            meal_plans = [
                MealPlan(
                    date=datetime(2023, 6, 14),  # Before range
                    meal_type=MealType.DINNER,
                    title="Before Range",
                    cook="Alice",
                    dishes=[Dish(name="Dish1")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 15),  # Start of range
                    meal_type=MealType.BREAKFAST,
                    title="Start Date",
                    cook="Bob",
                    dishes=[Dish(name="Dish2")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 17),  # End of range
                    meal_type=MealType.LUNCH,
                    title="End Date",
                    cook="Charlie",
                    dishes=[Dish(name="Dish3")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 18),  # After range
                    meal_type=MealType.DINNER,
                    title="After Range",
                    cook="David",
                    dishes=[Dish(name="Dish4")],
                ),
            ]

            # Store all meal plans
            for meal_plan in meal_plans:
                store_mealplan(meal_plan)

            # Query for specific range
            result = list_mealplans_by_date_range("2023-06-15", "2023-06-17")

            assert len(result) == 2
            assert result[0]["title"] == "Start Date"
            assert result[1]["title"] == "End Date"

    def test_meal_plan_with_no_dishes(self, monkeypatch):
        """Test that meal plans with no dishes return empty dish array."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.SNACK,
                title="Empty Meal",
                cook="Someone",
                dishes=[],
            )

            store_mealplan(meal_plan)

            result = list_mealplans_by_date_range("2023-06-15", "2023-06-15")

            assert len(result) == 1
            assert result[0]["dishes"] == []

    def test_multiple_meal_types_same_date(self, monkeypatch):
        """Test that multiple meal types on the same date are all returned."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            date = datetime(2023, 6, 15)

            meal_plans = [
                MealPlan(
                    date=date,
                    meal_type=MealType.BREAKFAST,
                    title="Morning Meal",
                    cook="Alice",
                    dishes=[Dish(name="Eggs")],
                ),
                MealPlan(
                    date=date,
                    meal_type=MealType.LUNCH,
                    title="Afternoon Meal",
                    cook="Bob",
                    dishes=[Dish(name="Salad")],
                ),
                MealPlan(
                    date=date,
                    meal_type=MealType.DINNER,
                    title="Evening Meal",
                    cook="Charlie",
                    dishes=[Dish(name="Pasta")],
                ),
            ]

            for meal_plan in meal_plans:
                store_mealplan(meal_plan)

            result = list_mealplans_by_date_range("2023-06-15", "2023-06-15")

            assert len(result) == 3

            # Should be sorted by meal type (alphabetically: breakfast, dinner, lunch)
            meal_types = [meal["meal_type"] for meal in result]
            assert "breakfast" in meal_types
            assert "lunch" in meal_types
            assert "dinner" in meal_types

    def test_invalid_date_range_returns_empty_list(self, monkeypatch):
        """Test that invalid date ranges return empty lists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # End date before start date
            result = list_mealplans_by_date_range("2023-06-20", "2023-06-15")
            assert result == []

    def test_cleaned_title_used_in_response(self, monkeypatch):
        """Test that cleaned titles are used in the response."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.DINNER,
                title="  Messy   Title   ",  # Title with extra whitespace
                cook="Chef",
                dishes=[Dish(name="Dish")],
            )

            store_mealplan(meal_plan)

            result = list_mealplans_by_date_range("2023-06-15", "2023-06-15")

            assert len(result) == 1
            assert result[0]["title"] == "Messy   Title"  # Should be cleaned

    def test_single_date_range(self, monkeypatch):
        """Test querying for a single date (start == end)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.LUNCH,
                title="Single Day",
                cook="Chef",
                dishes=[Dish(name="Lunch Dish")],
            )

            store_mealplan(meal_plan)

            result = list_mealplans_by_date_range("2023-06-15", "2023-06-15")

            assert len(result) == 1
            assert result[0]["date"] == "2023-06-15"

    def test_parsing_dish_names_from_markdown(self, monkeypatch):
        """Test that dish names are correctly extracted from existing markdown files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # This test will be important for existing meal plans that are already stored
            # We'll create a meal plan, then verify the service can read it back correctly

            dish1 = Dish(name="Complex Dish Name with Special Characters!")
            dish2 = Dish(name="Simple Dish")

            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.DINNER,
                title="Dish Name Test",
                cook="Chef",
                dishes=[dish1, dish2],
            )

            store_mealplan(meal_plan)

            result = list_mealplans_by_date_range("2023-06-15", "2023-06-15")

            assert len(result) == 1
            dish_names = result[0]["dishes"]
            assert "Complex Dish Name with Special Characters!" in dish_names
            assert "Simple Dish" in dish_names
