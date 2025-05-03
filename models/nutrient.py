"""
Models for nutrients in meal planning.
"""
from typing import TypedDict, Union

class Nutrient(TypedDict):
    """
    Model for a nutrient.
    
    Attributes:
        name: The name of the nutrient (e.g., protein, carbohydrates, fat)
        amount: The amount of the nutrient
        unit: The unit of measurement (e.g., g, mg, kcal)
    """
    name: str
    amount: Union[int, float]
    unit: str 