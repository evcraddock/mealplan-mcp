"""
Service for storing meal plan data.

This module provides the store_mealplan service for persisting meal plan data
to the filesystem, including handling atomic file operations and directory creation.
"""

import os
import tempfile
from pathlib import Path
from typing import Set

from models.meal_plan import MealPlan
from mealplan_mcp.utils.paths import mealplan_directory_path
from mealplan_mcp.renderers.mealplan import render_mealplan_markdown
from mealplan_mcp.utils.slugify import suffix_if_exists


def store_mealplan(meal_plan: MealPlan) -> Path:
    """
    Store a meal plan to a markdown file based on its date and meal type.

    If a meal plan with the same path already exists, a numerical suffix
    is added to the filename to ensure uniqueness.

    Args:
        meal_plan: The meal plan model instance to store

    Returns:
        The path to the stored meal plan file
    """
    # Get the meal type as string
    meal_type_str = meal_plan.meal_type.value

    # Get all existing meal plan files for this date
    existing_files = _get_existing_mealplan_files(meal_plan.date)

    # Check if the basic filename already exists
    base_filename = f"{meal_type_str}.md"

    # If the file exists, append a suffix to the base name (before extension)
    if base_filename in existing_files:
        # Extract base name and extension
        base_name = meal_type_str
        extension = ".md"

        # Get existing base names (without extension) for suffix checking
        existing_base_names = {
            f.replace(".md", "") for f in existing_files if f.endswith(".md")
        }

        # Find a unique base name
        final_base_name = suffix_if_exists(base_name, existing_base_names)
        final_filename = f"{final_base_name}{extension}"
    else:
        final_filename = base_filename

    # Get the directory path for this date
    dir_path = mealplan_directory_path(meal_plan.date)

    # Ensure the parent directory exists
    dir_path.mkdir(parents=True, exist_ok=True)

    # Get the final file path
    file_path = dir_path / final_filename

    # Generate the markdown content
    markdown_content = render_mealplan_markdown(meal_plan)

    # Use atomic write to ensure the file is either completely written or not at all
    # This prevents corrupted files if the process is interrupted during writing
    with tempfile.NamedTemporaryFile(mode="w", delete=False, dir=dir_path) as tf:
        # Write meal plan data to the temporary file
        tf.write(markdown_content)

        # Make sure data is flushed to disk
        tf.flush()
        os.fsync(tf.fileno())

        # Get temporary file name
        temp_name = tf.name

    # Atomically replace the target file with the temporary file
    # This is the atomic write operation
    os.replace(temp_name, file_path)

    # Return the path to the stored file
    return file_path


def _get_existing_mealplan_files(date) -> Set[str]:
    """
    Get the set of existing meal plan files for a specific date.

    Args:
        date: The date to check for existing meal plans

    Returns:
        A set of existing meal plan file names (including .md extension)
    """
    # Get the directory for this date
    dir_path = mealplan_directory_path(date)

    # If the directory doesn't exist, no files exist
    if not dir_path.exists():
        return set()

    # Get all markdown files and extract their names
    files = set()
    for file_path in dir_path.glob("*.md"):
        files.add(file_path.name)

    return files
