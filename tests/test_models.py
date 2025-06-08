"""Basic tests for models."""

from mealplan_mcp.models.meal_type import MealType


def test_meal_type_enum():
    """Test that MealType enum exists and has expected values."""
    assert MealType.BREAKFAST.value == "breakfast"
    assert MealType.LUNCH.value == "lunch"
    assert MealType.DINNER.value == "dinner"
    assert MealType.SNACK.value == "snack"
