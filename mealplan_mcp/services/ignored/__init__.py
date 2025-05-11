"""
Services for managing ignored ingredients.

This module provides services for adding and retrieving ingredients
that should be excluded from grocery lists.
"""

from mealplan_mcp.services.ignored.add import add_ingredient

__all__ = ["add_ingredient"]
