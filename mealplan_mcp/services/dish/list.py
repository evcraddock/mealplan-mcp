"""
Service for listing dishes.

This module provides the list_dishes service for retrieving dish data
from the filesystem, with alphabetical natural sorting by dish name.
"""

import json
from typing import List

from mealplan_mcp.models.dish import Dish
from mealplan_mcp.utils.paths import dish_path


def list_dishes() -> List[Dish]:
    """
    List all dishes stored in the dish directory.

    Returns dishes sorted alphabetically by their internal name.
    Skips any corrupt JSON files.

    Returns:
        List of Dish objects sorted by name
    """
    # Get the dishes directory
    dishes_dir = dish_path("").parent

    # Create the directory if it doesn't exist
    dishes_dir.mkdir(parents=True, exist_ok=True)

    # Get all JSON files
    json_files = dishes_dir.glob("*.json")

    # Load each file into a Dish object
    dishes = []

    for file_path in json_files:
        # Skip files that don't exist (should never happen, but just in case)
        if not file_path.exists():
            continue

        try:
            # Read the file
            json_data = file_path.read_text(encoding="utf-8")

            # Parse the JSON and create a Dish object
            dish_data = json.loads(json_data)
            dish = Dish(**dish_data)

            # Add the dish to our list
            dishes.append(dish)
        except (json.JSONDecodeError, ValueError, KeyError):
            # Skip files with invalid JSON, validation errors, or missing keys
            continue

    # Sort the dishes by name
    dishes.sort(key=lambda dish: dish.name)

    return dishes
