"""
Tests for the grocery list generator service.

These tests verify that the generate_grocery_list service correctly:
1. Reads meal plan data
2. Renders markdown format
3. Writes files with correct paths
4. Returns the relative path
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def mock_dishes():
    """Create mock dish data for testing."""
    return [
        {
            "name": "Spaghetti Bolognese",
            "ingredients": [
                {"name": "ground beef", "amount": "500g"},
                {"name": "onion", "amount": "1 medium"},
                {"name": "garlic", "amount": "3 cloves"},
                {"name": "crushed tomatoes", "amount": "800g"},
            ],
        },
        {
            "name": "Chicken Curry",
            "ingredients": [
                {"name": "chicken breast", "amount": "500g"},
                {"name": "curry paste", "amount": "2 tbsp"},
                {"name": "coconut milk", "amount": "400ml"},
                {"name": "onion", "amount": "1 medium"},
            ],
        },
    ]


@pytest.fixture
def mock_meal_plans():
    """Create mock meal plan data for testing."""
    return [
        {
            "date": "2025-05-10",
            "meal_type": "dinner",
            "dish": "Spaghetti Bolognese",
        },
        {
            "date": "2025-05-11",
            "meal_type": "dinner",
            "dish": "Chicken Curry",
        },
    ]


def test_generate_grocery_list_with_string_dates(
    tmp_path, mock_dishes, mock_meal_plans
):
    """Test generate_grocery_list with string dates."""
    try:
        from mealplan_mcp.services.grocery import generate_grocery_list
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Set the MEALPLANPATH to our temp directory
    os.environ["MEALPLANPATH"] = str(tmp_path)

    # Create a directory for dishes and meal plans
    dishes_dir = tmp_path / "dishes"
    dishes_dir.mkdir()

    # Write mock dishes to files
    for dish in mock_dishes:
        dish_path = dishes_dir / f"{dish['name'].lower().replace(' ', '-')}.json"
        with open(dish_path, "w") as f:
            json.dump(dish, f)

    # Create year/month directories for meal plans
    year_dir = tmp_path / "2025"
    year_dir.mkdir()
    month_dir = year_dir / "05-May"
    month_dir.mkdir()

    # Create day directories for meal plans
    day_dir1 = month_dir / "05-10-2025"
    day_dir1.mkdir()
    day_dir2 = month_dir / "05-11-2025"
    day_dir2.mkdir()

    # Write mock meal plans to files
    meal_plan1_path = day_dir1 / "dinner.md"
    meal_plan2_path = day_dir2 / "dinner.md"

    # Create a simple meal plan file
    with open(meal_plan1_path, "w") as f:
        f.write(
            f"# {mock_meal_plans[0]['dish']}\n\n**Date:** {mock_meal_plans[0]['date']}\n"
        )

    with open(meal_plan2_path, "w") as f:
        f.write(
            f"# {mock_meal_plans[1]['dish']}\n\n**Date:** {mock_meal_plans[1]['date']}\n"
        )

    # Call the service
    start_date = "2025-05-10"
    end_date = "2025-05-11"

    with patch(
        "mealplan_mcp.services.grocery.generator.list_dishes"
    ) as mock_list_dishes:
        # Mock the list_dishes function to return our mock dishes
        # Mock the list_dishes function to return mock dishes for both dish names in meal plans
        mock_dishes_objects = []

        # Create a mock for Spaghetti Bolognese
        spaghetti = MagicMock()
        spaghetti.name = "Spaghetti Bolognese"
        spaghetti.ingredients = [
            {"name": "pasta", "amount": "200g"},
            {"name": "ground beef", "amount": "300g"},
            {"name": "tomato sauce", "amount": "400g"},
        ]
        mock_dishes_objects.append(spaghetti)

        # Create a mock for Chicken Curry
        curry = MagicMock()
        curry.name = "Chicken Curry"
        curry.ingredients = [
            {"name": "chicken", "amount": "500g"},
            {"name": "curry paste", "amount": "2 tbsp"},
            {"name": "onion", "amount": "1"},
        ]
        mock_dishes_objects.append(curry)

        mock_list_dishes.return_value = mock_dishes_objects

        # Call the service and save the result for assertion
        result = generate_grocery_list(start_date, end_date)

    # Check that the result is a string (relative path)
    assert isinstance(result, str)

    # Check that the grocery list file was created
    expected_file = tmp_path / "2025" / "05-May" / f"{start_date}_to_{end_date}.md"
    assert expected_file.exists()

    # Read the content and verify basic structure
    content = expected_file.read_text()

    # Should include a header with the date range
    assert (
        f"## {start_date} to {end_date}" in content
        or f"## {start_date}_to_{end_date}" in content
    )

    # Should include both dishes
    assert "Spaghetti Bolognese" in content
    assert "Chicken Curry" in content

    # Should include ingredients with checkbox format
    assert "- [ ] ground beef" in content
    assert "- [ ] pasta" in content
    assert "- [ ] tomato sauce" in content
    assert "- [ ] chicken" in content

    # Shared ingredients should be consolidated (like onion)
    onion_count = content.count("- [ ] onion")
    assert onion_count == 1, f"Expected onion to appear once, found {onion_count} times"


def test_generate_grocery_list_with_ignored_ingredients(
    tmp_path, mock_dishes, mock_meal_plans
):
    """Test generate_grocery_list with ignored ingredients."""
    try:
        from mealplan_mcp.services.grocery import generate_grocery_list
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Set the MEALPLANPATH to our temp directory
    os.environ["MEALPLANPATH"] = str(tmp_path)

    # Create a directory for dishes and meal plans
    dishes_dir = tmp_path / "dishes"
    dishes_dir.mkdir()

    # Write mock dishes to files
    for dish in mock_dishes:
        dish_path = dishes_dir / f"{dish['name'].lower().replace(' ', '-')}.json"
        with open(dish_path, "w") as f:
            json.dump(dish, f)

    # Create year/month directories for meal plans
    year_dir = tmp_path / "2025"
    year_dir.mkdir()
    month_dir = year_dir / "05-May"
    month_dir.mkdir()

    # Create day directories for meal plans
    day_dir1 = month_dir / "05-10-2025"
    day_dir1.mkdir()
    day_dir2 = month_dir / "05-11-2025"
    day_dir2.mkdir()

    # Write mock meal plans to files
    meal_plan1_path = day_dir1 / "dinner.md"
    meal_plan2_path = day_dir2 / "dinner.md"

    # Create a simple meal plan file
    with open(meal_plan1_path, "w") as f:
        f.write(
            f"# {mock_meal_plans[0]['dish']}\n\n**Date:** {mock_meal_plans[0]['date']}\n"
        )

    with open(meal_plan2_path, "w") as f:
        f.write(
            f"# {mock_meal_plans[1]['dish']}\n\n**Date:** {mock_meal_plans[1]['date']}\n"
        )

    # Set up mocks
    with (
        patch(
            "mealplan_mcp.services.grocery.generator.list_dishes"
        ) as mock_list_dishes,
        patch(
            "mealplan_mcp.services.grocery.generator.get_ignored_ingredients"
        ) as mock_get_ignored,
    ):

        # Mock the list_dishes function to return mock dishes for both dish names in meal plans
        mock_dishes_objects = []

        # Create a mock for Spaghetti Bolognese
        spaghetti = MagicMock()
        spaghetti.name = "Spaghetti Bolognese"
        spaghetti.ingredients = [
            {"name": "pasta", "amount": "200g"},
            {"name": "ground beef", "amount": "300g"},
            {"name": "tomato sauce", "amount": "400g"},
        ]
        mock_dishes_objects.append(spaghetti)

        # Create a mock for Chicken Curry
        curry = MagicMock()
        curry.name = "Chicken Curry"
        curry.ingredients = [
            {"name": "chicken", "amount": "500g"},
            {"name": "curry paste", "amount": "2 tbsp"},
            {"name": "onion", "amount": "1"},
        ]
        mock_dishes_objects.append(curry)

        mock_list_dishes.return_value = mock_dishes_objects

        # Mock ignored ingredients to include "onion"
        mock_get_ignored.return_value = ["onion"]

        # Call the service
        start_date = "2025-05-10"
        end_date = "2025-05-11"
        # Calling the function but ignoring the return value
        # We're just testing side effects
        _ = generate_grocery_list(start_date, end_date)

    # Check that the grocery list file was created
    expected_file = tmp_path / "2025" / "05-May" / f"{start_date}_to_{end_date}.md"
    assert expected_file.exists()

    # Read the content
    content = expected_file.read_text()

    # "onion" should be excluded or marked as ignored
    assert "onion" not in content or "~~onion~~" in content or "IGNORED" in content

    # Other ingredients should still be included
    assert "ground beef" in content
    assert "pasta" in content
    assert "chicken" in content
    assert "curry paste" in content


def test_generate_grocery_list_empty_period(tmp_path):
    """Test generate_grocery_list with no meal plans in the period."""
    try:
        from mealplan_mcp.services.grocery import generate_grocery_list
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Set the MEALPLANPATH to our temp directory
    os.environ["MEALPLANPATH"] = str(tmp_path)

    # Create empty directory structure
    year_dir = tmp_path / "2025"
    year_dir.mkdir()
    month_dir = year_dir / "05-May"
    month_dir.mkdir()

    # Call the service with dates where no meal plans exist
    start_date = "2025-05-20"
    end_date = "2025-05-21"

    with patch(
        "mealplan_mcp.services.grocery.generator.list_dishes"
    ) as mock_list_dishes:
        # Return empty list to simulate no dishes
        mock_list_dishes.return_value = []

        # Print mealplan_root for debugging
        from mealplan_mcp.utils.paths import mealplan_root

        print(f"MEALPLANPATH set to: {os.environ.get('MEALPLANPATH')}")
        print(f"mealplan_root is: {mealplan_root}")

        # Calling the function but ignoring the return value
        # We're just testing side effects
        _ = generate_grocery_list(start_date, end_date)

    # Check that the grocery list file was created even for empty period
    expected_file = tmp_path / "2025" / "05-May" / f"{start_date}_to_{end_date}.md"
    assert expected_file.exists()

    # Read the content
    content = expected_file.read_text()

    # Should include a message about no ingredients or meal plans
    assert (
        "No meal plans" in content
        or "No ingredients" in content
        or "Empty grocery list" in content
    )
