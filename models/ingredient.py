"""
Models for ingredients in meal planning.
"""

from typing import TypedDict


class Ingredient(TypedDict):
    """
    Model for an ingredient.

    Attributes:
        name: The name of the ingredient (e.g., flour, sugar, eggs)
        amount: The amount of the ingredient (e.g., "2 cups", "500g", "3 pieces")
    """

    name: str
    amount: str
