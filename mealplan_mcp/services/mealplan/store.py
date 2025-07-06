"""
Service for storing meal plan data.

This module provides the store_mealplan service for persisting meal plan data
to the filesystem, including handling atomic file operations and directory creation.
"""

import os
import tempfile
from pathlib import Path
from typing import Tuple

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.utils.paths import mealplan_path
from mealplan_mcp.renderers.mealplan import render_mealplan_markdown


def store_mealplan(meal_plan: MealPlan) -> Tuple[Path, Path]:
    """
    Store a meal plan to both markdown and JSON files based on its date and meal type.

    If a meal plan with the same path already exists, it will be overwritten.

    Args:
        meal_plan: The meal plan model instance to store

    Returns:
        A tuple containing (markdown_path, json_path) for the stored files
    """
    # Get the primary file path using the utility function
    primary_path = mealplan_path(meal_plan.date, meal_plan.meal_type.value)

    # Use the primary path directly - overwrite if exists
    markdown_path = primary_path
    json_path = primary_path.with_suffix(".json")

    # Ensure the parent directory exists
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate the markdown content
    markdown_content = render_mealplan_markdown(meal_plan)

    # Generate the JSON content
    json_content = meal_plan.model_dump_json(indent=2, exclude={"cleaned_title"})

    # Use atomic write to ensure both files are either completely written or not at all
    # This prevents corrupted files if the process is interrupted during writing

    # Write markdown file atomically
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, dir=markdown_path.parent, suffix=".md"
    ) as tf_md:
        # Write meal plan data to the temporary file
        tf_md.write(markdown_content)

        # Make sure data is flushed to disk
        tf_md.flush()
        os.fsync(tf_md.fileno())

        # Get temporary file name
        temp_md_name = tf_md.name

    # Write JSON file atomically
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, dir=json_path.parent, suffix=".json"
    ) as tf_json:
        # Write JSON data to the temporary file
        tf_json.write(json_content)

        # Make sure data is flushed to disk
        tf_json.flush()
        os.fsync(tf_json.fileno())

        # Get temporary file name
        temp_json_name = tf_json.name

    try:
        # Atomically replace the target files with the temporary files
        # This is the atomic write operation
        os.replace(temp_md_name, markdown_path)
        os.replace(temp_json_name, json_path)
    except Exception:
        # If something goes wrong, clean up the temporary files
        try:
            os.unlink(temp_md_name)
        except FileNotFoundError:
            pass
        try:
            os.unlink(temp_json_name)
        except FileNotFoundError:
            pass
        raise

    # Return the paths to both stored files
    return markdown_path, json_path
