"""
Markdown renderer for grocery lists.

This module provides functions for rendering grocery lists in Markdown format.
"""

from datetime import datetime
from typing import Union, Any, Dict


def header(date_value: Union[str, datetime, Any]) -> str:
    """
    Generate a Markdown header for a grocery list with the given date.

    Args:
        date_value: A date as string (YYYY-MM-DD), datetime object, or date object

    Returns:
        A Markdown H2 header containing the date in YYYY-MM-DD format
    """
    # Handle string dates
    if isinstance(date_value, str):
        date_str = date_value
    # Handle datetime and date objects
    elif hasattr(date_value, "strftime"):
        date_str = date_value.strftime("%Y-%m-%d")
    # Handle other types (fallback)
    else:
        date_str = str(date_value)

    # Return the formatted header
    return f"## {date_str}"


def render_dish_ingredients(dish: Dict[str, Any]) -> str:
    """
    Render a dish's ingredients as a Markdown block with checkboxes.

    Args:
        dish: A dictionary containing dish data with 'name' (or 'title')
             and 'ingredients' fields

    Returns:
        A Markdown-formatted string with a header for the dish name
        and checkboxes for each ingredient
    """
    lines = []

    # Get the dish name, with fallbacks
    dish_name = dish.get("name", dish.get("title", "Unnamed Dish"))

    # Add dish name as a header
    lines.append(f"### {dish_name}")
    lines.append("")  # Empty line after header

    # Get ingredients
    ingredients = dish.get("ingredients", [])

    if not ingredients:
        lines.append("No ingredients listed for this dish.")
        return "\n".join(lines)

    # Process ingredients
    for ingredient in ingredients:
        if isinstance(ingredient, dict):
            # Handle dictionary format (name/amount)
            name = ingredient.get("name", "")
            amount = ingredient.get("amount", "")
            if name and amount:
                lines.append(f"- [ ] {name} ({amount})")
            elif name:
                lines.append(f"- [ ] {name}")
            else:
                # Skip empty ingredients
                continue
        elif isinstance(ingredient, str):
            # Handle string format
            lines.append(f"- [ ] {ingredient}")

    return "\n".join(lines)
