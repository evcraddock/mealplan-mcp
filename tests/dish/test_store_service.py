"""
Tests for the store_dish service.

These tests verify that the store_dish service correctly:
1. Stores a new dish to the appropriate file path based on its slug
2. Handles collisions by appending suffixes to the slug
"""

import json
import tempfile
from pathlib import Path
import pytest
import sys
import os

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from mealplan_mcp.utils.paths import dish_path


# Mock implementations
class MockDish:
    """Mock implementation of the Dish model."""

    def __init__(self, name, slug=None):
        self.name = name
        self._slug = slug or name.lower().replace(" ", "-")

    @property
    def slug(self):
        return self._slug

    @property
    def model_dump_json(self):
        """Mock the model_dump_json method."""
        return json.dumps({"name": self.name})


def test_store_new_dish():
    """Test storing a new dish to the correct file path."""
    try:
        from mealplan_mcp.services.dish import store_dish
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Create a temp directory to use as the dish storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up a mock dish
        dish_name = "Spaghetti Carbonara"
        dish = MockDish(dish_name)

        # Patch the dish_path function to use the temp directory
        original_dish_path = dish_path

        def mock_dish_path(slug):
            return Path(temp_dir) / f"{slug}.json"

        # Use the patched function
        try:
            # Monkeypatch the dish_path function
            import mealplan_mcp.services.dish

            mealplan_mcp.services.dish.dish_path = mock_dish_path

            # Call the service
            result_path = store_dish(dish)

            # Check that the file was created
            expected_path = mock_dish_path(dish.slug)
            assert result_path == expected_path
            assert expected_path.exists()

            # Check the file contents
            with open(expected_path, "r") as f:
                stored_data = json.load(f)

            assert stored_data["name"] == dish_name

        finally:
            # Restore the original dish_path function
            mealplan_mcp.services.dish.dish_path = original_dish_path


def test_store_dish_with_collision():
    """Test storing a dish with a slug that already exists."""
    try:
        from mealplan_mcp.services.dish import store_dish
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Create a temp directory to use as the dish storage
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up mock dishes with the same slug
        dish1 = MockDish("Spaghetti Carbonara")
        dish2 = MockDish("Spaghetti Carbonara (Variation)")

        # Force the same slug for both dishes
        dish2._slug = dish1.slug

        # Patch the dish_path function to use the temp directory
        original_dish_path = dish_path

        def mock_dish_path(slug):
            return Path(temp_dir) / f"{slug}.json"

        # Use the patched function
        try:
            # Monkeypatch the dish_path function
            import mealplan_mcp.services.dish

            mealplan_mcp.services.dish.dish_path = mock_dish_path

            # Store the first dish
            store_dish(dish1)

            # Store the second dish with the same slug
            # This should append a suffix to the slug
            result_path = store_dish(dish2)

            # Check that both files exist
            expected_path1 = mock_dish_path(dish1.slug)
            expected_path2 = mock_dish_path(f"{dish2.slug}-1")

            assert expected_path1.exists()
            assert expected_path2.exists()

            # The result should be the new path
            assert result_path == expected_path2

            # Check the contents of the second file
            with open(expected_path2, "r") as f:
                stored_data = json.load(f)

            assert stored_data["name"] == dish2.name

        finally:
            # Restore the original dish_path function
            mealplan_mcp.services.dish.dish_path = original_dish_path
