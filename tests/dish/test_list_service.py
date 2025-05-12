"""
Tests for the dish listing service.

This test module verifies that the list_dishes service:
1. Returns dishes sorted alphabetically by internal name
2. Skips any corrupt JSON files
3. Properly loads and returns dish objects
"""

import json
import sys
import os

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the service (will be implemented later)
from mealplan_mcp.services.dish import list_dishes


def test_list_dishes_empty(monkeypatch, tmp_path):
    """Test that an empty dishes directory returns an empty list."""
    # Setup a temporary empty directory structure for testing
    dishes_dir = tmp_path / "dishes"
    dishes_dir.mkdir(parents=True)

    # Mock dish_path to point to our temporary directory
    def mock_dish_path(slug):
        return dishes_dir / f"{slug}.json"

    # Patch dish_path
    monkeypatch.setattr("mealplan_mcp.services.dish.list.dish_path", mock_dish_path)

    # Run the service
    result = list_dishes()

    # Check the result
    assert isinstance(result, list)
    assert len(result) == 0


def test_list_dishes_sorted(monkeypatch, tmp_path):
    """Test that dishes are returned sorted by their internal name."""
    # Create test dishes with different names (intentionally out of order)
    dish_data = [
        {"name": "Zucchini Pasta", "slug": "zucchini-pasta"},
        {"name": "Apple Pie", "slug": "apple-pie"},
        {"name": "Meatballs", "slug": "meatballs"},
    ]

    # Setup a temporary directory structure for testing
    dishes_dir = tmp_path / "dishes"
    dishes_dir.mkdir(parents=True)

    # Create actual JSON files in the temporary directory
    for dish in dish_data:
        dish_file = dishes_dir / f"{dish['slug']}.json"
        dish_file.write_text(json.dumps(dish))

    # Mock dish_path to point to our temporary directory
    def mock_dish_path(slug):
        return dishes_dir / f"{slug}.json"

    # Patch dish_path
    monkeypatch.setattr("mealplan_mcp.services.dish.list.dish_path", mock_dish_path)

    # Run the service
    result = list_dishes()

    # Check the result
    assert isinstance(result, list)
    assert len(result) == 3

    # Verify dishes are sorted by name
    assert result[0].name == "Apple Pie"
    assert result[1].name == "Meatballs"
    assert result[2].name == "Zucchini Pasta"


def test_list_dishes_skips_corrupt_json(monkeypatch, tmp_path):
    """Test that corrupt JSON files are skipped."""
    # Setup a temporary directory structure for testing
    dishes_dir = tmp_path / "dishes"
    dishes_dir.mkdir(parents=True)

    # Create a valid JSON file
    valid_path = dishes_dir / "valid.json"
    valid_path.write_text('{"name": "Valid Dish", "slug": "valid"}')

    # Create a corrupt JSON file
    corrupt_path = dishes_dir / "corrupt.json"
    corrupt_path.write_text("{invalid json")

    # Mock dish_path to point to our temporary directory
    def mock_dish_path(slug):
        return dishes_dir / f"{slug}.json"

    # Patch dish_path
    monkeypatch.setattr("mealplan_mcp.services.dish.list.dish_path", mock_dish_path)

    # Run the service
    result = list_dishes()

    # Check the result
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].name == "Valid Dish"
