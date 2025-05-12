"""
Services for grocery list management in the Mealplan MCP server.

This package provides services for generating grocery lists from meal plans.
"""

from mealplan_mcp.services.grocery.generator import generate_grocery_list

__all__ = ["generate_grocery_list"]
