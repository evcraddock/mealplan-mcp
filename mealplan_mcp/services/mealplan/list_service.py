"""
Service for listing meal plan data by date range.

This module provides the list_mealplans_by_date_range service for querying
meal plan data within a specified date range, extracting dish names from both
markdown and JSON files.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from mealplan_mcp.utils.paths import mealplan_root


def list_mealplans_by_date_range(
    start_date: str, end_date: str
) -> List[Dict[str, Any]]:
    """
    List meal plans within a specified date range.

    Args:
        start_date: Start date in YYYY-MM-DD format (inclusive)
        end_date: End date in YYYY-MM-DD format (inclusive)

    Returns:
        List of meal plan dictionaries with keys:
        - title: Cleaned meal title
        - date: Date in YYYY-MM-DD format
        - meal_type: Type of meal (breakfast, lunch, dinner, snack)
        - cook: Person cooking the meal
        - dishes: List of dish names

    Raises:
        ValueError: If date format is invalid or end_date is before start_date
    """
    try:
        # Parse the date strings
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {e}")

    # If end date is before start date, return empty list (graceful handling)
    if end_dt < start_dt:
        return []

    meal_plans = []

    # Walk through the mealplan directory structure
    current_mealplan_root = Path(mealplan_root)

    if not current_mealplan_root.exists():
        return []

    # Iterate through year directories
    for year_dir in current_mealplan_root.iterdir():
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue

        # Iterate through month directories (MM-MonthName format)
        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue

            # Iterate through date directories (MM-DD-YYYY format)
            for date_dir in month_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                # Extract date from directory name (MM-DD-YYYY)
                date_match = re.match(r"(\d{2})-(\d{2})-(\d{4})", date_dir.name)
                if not date_match:
                    continue

                month, day, year = date_match.groups()
                try:
                    file_date = datetime(int(year), int(month), int(day))
                except ValueError:
                    continue

                # Check if date is within our range
                if start_dt <= file_date <= end_dt:
                    # Process all meal plan files in this directory
                    meal_plans.extend(_process_date_directory(date_dir, file_date))

    # Sort by date, then by meal type, then by title
    meal_plans.sort(key=lambda x: (x["date"], x["meal_type"], x["title"]))

    return meal_plans


def _process_date_directory(
    date_dir: Path, file_date: datetime
) -> List[Dict[str, Any]]:
    """
    Process all meal plan files in a date directory.

    Args:
        date_dir: Path to the date directory
        file_date: The date for this directory

    Returns:
        List of meal plan dictionaries
    """
    meal_plans = []
    date_str = file_date.strftime("%Y-%m-%d")

    # Group files by base name to avoid duplicates
    # Since we store both .md and .json files, we need to process each meal plan only once
    file_groups = {}

    for file_path in date_dir.iterdir():
        if file_path.suffix not in {".md", ".json"}:
            continue

        # Extract meal type from filename (MM-DD-YYYY-mealtype.ext)
        filename_match = re.match(r"\d{2}-\d{2}-\d{4}-(.+)\.(md|json)$", file_path.name)
        if not filename_match:
            continue

        meal_type = filename_match.group(1)
        file_extension = filename_match.group(2)

        # Group by base name (without extension)
        base_name = file_path.stem  # filename without extension
        if base_name not in file_groups:
            file_groups[base_name] = {}
        file_groups[base_name][file_extension] = file_path

    # Process each meal plan (preferring JSON over markdown for data accuracy)
    for base_name, files in file_groups.items():
        # Extract meal type from base name
        base_match = re.match(r"\d{2}-\d{2}-\d{4}-(.+)$", base_name)
        if not base_match:
            continue
        meal_type = base_match.group(1)

        meal_plan_data = None

        # Prefer JSON file if available (more structured data)
        if "json" in files:
            meal_plan_data = _parse_json_meal_plan(files["json"], date_str, meal_type)
        elif "md" in files:
            meal_plan_data = _parse_markdown_meal_plan(files["md"], date_str, meal_type)

        if meal_plan_data:
            meal_plans.append(meal_plan_data)

    return meal_plans


def _parse_json_meal_plan(
    file_path: Path, date_str: str, meal_type: str
) -> Optional[Dict[str, Any]]:
    """
    Parse a JSON meal plan file.

    Args:
        file_path: Path to the JSON file
        date_str: Date string in YYYY-MM-DD format
        meal_type: Meal type extracted from filename

    Returns:
        Meal plan dictionary or None if parsing fails
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract dish names from the dishes array
        dish_names = []
        if "dishes" in data and isinstance(data["dishes"], list):
            for dish in data["dishes"]:
                if isinstance(dish, dict) and "name" in dish:
                    dish_names.append(dish["name"])
                elif isinstance(dish, str):
                    dish_names.append(dish)

        # Clean the title (same logic as in MealPlan model)
        title = data.get("title", "Untitled Meal")
        cleaned_title = title.strip()
        if len(cleaned_title) > 100:
            cleaned_title = cleaned_title[:100]
        if not cleaned_title:
            cleaned_title = "Untitled Meal"

        return {
            "title": cleaned_title,
            "date": date_str,
            "meal_type": meal_type,
            "cook": data.get("cook", "Unknown"),
            "dishes": dish_names,
        }

    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        return None


def _parse_markdown_meal_plan(
    file_path: Path, date_str: str, meal_type: str
) -> Optional[Dict[str, Any]]:
    """
    Parse a markdown meal plan file.

    Args:
        file_path: Path to the markdown file
        date_str: Date string in YYYY-MM-DD format
        meal_type: Meal type extracted from filename

    Returns:
        Meal plan dictionary or None if parsing fails
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract title from the first heading
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else "Untitled Meal"

        # Extract cook from the markdown
        cook_match = re.search(r"\*\*Cook:\*\* (.+)$", content, re.MULTILINE)
        cook = cook_match.group(1).strip() if cook_match else "Unknown"

        # Extract dish names from the dishes section
        dish_names = []

        # Look for the dishes section (starts with "## Dishes")
        dishes_match = re.search(
            r"^## Dishes.*?(?=^##|\Z)", content, re.MULTILINE | re.DOTALL
        )
        if dishes_match:
            dishes_section = dishes_match.group(0)

            # Find all dish headings (### Dish Name)
            dish_headings = re.findall(r"^### (.+)$", dishes_section, re.MULTILINE)
            dish_names = [dish.strip() for dish in dish_headings]

        return {
            "title": title,
            "date": date_str,
            "meal_type": meal_type,
            "cook": cook,
            "dishes": dish_names,
        }

    except (FileNotFoundError, UnicodeDecodeError):
        return None
