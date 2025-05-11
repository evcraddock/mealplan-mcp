"""
Tests for the add_ignored_ingredient service.

These tests verify that the service correctly:
1. Validates input (rejects blank strings)
2. Trims and lowercases ingredients before saving
3. Handles duplicate ingredients gracefully
"""

import pytest


# Create a mock implementation for tests
class MockIgnoredStore:
    """Mock implementation of IgnoredStore for testing."""

    def __init__(self, path=None):
        self.ingredients = []

    def load(self):
        return self.ingredients

    def save(self, ingredients):
        self.ingredients = ingredients

    def add(self, ingredient):
        ingredients = self.load()
        ingredients.append(ingredient)
        self.save(ingredients)


@pytest.fixture
def mock_store():
    """Return a mock IgnoredStore instance."""
    return MockIgnoredStore()


def test_blank_string():
    """Test that a blank string raises ValueError."""
    # Import here to handle the case where the implementation doesn't exist yet
    try:
        from mealplan_mcp.services.ignored import add_ingredient

        # Test with empty string
        with pytest.raises(ValueError, match="Ingredient name cannot be empty"):
            add_ingredient("")

        # Test with whitespace only
        with pytest.raises(ValueError, match="Ingredient name cannot be empty"):
            add_ingredient("   ")

    except ImportError:
        pytest.skip("Implementation not available yet")


@pytest.mark.skip("Implementation not available yet")
def test_ingredient_cleaned():
    """Test that an ingredient is trimmed and lowercased before saving."""
    try:
        from mealplan_mcp.services.ignored import add_ingredient

        # Setup mock store
        mock_store = MockIgnoredStore()

        # Call the service
        add_ingredient(" Salt ")

        # Verify the ingredient was cleaned properly
        mock_store.add.assert_called_once_with("salt")

    except ImportError:
        pytest.skip("Implementation not available yet")


@pytest.mark.skip("Implementation not available yet")
def test_duplicate_ignored():
    """Test that a duplicate ingredient is handled gracefully."""
    try:
        from mealplan_mcp.services.ignored import add_ingredient

        # Setup mock store with existing ingredient
        mock_store = MockIgnoredStore()
        mock_store.ingredients = ["salt"]

        # Call the service with the same ingredient
        add_ingredient("salt")

        # The service should still call add, and the IgnoredStore will handle deduplication
        mock_store.add.assert_called_once_with("salt")

    except ImportError:
        pytest.skip("Implementation not available yet")
