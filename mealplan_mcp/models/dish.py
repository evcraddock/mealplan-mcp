"""
Dish model for the Mealplan MCP server.

This module provides the Dish model for representing and validating dish data,
including schema validation and slug generation.
"""

from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict, model_validator

from mealplan_mcp.utils.slugify import slugify


class Ingredient(BaseModel):
    """Model for an ingredient in a dish."""

    name: str
    amount: str


class Nutrient(BaseModel):
    """Model for a nutrient in a dish."""

    name: str
    amount: float
    unit: str = ""


class Dish(BaseModel):
    """
    Model for a dish.

    This class handles validation of dish data, name cleaning, and slug generation.
    """

    name: str = "Unnamed Dish"
    ingredients: List[Ingredient] = []
    instructions: str = ""
    nutrients: Optional[List[Nutrient]] = None

    # Internal fields not in JSON
    cleaned_name: Optional[str] = None

    # Configuration using modern Pydantic approach
    model_config = ConfigDict(extra="allow")

    @field_validator("name")
    def name_must_not_be_empty(cls, v: str) -> str:
        """Validate that the name is not empty."""
        if not v.strip():
            return "Unnamed Dish"
        return v

    @model_validator(mode="after")
    def clean_data(self) -> "Dish":
        """
        Clean the dish data after model initialization.

        This method:
        1. Trims whitespace from the name
        2. Truncates names longer than 100 characters
        """
        # Clean the name
        self.cleaned_name = self.name.strip()

        # Truncate long names
        if len(self.cleaned_name) > 100:
            self.cleaned_name = self.cleaned_name[:100]

        # Make sure the cleaned name is not empty
        if not self.cleaned_name:
            self.cleaned_name = "Unnamed Dish"

        return self

    @property
    def slug(self) -> str:
        """
        Generate a URL-friendly slug for the dish.

        Returns:
            A URL-friendly version of the dish name, truncated to 100 characters
        """
        return slugify(self.cleaned_name)
