"""
Tests for the meal plan markdown renderer.
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.models.meal_type import MealType
from mealplan_mcp.renderers.mealplan import (
    render_mealplan_markdown,
    render_mealplan_summary,
)


def test_render_mealplan_markdown_basic():
    """Test rendering basic meal plan markdown."""
    date = datetime(2023, 6, 15, 18, 30)
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.DINNER,
        title="Italian Night",
        cook="Chef Mario",
        dishes=[],
    )

    result = render_mealplan_markdown(meal_plan)

    # Check that markdown task is at the top
    assert result.startswith(
        "- [ ] Italian Night (dinner,Chef Mario) #mealplan [scheduled:: 2023-06-15]"
    )

    # Check main content structure
    assert "# Italian Night" in result
    assert "**Date:** 2023-06-15" in result
    assert "**Meal Type:** dinner" in result
    assert "**Cook:** Chef Mario" in result
    assert "## Dishes (0)" in result


def test_render_mealplan_markdown_with_cleaned_title():
    """Test that markdown renderer uses cleaned title."""
    date = datetime(2023, 6, 15)
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.BREAKFAST,
        title="  Fancy Breakfast   ",  # Has whitespace
        cook="Chef",
        dishes=[],
    )

    result = render_mealplan_markdown(meal_plan)

    # Should use cleaned title in content
    assert "# Fancy Breakfast" in result
    assert "- [ ] Fancy Breakfast (breakfast,Chef)" in result


def test_render_mealplan_summary_basic():
    """Test rendering basic meal plan summary."""
    date = datetime(2023, 6, 15, 18, 30)
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.LUNCH,
        title="Quick Lunch",
        cook="Home Cook",
        dishes=[],
    )

    result = render_mealplan_summary(meal_plan)

    # Check summary structure
    assert result.startswith(
        "Markdown Task: - [ ] Quick Lunch (lunch,Home Cook) #mealplan [scheduled:: 2023-06-15]"
    )
    assert "Meal Plan: Quick Lunch (lunch) on 2023-06-15 cooked by Home Cook" in result
    assert "Dishes (0):" in result


def test_render_mealplan_with_different_meal_types():
    """Test rendering with different meal types."""
    date = datetime(2023, 6, 15)

    for meal_type in [
        MealType.BREAKFAST,
        MealType.LUNCH,
        MealType.DINNER,
        MealType.SNACK,
    ]:
        meal_plan = MealPlan(
            date=date,
            meal_type=meal_type,
            title="Test Meal",
            cook="Test Cook",
            dishes=[],
        )

        markdown = render_mealplan_markdown(meal_plan)
        summary = render_mealplan_summary(meal_plan)

        meal_type_str = meal_type.value
        assert f"**Meal Type:** {meal_type_str}" in markdown
        assert f"({meal_type_str},Test Cook)" in markdown
        assert f"({meal_type_str}) on 2023-06-15" in summary


def test_render_mealplan_date_formatting():
    """Test that dates are formatted correctly in different components."""
    # Test different date scenarios
    dates = [
        datetime(2023, 1, 1),  # New Year's Day
        datetime(2023, 12, 31),  # New Year's Eve
        datetime(2023, 6, 5),  # Single digit day
    ]

    for date in dates:
        meal_plan = MealPlan(
            date=date,
            meal_type=MealType.DINNER,
            title="Test Meal",
            cook="Test Cook",
            dishes=[],
        )

        markdown = render_mealplan_markdown(meal_plan)
        summary = render_mealplan_summary(meal_plan)

        date_str = date.strftime("%Y-%m-%d")
        year = date.strftime("%Y")
        month_num = date.strftime("%m")
        day = date.strftime("%d")

        # Check date formatting in both outputs
        assert f"**Date:** {date_str}" in markdown
        assert f"[scheduled:: {year}-{month_num}-{day}]" in markdown
        assert f"on {date_str}" in summary


def test_render_mealplan_default_values():
    """Test rendering with default values."""
    date = datetime.now()
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.DINNER,
        # Using defaults for title and cook
    )

    markdown = render_mealplan_markdown(meal_plan)
    summary = render_mealplan_summary(meal_plan)

    # Should use default values
    assert "# Untitled Meal" in markdown
    assert "**Cook:** Unknown" in markdown
    assert "Untitled Meal (dinner,Unknown)" in summary


def test_render_empty_dishes_section():
    """Test rendering when there are no dishes."""
    date = datetime(2023, 6, 15)
    meal_plan = MealPlan(
        date=date, meal_type=MealType.SNACK, title="Light Snack", cook="Self", dishes=[]
    )

    markdown = render_mealplan_markdown(meal_plan)
    summary = render_mealplan_summary(meal_plan)

    # Should show 0 dishes
    assert "## Dishes (0)" in markdown
    assert "Dishes (0):" in summary
