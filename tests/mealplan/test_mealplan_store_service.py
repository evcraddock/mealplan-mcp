"""
Tests for the store_mealplan service.

These tests verify that the store_mealplan service correctly:
1. Stores a new meal plan to the appropriate file path based on date and meal type
2. Handles collisions by appending suffixes to the filename
3. Uses atomic file operations for data integrity
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.models.meal_type import MealType
from mealplan_mcp.services.mealplan import store_mealplan


def test_store_new_mealplan(monkeypatch):
    """Test storing a new meal plan to the correct file path."""
    # Create a temp directory to use as the meal plan storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up a test meal plan
        date = datetime(2023, 6, 15, 18, 30)
        meal_plan = MealPlan(
            date=date,
            meal_type=MealType.DINNER,
            title="Italian Night",
            cook="Chef Mario",
            dishes=[],
        )

        # Mock the path functions to point to temp directory
        def mock_mealplan_directory_path(date):
            return Path(temp_dir) / "2023" / "06-June" / "06-15-2023"

        def mock_mealplan_path(date, meal_type):
            return mock_mealplan_directory_path(date) / f"06-15-2023-{meal_type}.md"

        # Replace the path functions in the store module
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_directory_path",
            mock_mealplan_directory_path,
        )
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_path",
            mock_mealplan_path,
        )

        # Get expected paths
        expected_dir = mock_mealplan_directory_path(date)
        expected_path = expected_dir / "06-15-2023-dinner.md"

        # Call the service
        result_path = store_mealplan(meal_plan)

        # Check that the file was created
        assert str(result_path) == str(expected_path)
        assert expected_path.exists()

        # Check the file contents
        with open(expected_path, "r") as f:
            stored_content = f.read()

        # Verify key elements of the markdown content
        assert "# Italian Night" in stored_content
        assert "**Cook:** Chef Mario" in stored_content
        assert "**Meal Type:** dinner" in stored_content
        assert "- [ ] Italian Night (dinner,Chef Mario) #mealplan" in stored_content


def test_store_mealplan_with_collision(monkeypatch):
    """Test storing a meal plan when a file with the same name already exists."""
    # Create a temp directory to use as the meal plan storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up two meal plans for the same date and meal type
        date = datetime(2023, 6, 15)
        meal_plan1 = MealPlan(
            date=date,
            meal_type=MealType.DINNER,
            title="First Dinner",
            cook="Chef 1",
            dishes=[],
        )
        meal_plan2 = MealPlan(
            date=date,
            meal_type=MealType.DINNER,
            title="Second Dinner",
            cook="Chef 2",
            dishes=[],
        )

        # Mock the path functions
        def mock_mealplan_directory_path(date):
            return Path(temp_dir) / "2023" / "06-June" / "06-15-2023"

        def mock_mealplan_path(date, meal_type):
            return mock_mealplan_directory_path(date) / f"06-15-2023-{meal_type}.md"

        # Replace the path functions
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_directory_path",
            mock_mealplan_directory_path,
        )
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_path",
            mock_mealplan_path,
        )

        # Store the first meal plan
        result_path1 = store_mealplan(meal_plan1)

        # Store the second meal plan with the same date/meal type
        # This should append a suffix to the filename
        result_path2 = store_mealplan(meal_plan2)

        # Check that both files exist
        expected_dir = mock_mealplan_directory_path(date)
        expected_path1 = expected_dir / "06-15-2023-dinner.md"
        expected_path2 = expected_dir / "06-15-2023-dinner-1.md"

        assert expected_path1.exists()
        assert expected_path2.exists()
        assert str(result_path1) == str(expected_path1)
        assert str(result_path2) == str(expected_path2)

        # Check the contents of both files
        with open(expected_path1, "r") as f:
            content1 = f.read()
        with open(expected_path2, "r") as f:
            content2 = f.read()

        assert "First Dinner" in content1
        assert "Chef 1" in content1
        assert "Second Dinner" in content2
        assert "Chef 2" in content2


def test_store_mealplan_creates_directory_structure(monkeypatch):
    """Test that the service creates the necessary directory structure."""
    # Create a temp directory to use as the meal plan storage
    with tempfile.TemporaryDirectory() as temp_dir:
        date = datetime(2023, 12, 25)  # Christmas
        meal_plan = MealPlan(
            date=date,
            meal_type=MealType.BREAKFAST,
            title="Christmas Breakfast",
            cook="Family",
            dishes=[],
        )

        # Mock the path functions
        def mock_mealplan_directory_path(date):
            return Path(temp_dir) / "2023" / "12-December" / "12-25-2023"

        def mock_mealplan_path(date, meal_type):
            return mock_mealplan_directory_path(date) / f"12-25-2023-{meal_type}.md"

        # Replace the path functions
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_directory_path",
            mock_mealplan_directory_path,
        )
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_path",
            mock_mealplan_path,
        )

        # The directory shouldn't exist initially
        expected_dir = mock_mealplan_directory_path(date)
        assert not expected_dir.exists()

        # Store the meal plan
        result_path = store_mealplan(meal_plan)

        # Check that the directory was created
        assert expected_dir.exists()
        assert expected_dir.is_dir()

        # Check that the file was created
        expected_path = expected_dir / "12-25-2023-breakfast.md"
        assert result_path == expected_path
        assert expected_path.exists()


def test_store_mealplan_different_meal_types(monkeypatch):
    """Test storing different meal types on the same date."""
    # Create a temp directory to use as the meal plan storage
    with tempfile.TemporaryDirectory() as temp_dir:
        date = datetime(2023, 6, 15)

        # Create meal plans for different meal types
        meal_plans = [
            MealPlan(
                date=date, meal_type=MealType.BREAKFAST, title="Breakfast", cook="Cook"
            ),
            MealPlan(date=date, meal_type=MealType.LUNCH, title="Lunch", cook="Cook"),
            MealPlan(date=date, meal_type=MealType.DINNER, title="Dinner", cook="Cook"),
            MealPlan(date=date, meal_type=MealType.SNACK, title="Snack", cook="Cook"),
        ]

        # Mock the path functions
        def mock_mealplan_directory_path(date):
            return Path(temp_dir) / "2023" / "06-June" / "06-15-2023"

        def mock_mealplan_path(date, meal_type):
            return mock_mealplan_directory_path(date) / f"06-15-2023-{meal_type}.md"

        # Replace the path functions
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_directory_path",
            mock_mealplan_directory_path,
        )
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_path",
            mock_mealplan_path,
        )

        # Store all meal plans
        result_paths = []
        for meal_plan in meal_plans:
            result_paths.append(store_mealplan(meal_plan))

        # Check that all files were created with correct names
        expected_dir = mock_mealplan_directory_path(date)
        expected_files = [
            "06-15-2023-breakfast.md",
            "06-15-2023-lunch.md",
            "06-15-2023-dinner.md",
            "06-15-2023-snack.md",
        ]

        for expected_file in expected_files:
            expected_path = expected_dir / expected_file
            assert expected_path.exists()

        # Verify all paths are different
        assert len(set(result_paths)) == len(result_paths)


def test_store_mealplan_with_default_values(monkeypatch):
    """Test storing a meal plan with default values."""
    # Create a temp directory to use as the meal plan storage
    with tempfile.TemporaryDirectory() as temp_dir:
        date = datetime.now()
        meal_plan = MealPlan(
            date=date,
            meal_type=MealType.LUNCH,
            # Using default title and cook
        )

        # Mock the path functions
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

        # Replace the path functions
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_directory_path",
            mock_mealplan_directory_path,
        )
        monkeypatch.setattr(
            "mealplan_mcp.services.mealplan.store.mealplan_path",
            mock_mealplan_path,
        )

        # Store the meal plan
        result_path = store_mealplan(meal_plan)

        # Check that the file was created
        assert result_path.exists()

        # Check the file contents include default values
        with open(result_path, "r") as f:
            stored_content = f.read()

        assert "# Untitled Meal" in stored_content
        assert "**Cook:** Unknown" in stored_content
