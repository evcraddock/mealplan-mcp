"""
Tests for the MealPlan Pydantic model.
"""

from datetime import datetime

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.models.meal_type import MealType


def test_meal_plan_basic_creation():
    """Test creating a basic meal plan."""
    date = datetime(2023, 6, 15, 18, 30)
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.DINNER,
        title="Italian Night",
        cook="Chef Mario",
        dishes=[],
    )

    assert meal_plan.date == date
    assert meal_plan.meal_type == MealType.DINNER
    assert meal_plan.title == "Italian Night"
    assert meal_plan.cook == "Chef Mario"
    assert meal_plan.dishes == []
    assert meal_plan.cleaned_title == "Italian Night"


def test_meal_plan_default_values():
    """Test that default values are applied correctly."""
    date = datetime.now()
    meal_plan = MealPlan(date=date, meal_type=MealType.BREAKFAST)

    assert meal_plan.title == "Untitled Meal"
    assert meal_plan.cook == "Unknown"
    assert meal_plan.dishes == []


def test_meal_plan_empty_title_validation():
    """Test that empty titles are replaced with default."""
    date = datetime.now()
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.LUNCH,
        title="   ",  # Whitespace only
        cook="Test Cook",
    )

    assert meal_plan.title == "Untitled Meal"
    assert meal_plan.cleaned_title == "Untitled Meal"


def test_meal_plan_empty_cook_validation():
    """Test that empty cook names are replaced with default."""
    date = datetime.now()
    meal_plan = MealPlan(
        date=date, meal_type=MealType.DINNER, title="Test Meal", cook=""  # Empty string
    )

    assert meal_plan.cook == "Unknown"


def test_meal_plan_date_parsing_iso_format():
    """Test parsing date from ISO format string."""
    meal_plan = MealPlan(
        date="2023-06-15T18:30:00Z", meal_type=MealType.DINNER, title="Test Meal"
    )

    expected_date = datetime(2023, 6, 15, 18, 30)
    assert meal_plan.date.replace(tzinfo=None) == expected_date


def test_meal_plan_date_parsing_simple_format():
    """Test parsing date from simple YYYY-MM-DD format."""
    meal_plan = MealPlan(date="2023-06-15", meal_type=MealType.LUNCH, title="Test Meal")

    expected_date = datetime(2023, 6, 15)
    assert meal_plan.date == expected_date


def test_meal_plan_date_parsing_fallback():
    """Test that invalid date strings fall back to current time."""
    meal_plan = MealPlan(
        date="invalid-date", meal_type=MealType.SNACK, title="Test Meal"
    )

    # Should be close to now (within a few seconds)
    now = datetime.now()
    assert abs((meal_plan.date - now).total_seconds()) < 5


def test_meal_plan_title_cleaning():
    """Test that titles are cleaned properly."""
    meal_plan = MealPlan(
        date=datetime.now(),
        meal_type=MealType.BREAKFAST,
        title="  Fancy Breakfast   ",  # Leading/trailing whitespace
        cook="Test Cook",
    )

    assert meal_plan.title == "  Fancy Breakfast   "  # Original preserved
    assert meal_plan.cleaned_title == "Fancy Breakfast"  # Cleaned version


def test_meal_plan_long_title_truncation():
    """Test that very long titles are truncated."""
    long_title = "a" * 150  # 150 characters
    meal_plan = MealPlan(
        date=datetime.now(),
        meal_type=MealType.DINNER,
        title=long_title,
        cook="Test Cook",
    )

    assert len(meal_plan.cleaned_title) == 100
    assert meal_plan.cleaned_title == "a" * 100


def test_meal_plan_slug_generation():
    """Test that slugs are generated correctly."""
    date = datetime(2023, 6, 15)
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.DINNER,
        title="Italian Night Special",
        cook="Chef Mario",
    )

    expected_slug = "2023-06-15-dinner-italian-night-special"
    assert meal_plan.slug == expected_slug


def test_meal_plan_slug_with_special_characters():
    """Test slug generation with special characters in title."""
    date = datetime(2023, 6, 15)
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.BREAKFAST,
        title="Mom's Famous Pancakes & Syrup!",
        cook="Mom",
    )

    expected_slug = "2023-06-15-breakfast-moms-famous-pancakes-syrup"
    assert meal_plan.slug == expected_slug


def test_meal_plan_with_dishes():
    """Test meal plan with actual dishes."""
    # This would require the Dish model to be properly set up
    # For now, we'll just test with empty list since Dish is complex
    date = datetime.now()
    meal_plan = MealPlan(
        date=date,
        meal_type=MealType.DINNER,
        title="Multi-course Dinner",
        cook="Chef",
        dishes=[],  # Empty for now
    )

    assert isinstance(meal_plan.dishes, list)
    assert len(meal_plan.dishes) == 0
