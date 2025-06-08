"""
Markdown renderer for meal plans.

This module provides functions to render meal plans in various markdown formats,
separating content generation from the business logic.
"""

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.models.dish import Dish


def render_mealplan_markdown(meal_plan: MealPlan) -> str:
    """
    Render a meal plan as markdown content for saving to file.

    Args:
        meal_plan: The meal plan to render

    Returns:
        str: Markdown content ready to be written to file
    """
    # Format date components for display and task
    date_str = meal_plan.date.strftime("%Y-%m-%d")
    year = meal_plan.date.strftime("%Y")
    month_num = meal_plan.date.strftime("%m")
    day = meal_plan.date.strftime("%d")

    meal_type_str = meal_plan.meal_type.value
    title = meal_plan.cleaned_title or meal_plan.title
    cook = meal_plan.cook

    # Create markdown task at the top
    task = f"- [ ] {title} ({meal_type_str},{cook}) #mealplan [scheduled:: {year}-{month_num}-{day}]\n\n"

    # Create content in Markdown format
    content = task
    content += f"# {title}\n\n"
    content += f"**Date:** {date_str}  \n"
    content += f"**Meal Type:** {meal_type_str}  \n"
    content += f"**Cook:** {cook}  \n\n"

    # Add dishes information
    dishes = meal_plan.dishes
    content += f"## Dishes ({len(dishes)})\n\n"

    for i, dish in enumerate(dishes, 1):
        content += _render_dish_section(dish, i)

    return content


def render_mealplan_summary(meal_plan: MealPlan) -> str:
    """
    Render a meal plan as a summary for console output/return value.

    Args:
        meal_plan: The meal plan to render

    Returns:
        str: Summary text for display or return value
    """
    # Format date components
    date_str = meal_plan.date.strftime("%Y-%m-%d")
    year = meal_plan.date.strftime("%Y")
    month_num = meal_plan.date.strftime("%m")
    day = meal_plan.date.strftime("%d")

    meal_type_str = meal_plan.meal_type.value
    title = meal_plan.cleaned_title or meal_plan.title
    cook = meal_plan.cook

    # Generate console output
    result = f"Markdown Task: - [ ] {title} ({meal_type_str},{cook}) #mealplan [scheduled:: {year}-{month_num}-{day}]"
    result += f"\n\nMeal Plan: {title} ({meal_type_str}) on {date_str} cooked by {cook}"
    result += f"\n\nDishes ({len(meal_plan.dishes)}):"

    for i, dish in enumerate(meal_plan.dishes, 1):
        result += _render_dish_summary(dish, i)

    return result


def _render_dish_section(dish: Dish, index: int) -> str:
    """
    Render a single dish as a markdown section.

    Args:
        dish: The dish to render
        index: The dish number/index

    Returns:
        str: Markdown section for the dish
    """
    # Get dish name safely
    dish_name = getattr(dish, "name", f"Dish {index}")
    content = f"### {index}. {dish_name}\n\n"

    # Add ingredients safely
    content += "#### Ingredients\n\n"
    ingredients = getattr(dish, "ingredients", [])
    if not ingredients:
        content += "- None specified\n\n"
    else:
        for ingredient in ingredients:
            ing_name = getattr(ingredient, "name", "Unknown")
            ing_amount = getattr(ingredient, "amount", "Amount not specified")
            content += f"- {ing_name}: {ing_amount}\n"
        content += "\n"

    # Add instructions safely
    instructions = getattr(dish, "instructions", "No instructions provided")
    content += "#### Instructions\n\n"
    content += instructions.replace("\n", "\n\n")
    content += "\n\n"

    # Add nutrients if available
    nutrients = getattr(dish, "nutrients", [])
    if nutrients:
        content += "#### Nutrients\n\n"
        for nutrient in nutrients:
            nut_name = getattr(nutrient, "name", "Unknown")
            nut_amount = getattr(nutrient, "amount", 0)
            nut_unit = getattr(nutrient, "unit", "")
            content += f"- {nut_name}: {nut_amount} {nut_unit}\n"
        content += "\n"

    return content


def _render_dish_summary(dish: Dish, index: int) -> str:
    """
    Render a single dish as a summary for console output.

    Args:
        dish: The dish to render
        index: The dish number/index

    Returns:
        str: Summary text for the dish
    """
    dish_name = getattr(dish, "name", f"Dish {index}")
    result = f"\n\n{index}. {dish_name}"

    # Add ingredients
    result += "\n   Ingredients:"
    ingredients = getattr(dish, "ingredients", [])
    if not ingredients:
        result += "\n   - None specified"
    else:
        for ingredient in ingredients:
            ing_name = getattr(ingredient, "name", "Unknown")
            ing_amount = getattr(ingredient, "amount", "Amount not specified")
            result += f"\n   - {ing_name}: {ing_amount}"

    # Add instructions
    instructions = getattr(dish, "instructions", "No instructions provided")
    result += f"\n\n   Instructions:\n   {instructions.replace('\n', '\n   ')}"

    # Add nutrients if available
    nutrients = getattr(dish, "nutrients", [])
    if nutrients:
        result += "\n\n   Nutrients:"
        for nutrient in nutrients:
            nut_name = getattr(nutrient, "name", "Unknown")
            nut_amount = getattr(nutrient, "amount", 0)
            nut_unit = getattr(nutrient, "unit", "")
            result += f"\n   - {nut_name}: {nut_amount} {nut_unit}"

    return result
