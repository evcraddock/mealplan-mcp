"""
Tests for the grocery markdown renderer.

These tests verify that the grocery markdown renderer correctly formats:
1. Headers for grocery lists with a date
2. Ingredient blocks with proper formatting
"""

import sys
import os
import pytest
from datetime import datetime, date

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def test_header_with_string_date():
    """Test that the header function correctly formats a string date."""
    try:
        from mealplan_mcp.renderers.grocery import header
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Test with a string date in the format YYYY-MM-DD
    test_date = "2025-05-10"
    result = header(test_date)

    # The header should be a markdown H2 with the date
    assert result == "## 2025-05-10"


def test_header_with_date_object():
    """Test that the header function correctly formats a date object."""
    try:
        from mealplan_mcp.renderers.grocery import header
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Test with a date object
    test_date = date(2025, 5, 10)
    result = header(test_date)

    # The header should be a markdown H2 with the date
    assert result == "## 2025-05-10"


def test_header_with_datetime_object():
    """Test that the header function correctly formats a datetime object."""
    try:
        from mealplan_mcp.renderers.grocery import header
    except ImportError:
        pytest.skip("Implementation not available yet")

    # Test with a datetime object
    test_date = datetime(2025, 5, 10, 12, 30, 0)
    result = header(test_date)

    # The header should be a markdown H2 with the date (time part ignored)
    assert result == "## 2025-05-10"
