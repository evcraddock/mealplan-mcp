"""
Model for ignored ingredients in recipes.

This module provides the IgnoredStore class for managing a list of
ingredients to be excluded from grocery lists.
"""

import json
from pathlib import Path
from typing import List, Optional, Union

from mealplan_mcp.utils.paths import mealplan_root


class IgnoredStore:
    """
    A store for managing a list of ignored ingredients.

    This class provides functionality for loading and saving a list of
    ignored ingredients from/to a JSON file.

    The store ensures that ingredients are:
    - Stored as lowercase
    - Deduplicated (no duplicates in the list)
    - Persisted to a JSON file
    """

    def __init__(self, path: Optional[Union[str, Path]] = None):
        """
        Initialize an IgnoredStore with a path.

        Args:
            path: Path to the ignored ingredients JSON file.
                 If not provided, uses the default path.
        """
        if path is None:
            self.path = mealplan_root / "ignored_ingredients.json"
        else:
            self.path = Path(path)

    def load(self) -> List[str]:
        """
        Load the list of ignored ingredients from the JSON file.

        Returns:
            An empty list if the file doesn't exist or is empty,
            otherwise the list of ignored ingredients.
        """
        if not self.path.exists() or self.path.stat().st_size == 0:
            return []

        try:
            with self.path.open("r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Return an empty list if the file is not valid JSON
            return []

    def save(self, ingredients: List[str]) -> None:
        """
        Save a list of ignored ingredients to the JSON file.

        The ingredients will be:
        - Converted to lowercase
        - Deduplicated

        Args:
            ingredients: The list of ingredients to save
        """
        # Ensure parent directory exists
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Normalize ingredients: lowercase and deduplicate
        normalized = set(ingredient.lower() for ingredient in ingredients)
        sorted_ingredients = sorted(normalized)

        # Write to file
        with self.path.open("w") as f:
            json.dump(sorted_ingredients, f, indent=2)

    def add(self, ingredient: str) -> None:
        """
        Add a new ingredient to the ignored list.

        The ingredient will be added to the existing list, lowercased,
        and the list will be deduplicated before saving.

        Args:
            ingredient: The ingredient to add
        """
        # Load existing ingredients
        ingredients = self.load()

        # Add new ingredient
        ingredients.append(ingredient)

        # Save updated list
        self.save(ingredients)

    def __str__(self) -> str:
        """String representation of the path."""
        return str(self.path)
