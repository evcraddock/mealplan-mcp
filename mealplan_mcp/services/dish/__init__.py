"""
Services for dish management in the Mealplan MCP server.

This package provides services for storing and retrieving dish data.
"""

from mealplan_mcp.services.dish.store import store_dish
from mealplan_mcp.services.dish.list import list_dishes

__all__ = ["store_dish", "list_dishes"]
