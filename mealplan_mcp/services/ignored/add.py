"""
Service for adding ignored ingredients.

This module provides the add_ingredient service that allows users to
add ingredients to the ignored ingredients list.
"""

from mealplan_mcp.models.ignored import IgnoredStore


def add_ingredient(name: str) -> None:
    """
    Add an ingredient to the ignored ingredients list.

    The ingredient name will be:
    - Validated (cannot be empty)
    - Trimmed (whitespace removed)
    - Lowercased

    Args:
        name: The name of the ingredient to ignore

    Raises:
        ValueError: If the ingredient name is empty or whitespace only
    """
    # Validate the ingredient name
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Ingredient name cannot be empty")

    # Lowercase the name
    cleaned_name = cleaned_name.lower()

    # Get the store and add the ingredient
    store = IgnoredStore()
    store.add(cleaned_name)
