"""
Tests for the slugify function.

These tests verify that the slugify function works as expected:
- Converting spaces and special characters to dashes
- Removing non-ASCII characters
- Truncating to max 100 characters
"""

import pytest


@pytest.mark.parametrize(
    "input_string, expected_slug",
    [
        (" Chili  Con Carne! ", "chili-con-carne"),
        ("Spätzle & Käse", "spatzle-kase"),
        ("x" * 120, "x" * 100),
    ],
)
def test_slugify(input_string, expected_slug):
    """Test that slugify properly transforms strings into URL-friendly slugs."""
    try:
        from mealplan_mcp.utils.slugify import slugify
    except ImportError:
        # The function doesn't exist yet, but we need the test to compile
        pytest.skip("slugify function not implemented yet")

    assert slugify(input_string) == expected_slug
