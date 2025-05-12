"""
Markdown renderer for grocery lists.

This module provides functions for rendering grocery lists in Markdown format.
"""

from datetime import datetime
from typing import Union, Any


def header(date_value: Union[str, datetime, Any]) -> str:
    """
    Generate a Markdown header for a grocery list with the given date.

    Args:
        date_value: A date as string (YYYY-MM-DD), datetime object, or date object

    Returns:
        A Markdown H2 header containing the date in YYYY-MM-DD format
    """
    # Handle string dates
    if isinstance(date_value, str):
        date_str = date_value
    # Handle datetime and date objects
    elif hasattr(date_value, "strftime"):
        date_str = date_value.strftime("%Y-%m-%d")
    # Handle other types (fallback)
    else:
        date_str = str(date_value)

    # Return the formatted header
    return f"## {date_str}"
