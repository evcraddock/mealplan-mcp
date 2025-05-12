"""
Service for storing dish data.

This module provides the store_dish service for persisting dish data
to the filesystem, including handling slug collisions.
"""

import os
import tempfile
from pathlib import Path
from typing import Set

from mealplan_mcp.models.dish import Dish
from mealplan_mcp.utils.paths import dish_path
from mealplan_mcp.utils.slugify import suffix_if_exists


def store_dish(dish: Dish) -> Path:
    """
    Store a dish to a JSON file based on its slug.

    If a dish with the same slug already exists, a numerical suffix
    is added to the slug to ensure uniqueness.

    Args:
        dish: The dish model instance to store

    Returns:
        The path to the stored dish file
    """
    # Get the base slug
    base_slug = dish.slug

    # Get all existing dish slugs
    existing_slugs = _get_existing_dish_slugs()

    # If the slug exists, append a suffix
    final_slug = suffix_if_exists(base_slug, existing_slugs)

    # Get the path to store the dish
    path = dish_path(final_slug)

    # Ensure the parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Use atomic write to ensure the file is either completely written or not at all
    # This prevents corrupted files if the process is interrupted during writing
    with tempfile.NamedTemporaryFile(mode="w", delete=False, dir=path.parent) as tf:
        # Write dish data to the temporary file
        json_data = dish.model_dump_json()
        tf.write(json_data)

        # Make sure data is flushed to disk
        tf.flush()
        os.fsync(tf.fileno())

        # Get temporary file name
        temp_name = tf.name

    # Atomically replace the target file with the temporary file
    # This is the atomic write operation
    os.replace(temp_name, path)

    # Return the path to the stored file
    return path


def _get_existing_dish_slugs() -> Set[str]:
    """
    Get the set of existing dish slugs from the dishes directory.

    Returns:
        A set of existing dish slug names (without the .json extension)
    """
    # Get the dishes directory
    dishes_dir = dish_path("").parent

    # Create the directory if it doesn't exist
    dishes_dir.mkdir(parents=True, exist_ok=True)

    # Get all JSON files and extract their slug names
    slugs = set()

    for file_path in dishes_dir.glob("*.json"):
        slugs.add(file_path.stem)  # stem is the filename without extension

    return slugs
