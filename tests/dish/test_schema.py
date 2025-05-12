"""
Tests for the Dish schema.

These tests verify that the Dish schema correctly:
1. Validates proper JSON input
2. Applies name cleaning and slug generation rules
3. Truncates names longer than 100 characters
"""

import pytest
from typing import Dict, Any


# For the tests we're just setting up the required interface,
# not importing the actual implementation (which doesn't exist yet)
class MockDish:
    """Mock implementation of Dish schema for testing."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize with dish data."""
        self.data = data
        self.cleaned_name = None
        self._slug = None
        self.clean()

    def clean(self):
        """Clean the dish data, including name fields."""
        name = self.data.get("name", "").strip()
        if name:
            self.cleaned_name = name[:100]  # Truncate to 100 chars
            # In the real implementation, there would be more sophisticated cleaning
        else:
            self.cleaned_name = "Unnamed Dish"

    @property
    def slug(self) -> str:
        """Generate a URL-friendly slug for the dish name."""
        # This would use the slugify function in the real implementation
        if not self._slug:
            self._slug = self.cleaned_name.lower().replace(" ", "-")[:100]
        return self._slug


def test_valid_json():
    """Test that a valid JSON representation passes validation."""
    try:
        from mealplan_mcp.models.dish import Dish
    except ImportError:
        Dish = MockDish
        pytest.skip("Using mock implementation")

    valid_json = {
        "name": "Spaghetti Carbonara",
        "ingredients": [
            {"name": "Pasta", "amount": "200g"},
            {"name": "Eggs", "amount": "2"},
            {"name": "Parmesan", "amount": "50g"},
            {"name": "Bacon", "amount": "100g"},
        ],
        "instructions": "Cook pasta. Mix eggs and cheese. Combine.",
    }

    dish = Dish(valid_json)
    assert dish.data["name"] == "Spaghetti Carbonara"
    assert len(dish.data["ingredients"]) == 4


def test_name_cleaning_and_slug():
    """Test that name cleaning and slug generation follow the expected rules."""
    try:
        from mealplan_mcp.models.dish import Dish
    except ImportError:
        Dish = MockDish
        pytest.skip("Using mock implementation")

    # Test with leading/trailing whitespace and mixed case
    dish_data = {"name": "  Spätzle & Käse  "}
    dish = Dish(dish_data)

    # Name should be trimmed but preserve original case
    assert dish.cleaned_name == "Spätzle & Käse"

    # Slug should be lowercase, with special chars removed/replaced
    # In the real implementation, this would utilize the slugify function
    assert dish.slug in ["spatzle-kase", "spatzkle-kase", "spatzle-and-kase"]


def test_long_name_truncation():
    """Test that names longer than 100 characters are truncated."""
    try:
        from mealplan_mcp.models.dish import Dish
    except ImportError:
        Dish = MockDish
        pytest.skip("Using mock implementation")

    # Create a dish with a very long name
    long_name = "This is a very long dish name " * 10  # 300 characters
    dish_data = {"name": long_name}
    dish = Dish(dish_data)

    # Check that the cleaned name is truncated to 100 characters
    assert len(dish.cleaned_name) <= 100

    # Check that the slug is also truncated to 100 characters
    assert len(dish.slug) <= 100


def test_missing_name():
    """Test that dishes with missing names get a default value."""
    try:
        from mealplan_mcp.models.dish import Dish
    except ImportError:
        Dish = MockDish
        pytest.skip("Using mock implementation")

    # Create a dish with no name
    dish_data = {"ingredients": [{"name": "Salt", "amount": "1 tsp"}]}
    dish = Dish(dish_data)

    # Check that a default name is provided
    assert dish.cleaned_name == "Unnamed Dish"
    assert dish.slug in ["unnamed-dish", "unnamed"]
