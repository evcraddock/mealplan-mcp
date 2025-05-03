from mcp.server import FastMCP
# Import removed as Dish class is not used in this file
from models.meal_plan import MealPlan
# MealType imported for type checking
# from models.meal_type import MealType

app = FastMCP("mealplan", transport="stdio")

@app.tool()
async def hello(message: str) -> str:
    """A simple tool that returns a hello world message.

    Args:
        message: The message to return

    Returns:
        str: A greeting message
    """
    return f"Hello {message} from the mealplan MCP server!"

@app.tool()
async def create_mealplan(meal_plan: MealPlan) -> str:
    """Create a meal plan entry with the specified parameters.

    Args:
        meal_plan: An object containing meal plan details
            - date: The date for the meal plan
            - meal_type: The type of meal (breakfast, lunch, dinner, snack)
            - title: The title of the meal
            - cook: The person who will cook the meal
            - dishes: List of dishes to be prepared

    Returns:
        str: A string containing the meal plan details
    """
    try:
        # Access required fields with proper error handling
        title = meal_plan.get('title', 'Untitled')

        # Handle meal_type safely - ensure it's a valid enum
        meal_type = meal_plan.get('meal_type')
        meal_type_str = meal_type.value if hasattr(meal_type, 'value') else str(meal_type)

        # Handle date formatting safely
        date_obj = meal_plan.get('date')
        date_str = date_obj.strftime('%Y-%m-%d') if hasattr(date_obj, 'strftime') else str(date_obj)

        cook = meal_plan.get('cook', 'Unknown')

        result = f"Meal Plan: {title} ({meal_type_str}) on {date_str} cooked by {cook}"

        # Get dishes safely
        dishes = meal_plan.get('dishes', [])
        result += f"\n\nDishes ({len(dishes)}):"

        for i, dish in enumerate(dishes, 1):
            # Get dish name safely
            dish_name = dish.get('name', f'Dish {i}')
            result += f"\n\n{i}. {dish_name}"

            # Add ingredients safely
            result += "\n   Ingredients:"
            ingredients = dish.get('ingredients', [])
            if not ingredients:
                result += "\n   - None specified"
            else:
                for ingredient in ingredients:
                    ing_name = ingredient.get('name', 'Unknown')
                    ing_amount = ingredient.get('amount', 'Amount not specified')
                    result += f"\n   - {ing_name}: {ing_amount}"

            # Add instructions safely
            instructions = dish.get('instructions', 'No instructions provided')
            result += f"\n\n   Instructions:\n   {instructions.replace('\n', '\n   ')}"

            # Add nutrients if available
            nutrients = dish.get('nutrients', [])
            if nutrients:
                result += "\n\n   Nutrients:"
                for nutrient in nutrients:
                    nut_name = nutrient.get('name', 'Unknown')
                    nut_amount = nutrient.get('amount', 0)
                    nut_unit = nutrient.get('unit', '')
                    result += f"\n   - {nut_name}: {nut_amount} {nut_unit}"

        return result
    except Exception as e:
        # Log the error and return a friendly message
        print(f"Error creating meal plan: {e}")
        return f"Error creating meal plan: {str(e)}"

if __name__ == "__main__":
    app.run()
