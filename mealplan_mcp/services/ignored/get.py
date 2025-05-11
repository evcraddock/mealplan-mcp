"""
Service for retrieving ignored ingredients.

This module provides the get_ignored_ingredients service that returns
the list of ingredients that should be excluded from grocery lists.
"""

from typing import List

from mealplan_mcp.models.ignored import IgnoredStore


def get_ignored_ingredients() -> List[str]:
    """
    Get the list of ignored ingredients.

    Returns:
        A sorted list of ingredient names to be ignored in grocery lists.
    """
    # Get the store and load the ingredients
    store = IgnoredStore()
    ingredients = store.load()

    # Sort the ingredients alphabetically
    return sorted(ingredients)
