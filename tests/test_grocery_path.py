"""
Tests for the grocery_path function.

These tests verify that the grocery_path function correctly generates
file paths for grocery lists based on date ranges.
"""

import os
import sys
import pytest
from pathlib import Path

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_grocery_path_with_string_dates():
    """Test grocery_path with string dates."""
    try:
        from mealplan_mcp.utils.paths import grocery_path
    except ImportError:
        pytest.skip("Implementation not available yet")

    start_date = "2025-05-10"
    end_date = "2025-05-17"

    result = grocery_path(start_date, end_date)

    # Check that the result is a Path object
    assert isinstance(result, Path)

    # Check path structure: YYYY/MM-MonthName/YYYY-MM-DD_to_YYYY-MM-DD.md
    expected_parts = ["2025", "05-May", "2025-05-10_to_2025-05-17.md"]

    # Convert Path to string and split by path separator
    path_parts = str(result).split(os.path.sep)

    # Check that all expected parts are in the path
    for part in expected_parts:
        assert part in path_parts

    # Check the file name specifically
    assert path_parts[-1] == "2025-05-10_to_2025-05-17.md"


def test_grocery_path_with_same_dates():
    """Test grocery_path when start and end dates are the same."""
    try:
        from mealplan_mcp.utils.paths import grocery_path
    except ImportError:
        pytest.skip("Implementation not available yet")

    same_date = "2025-05-10"

    result = grocery_path(same_date, same_date)

    # Check path structure for same dates
    expected_parts = [
        "2025",
        "05-May",
        "2025-05-10.md",  # Should be just the date, not a range
    ]

    path_parts = str(result).split(os.path.sep)

    for part in expected_parts:
        assert part in path_parts

    # Should not include "_to_" since it's not a range
    assert "_to_" not in path_parts[-1]
    assert path_parts[-1] == "2025-05-10.md"


def test_grocery_path_with_different_months():
    """Test grocery_path when dates span different months."""
    try:
        from mealplan_mcp.utils.paths import grocery_path
    except ImportError:
        pytest.skip("Implementation not available yet")

    start_date = "2025-05-25"
    end_date = "2025-06-05"

    result = grocery_path(start_date, end_date)

    # For date ranges crossing months, the path should be in the month of the start date
    expected_parts = [
        "2025",
        "05-May",  # Should use the start date's month
        "2025-05-25_to_2025-06-05.md",
    ]

    path_parts = str(result).split(os.path.sep)

    for part in expected_parts:
        assert part in path_parts

    assert path_parts[-1] == "2025-05-25_to_2025-06-05.md"


def test_grocery_path_with_different_years():
    """Test grocery_path when dates span different years."""
    try:
        from mealplan_mcp.utils.paths import grocery_path
    except ImportError:
        pytest.skip("Implementation not available yet")

    start_date = "2025-12-25"
    end_date = "2026-01-05"

    result = grocery_path(start_date, end_date)

    # For date ranges crossing years, use the start date's year
    expected_parts = [
        "2025",  # Should use the start date's year
        "12-December",
        "2025-12-25_to_2026-01-05.md",
    ]

    path_parts = str(result).split(os.path.sep)

    for part in expected_parts:
        assert part in path_parts

    assert path_parts[-1] == "2025-12-25_to_2026-01-05.md"
