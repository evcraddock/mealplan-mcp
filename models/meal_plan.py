"""
Models for meal planning.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict, model_validator

from models.meal_type import MealType
from models.dish import Dish
from mealplan_mcp.utils.slugify import slugify


class MealPlan(BaseModel):
    """
    Model for a meal plan.

    This class handles validation of meal plan data, name cleaning, and slug generation.
    """

    date: datetime
    meal_type: MealType
    title: str = "Untitled Meal"
    cook: str = "Unknown"
    dishes: List[Dish] = []

    # Internal fields not in JSON
    cleaned_title: Optional[str] = None

    # Configuration using modern Pydantic approach
    model_config = ConfigDict(extra="allow")

    @field_validator("title")
    def title_must_not_be_empty(cls, v: str) -> str:
        """Validate that the title is not empty."""
        if not v.strip():
            return "Untitled Meal"
        return v

    @field_validator("cook")
    def cook_must_not_be_empty(cls, v: str) -> str:
        """Validate that the cook is not empty."""
        if not v.strip():
            return "Unknown"
        return v

    @field_validator("date", mode="before")
    def parse_date(cls, v):
        """Parse date from various formats."""
        if isinstance(v, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                try:
                    # Try standard format
                    return datetime.strptime(v, "%Y-%m-%d")
                except ValueError:
                    # Default to now if parsing fails
                    return datetime.now()
        elif isinstance(v, datetime):
            return v
        else:
            return datetime.now()

    @model_validator(mode="after")
    def clean_data(self) -> "MealPlan":
        """
        Clean the meal plan data after model initialization.

        This method:
        1. Trims whitespace from the title
        2. Truncates titles longer than 100 characters
        """
        # Clean the title
        self.cleaned_title = self.title.strip()

        # Truncate long titles
        if len(self.cleaned_title) > 100:
            self.cleaned_title = self.cleaned_title[:100]

        # Make sure the cleaned title is not empty
        if not self.cleaned_title:
            self.cleaned_title = "Untitled Meal"

        return self

    @property
    def slug(self) -> str:
        """
        Generate a URL-friendly slug for the meal plan.

        Returns:
            A URL-friendly version of the meal plan title and date
        """
        date_str = self.date.strftime("%Y-%m-%d")
        meal_type_str = self.meal_type.value
        title_slug = slugify(self.cleaned_title)
        return f"{date_str}-{meal_type_str}-{title_slug}"
