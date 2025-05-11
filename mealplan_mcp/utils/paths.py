"""
Path utilities for the Mealplan MCP server.

This module provides consistent path handling for various file types
used by the application, including dishes and grocery lists.
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


def grocery_path(start_date: str, end_date: str) -> Path:
    """
    Generate the path for a grocery list based on date range.

    The path follows the pattern:
    $MEALPLANPATH/YYYY/MM-MonthName/start_date_to_end_date.md

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Path: The full path to the grocery list markdown file
    """
    # Parse start date for directory structure
    start = datetime.strptime(start_date, "%Y-%m-%d")
    year = start.strftime("%Y")
    month_num = start.strftime("%m")
    month_name = calendar.month_name[start.month]

    # Create the filename
    filename = f"{start_date}_to_{end_date}.md"

    # Build the full path
    return mealplan_root / year / f"{month_num}-{month_name}" / filename
