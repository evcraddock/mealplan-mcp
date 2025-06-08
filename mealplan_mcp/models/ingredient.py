"""
Ingredient model for the Mealplan MCP server.

This module provides the Ingredient model for representing ingredient data.
"""

from pydantic import BaseModel, field_validator


class Ingredient(BaseModel):
    """
    Model for an ingredient in a dish.

    Attributes:
        name: The name of the ingredient (e.g., flour, sugar, eggs)
        amount: The amount of the ingredient (e.g., "2 cups", "500g", "3 pieces")
    """

    name: str
    amount: str

    @field_validator("name")
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that the name is not empty."""
        if not v.strip():
            return "Unknown Ingredient"
        return v.strip()

    @field_validator("amount")
    def amount_must_not_be_empty(cls, v: str) -> str:
        """Validate that the amount is not empty."""
        if not v.strip():
            return "Unknown Amount"
        return v.strip()
