"""
Models for meal planning.
"""
from datetime import datetime
from typing import TypedDict, List
from models.meal_type import MealType
from models.dish import Dish

class MealPlan(TypedDict):
    """
    Model for a meal plan.

    Attributes:
        date: The date for the meal plan
        meal_type: The type of meal (breakfast, lunch, dinner, snack)
        title: The title of the meal
        cook: The person who will cook the meal
        dishes: List of dishes to be prepared
    """
    date: datetime
    meal_type: MealType
    title: str
    cook: str
    dishes: List[Dish]
