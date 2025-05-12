"""
Tests for the grocery markdown renderer.

These tests verify that the grocery markdown renderer correctly formats:
1. Headers for grocery lists with a date
2. Ingredient blocks with proper checkbox formatting and ordering
"""

import sys
import os
import pytest
from datetime import datetime, date

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_header_with_string_date():
    """Test that the header function correctly formats a string date."""
    try:
        from mealplan_mcp.renderers.grocery import header
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Test with a string date in the format YYYY-MM-DD
    test_date = "2025-05-10"
    result = header(test_date)

    # The header should be a markdown H2 with the date
    assert result == "## 2025-05-10"


def test_header_with_date_object():
    """Test that the header function correctly formats a date object."""
    try:
        from mealplan_mcp.renderers.grocery import header
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Test with a date object
    test_date = date(2025, 5, 10)
    result = header(test_date)

    # The header should be a markdown H2 with the date
    assert result == "## 2025-05-10"


def test_header_with_datetime_object():
    """Test that the header function correctly formats a datetime object."""
    try:
        from mealplan_mcp.renderers.grocery import header
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Test with a datetime object
    test_date = datetime(2025, 5, 10, 12, 30, 0)
    result = header(test_date)

    # The header should be a markdown H2 with the date (time part ignored)
    assert result == "## 2025-05-10"


def test_render_dish_ingredients_block():
    """Test that dish ingredients are rendered properly with checkboxes."""
    try:
        from mealplan_mcp.renderers.grocery import render_dish_ingredients
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Sample dish data
    dish = {
        "name": "Spaghetti Bolognese",
        "ingredients": [
            {"name": "ground beef", "amount": "500g"},
            {"name": "onion", "amount": "1 medium"},
            {"name": "garlic", "amount": "3 cloves"},
            {"name": "crushed tomatoes", "amount": "800g"},
        ],
    }

    result = render_dish_ingredients(dish)

    # Check if the dish name is correctly rendered as a header
    assert "### Spaghetti Bolognese" in result

    # Check if ingredients are rendered as checkboxes
    assert "- [ ] ground beef (500g)" in result
    assert "- [ ] onion (1 medium)" in result
    assert "- [ ] garlic (3 cloves)" in result
    assert "- [ ] crushed tomatoes (800g)" in result

    # Check the order of the ingredients (should match input order)
    first_ingredient_pos = result.find("ground beef")
    second_ingredient_pos = result.find("onion")
    third_ingredient_pos = result.find("garlic")
    fourth_ingredient_pos = result.find("crushed tomatoes")

    assert (
        first_ingredient_pos
        < second_ingredient_pos
        < third_ingredient_pos
        < fourth_ingredient_pos
    )


def test_render_dish_with_empty_ingredients():
    """Test rendering a dish with no ingredients."""
    try:
        from mealplan_mcp.renderers.grocery import render_dish_ingredients
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Sample dish with no ingredients
    dish = {"name": "Empty Dish", "ingredients": []}

    result = render_dish_ingredients(dish)

    # The dish name should still be included
    assert "### Empty Dish" in result

    # There should be a message about no ingredients
    assert "No ingredients" in result


def test_render_dish_with_non_standard_format():
    """Test that the renderer handles dish data in non-standard format."""
    try:
        from mealplan_mcp.renderers.grocery import render_dish_ingredients
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Dish with different structure
    dish = {
        "title": "Non-standard Dish",  # Using "title" instead of "name"
        "ingredients": [
            "flour - 200g",  # Ingredients as strings instead of objects
            "sugar - 100g",
            "eggs - 2",
        ],
    }

    result = render_dish_ingredients(dish)

    # Should still render a header with the dish name or title
    assert "### Non-standard Dish" in result

    # Should still render ingredients as checkboxes
    assert "- [ ] flour - 200g" in result
    assert "- [ ] sugar - 100g" in result
    assert "- [ ] eggs - 2" in result
