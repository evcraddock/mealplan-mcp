"""
Tests for the get_ignored_ingredients service.

These tests verify that the service correctly returns a sorted list of
ignored ingredients from the IgnoredStore.
"""

import pytest


# Create a mock implementation for tests
class MockIgnoredStore:
    """Mock implementation of IgnoredStore for testing."""

    def __init__(self, path=None):
        self.ingredients = []

    def load(self):
        return self.ingredients


@pytest.fixture
def mock_store():
    """Return a mock IgnoredStore instance."""
    return MockIgnoredStore()


def test_get_empty_list(monkeypatch):
    """Test that an empty ingredients list is returned when store is empty."""
    try:
        from mealplan_mcp.services.ignored import get_ignored_ingredients

        # Create a mock store with no ingredients
        mock_store = MockIgnoredStore()

        # Mock the IgnoredStore to return our mock
        monkeypatch.setattr(
            "mealplan_mcp.services.ignored.get.IgnoredStore",
            lambda *args, **kwargs: mock_store,
        )

        # Call the service
        ingredients = get_ignored_ingredients()

        # Verify an empty list is returned
        assert isinstance(ingredients, list)
        assert len(ingredients) == 0

    except ImportError:
        pytest.skip("Implementation not available yet")


def test_get_sorted_list(monkeypatch):
    """Test that ingredients are returned sorted alphabetically."""
    try:
        from mealplan_mcp.services.ignored import get_ignored_ingredients

        # Create a mock store with unsorted ingredients
        mock_store = MockIgnoredStore()
        mock_store.ingredients = ["pepper", "basil", "salt"]

        # Mock the IgnoredStore to return our mock
        monkeypatch.setattr(
            "mealplan_mcp.services.ignored.get.IgnoredStore",
            lambda *args, **kwargs: mock_store,
        )

        # Call the service
        ingredients = get_ignored_ingredients()

        # Verify the list is sorted alphabetically
        assert isinstance(ingredients, list)
        assert len(ingredients) == 3
        assert ingredients == ["basil", "pepper", "salt"]

    except ImportError:
        pytest.skip("Implementation not available yet")


def test_get_duplicate_handling(monkeypatch):
    """Test that any duplicates in the store are handled correctly."""
    try:
        from mealplan_mcp.services.ignored import get_ignored_ingredients

        # Create a mock store with duplicate ingredients
        mock_store = MockIgnoredStore()
        mock_store.ingredients = ["salt", "pepper", "salt"]

        # Mock the IgnoredStore to return our mock
        monkeypatch.setattr(
            "mealplan_mcp.services.ignored.get.IgnoredStore",
            lambda *args, **kwargs: mock_store,
        )

        # Call the service
        ingredients = get_ignored_ingredients()

        # Verify duplicates are preserved (deduplication is IgnoredStore's responsibility)
        # But the list should still be sorted
        assert isinstance(ingredients, list)
        assert len(ingredients) == 3
        assert ingredients == ["pepper", "salt", "salt"]

    except ImportError:
        pytest.skip("Implementation not available yet")
