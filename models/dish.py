"""
Models for dishes in meal planning.
"""

from typing import TypedDict, List, Optional
from models.ingredient import Ingredient
from models.nutrient import Nutrient


class Dish(TypedDict):
    """
    Model for a dish.

    Attributes:
        name: The name of the dish (e.g., Spaghetti Carbonara, Chocolate Cake)
        ingredients: List of ingredients needed for the dish
        instructions: Step-by-step instructions for preparing the dish
        nutrients: Optional list of nutrients in the dish
    """

    name: str
    ingredients: List[Ingredient]
    instructions: str
    nutrients: Optional[List[Nutrient]]
