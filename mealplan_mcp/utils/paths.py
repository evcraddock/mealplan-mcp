"""
Path utilities for the Mealplan MCP server.

This module provides consistent path handling for various file types
used by the application, including dishes, grocery lists, and meal plans.
"""

import os
import calendar
from datetime import datetime
from pathlib import Path

# Get the meal plan root path from environment variable
# Default to current directory if not set
mealplan_root = Path(os.environ.get("MEALPLANPATH", os.getcwd()))


def dish_path(slug: str) -> Path:
    """
    Get the path to a dish file.

    Args:
        slug: The slug identifying the dish

    Returns:
        Path: The full path to the dish's JSON file
    """
    return mealplan_root / "dishes" / f"{slug}.json"


def mealplan_path(date: datetime, meal_type: str) -> Path:
    """
    Generate the path for a meal plan based on date and meal type.

    The path follows the pattern:
    $MEALPLANPATH/YYYY/MM-MonthName/MM-DD-YYYY/meal_type.md

    Args:
        date: The date for the meal plan
        meal_type: The type of meal (breakfast, lunch, dinner, snack)

    Returns:
        Path: The full path to the meal plan markdown file
    """
    # Get the current mealplan root path from environment
    current_mealplan_root = Path(os.environ.get("MEALPLANPATH", os.getcwd()))

    # Format date components
    year = date.strftime("%Y")
    month_num = date.strftime("%m")
    month_name = calendar.month_name[date.month]
    day = date.strftime("%d")

    # Create directory structure: YYYY/MM-MonthName/MM-DD-YYYY/
    date_dir = f"{month_num}-{day}-{year}"
    dir_path = current_mealplan_root / year / f"{month_num}-{month_name}" / date_dir

    # Create file path: meal_type.md
    return dir_path / f"{meal_type}.md"


def mealplan_directory_path(date: datetime) -> Path:
    """
    Generate the directory path for meal plans on a specific date.

    Args:
        date: The date for the meal plan

    Returns:
        Path: The directory path for meal plans on this date
    """
    # Get the current mealplan root path from environment
    current_mealplan_root = Path(os.environ.get("MEALPLANPATH", os.getcwd()))

    # Format date components
    year = date.strftime("%Y")
    month_num = date.strftime("%m")
    month_name = calendar.month_name[date.month]
    day = date.strftime("%d")

    # Create directory structure: YYYY/MM-MonthName/MM-DD-YYYY/
    date_dir = f"{month_num}-{day}-{year}"
    return current_mealplan_root / year / f"{month_num}-{month_name}" / date_dir


def grocery_path(start_date: str, end_date: str) -> Path:
    """
    Generate the path for a grocery list based on date range.

    The path follows the pattern:
    $MEALPLANPATH/YYYY/MM-MonthName/start_date_to_end_date.md

    If start_date and end_date are the same, the pattern is:
    $MEALPLANPATH/YYYY/MM-MonthName/date.md

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Path: The full path to the grocery list markdown file
    """
    # Get the current mealplan root path from environment
    current_mealplan_root = Path(os.environ.get("MEALPLANPATH", os.getcwd()))

    # Parse start date for directory structure
    start = datetime.strptime(start_date, "%Y-%m-%d")
    year = start.strftime("%Y")
    month_num = start.strftime("%m")
    month_name = calendar.month_name[start.month]

    # Create the filename
    if start_date == end_date:
        # If it's for a single day, just use the date
        filename = f"{start_date}.md"
    else:
        # Otherwise use a date range
        filename = f"{start_date}_to_{end_date}.md"

    # Build the full path
    return current_mealplan_root / year / f"{month_num}-{month_name}" / filename
