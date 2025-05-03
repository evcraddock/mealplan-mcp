"""
Enums for meal planning.
"""
from enum import Enum

class MealType(Enum):
    """
    Enum representing different types of meals.
    
    Values:
        BREAKFAST: Morning meal
        LUNCH: Midday meal
        DINNER: Evening meal
        SNACK: Small meal between main meals
    """
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack" 