"""
Nutrient model for the Mealplan MCP server.

This module provides the Nutrient model for representing nutrient data.
"""

from pydantic import BaseModel, field_validator


class Nutrient(BaseModel):
    """
    Model for a nutrient in a dish.

    Attributes:
        name: The name of the nutrient (e.g., protein, carbohydrates, fat)
        amount: The amount of the nutrient (numeric value)
        unit: The unit of measurement (e.g., g, mg, kcal), defaults to empty string
    """

    name: str
    amount: float
    unit: str = ""

    @field_validator("name")
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that the name is not empty."""
        if not v.strip():
            return "Unknown Nutrient"
        return v.strip()

    @field_validator("amount")
    def amount_must_be_positive(cls, v: float) -> float:
        """Validate that the amount is positive."""
        if v < 0:
            return 0.0
        return v
