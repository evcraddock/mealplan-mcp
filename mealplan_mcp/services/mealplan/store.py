"""
Service for storing meal plan data.

This module provides the store_mealplan service for persisting meal plan data
to the filesystem, including handling atomic file operations and directory creation.
"""

import os
import tempfile
from pathlib import Path
from typing import Set, Tuple

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.utils.paths import mealplan_directory_path, mealplan_path
from mealplan_mcp.renderers.mealplan import render_mealplan_markdown
from mealplan_mcp.utils.slugify import suffix_if_exists


def store_mealplan(meal_plan: MealPlan) -> Tuple[Path, Path]:
    """
    Store a meal plan to both markdown and JSON files based on its date and meal type.

    If a meal plan with the same path already exists, a numerical suffix
    is added to the filename to ensure uniqueness.

    Args:
        meal_plan: The meal plan model instance to store

    Returns:
        A tuple containing (markdown_path, json_path) for the stored files
    """
    # Get the primary file path using the utility function
    primary_path = mealplan_path(meal_plan.date, meal_plan.meal_type.value)

    # Get all existing meal plan files for this date
    existing_files = _get_existing_mealplan_files(meal_plan.date)

    # Check if the primary file already exists
    primary_filename = primary_path.name

    # If the file exists, append a suffix to the base name (before extension)
    if primary_filename in existing_files:
        # Extract base name and extension from the primary filename
        # For "06-15-2023-dinner.md", we want to suffix "06-15-2023-dinner"
        base_name = primary_filename.replace(".md", "")
        extension = ".md"

        # Get existing base names (without extension) for suffix checking
        existing_base_names = {
            f.replace(".md", "").replace(".json", "")
            for f in existing_files
            if f.endswith((".md", ".json"))
        }

        # Find a unique base name
        final_base_name = suffix_if_exists(base_name, existing_base_names)
        final_filename_md = f"{final_base_name}{extension}"
        final_filename_json = f"{final_base_name}.json"

        # Create the final paths in the same directory
        markdown_path = primary_path.parent / final_filename_md
        json_path = primary_path.parent / final_filename_json
    else:
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


def _get_existing_mealplan_files(date) -> Set[str]:
    """
    Get the set of existing meal plan files for a specific date.

    Args:
        date: The date to check for existing meal plans

    Returns:
        A set of existing meal plan file names (including .md and .json extensions)
    """
    # Get the directory for this date
    dir_path = mealplan_directory_path(date)

    # If the directory doesn't exist, no files exist
    if not dir_path.exists():
        return set()

    # Get all markdown and JSON files and extract their names
    files = set()
    for file_path in dir_path.glob("*"):
        if file_path.suffix in {".md", ".json"}:
            files.add(file_path.name)

    return files
