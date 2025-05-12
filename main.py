import os
import calendar
from datetime import datetime
from mcp.server import FastMCP
from models.meal_plan import MealPlan

# Import our services for ignored ingredients
from mealplan_mcp.services.ignored import (
    add_ingredient,
    get_ignored_ingredients as get_ignored_ingredients_service,
)

# Get the meal plan path from environment variable, default to current directory if not set
MEALPLAN_PATH = os.environ.get("MEALPLANPATH", os.getcwd())

app = FastMCP("mealplan", transport="stdio")


# Add ignored ingredients tools
@app.tool()
async def add_ignored_ingredient(ingredient: str) -> dict:
    """Add an ingredient to the ignored ingredients list.

    Args:
        ingredient: The name of the ingredient to ignore

    Returns:
        A dictionary with a confirmation message
    """
    # Call the service to add the ingredient
    add_ingredient(ingredient)

    # Return success response
    return {"ok": "Saved"}


@app.tool()
def get_ignored_ingredients() -> list:
    """Get the list of ignored ingredients.

    Returns:
        A sorted list of ingredient names to be ignored in grocery lists
    """
    # Call the service to get the ingredients
    return get_ignored_ingredients_service()


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
    """Create a meal plan entry with the specified parameters and save it to a file.

    Args:
        meal_plan: An object containing meal plan details
            - date: The date for the meal plan
            - meal_type: The type of meal (breakfast, lunch, dinner, snack)
            - title: The title of the meal
            - cook: The person who will cook the meal
            - dishes: List of dishes to be prepared

    Returns:
        str: A string containing the meal plan details and the path where it was saved
    """
    try:
        # Access required fields with proper error handling
        title = meal_plan.get("title", "Untitled")

        # Handle meal_type safely - ensure it's a valid enum
        meal_type = meal_plan.get("meal_type")
        meal_type_str = (
            meal_type.value if hasattr(meal_type, "value") else str(meal_type)
        )

        # Handle date formatting safely
        date_obj = meal_plan.get("date")
        if not date_obj:
            date_obj = datetime.now()

        # Format the date for display
        if hasattr(date_obj, "strftime"):
            year = date_obj.strftime("%Y")
            month_num = date_obj.strftime("%m")
            month_name = calendar.month_name[date_obj.month]
            day = date_obj.strftime("%d")
            date_str = date_obj.strftime("%Y-%m-%d")
        else:
            # Fallback if date is not a datetime object
            date_str = str(date_obj)
            # Try to extract year and month from the string date
            try:
                # Assuming format like "2023-06-15T18:30:00Z"
                parts = date_str.split("T")[0].split("-")
                year = parts[0]
                month_num = parts[1]
                month_name = calendar.month_name[int(month_num)]
                day = parts[2]
            except (IndexError, ValueError):
                # Default values if parsing fails
                now = datetime.now()
                year = now.strftime("%Y")
                month_num = now.strftime("%m")
                month_name = calendar.month_name[now.month]
                day = now.strftime("%d")

        # Create directory structure: $MEALPLANPATH/YYYY/MM-MonthName/MM-DD-YYYY/
        date_dir = f"{month_num}-{day}-{year}"
        dir_path = os.path.join(
            MEALPLAN_PATH, year, f"{month_num}-{month_name}", date_dir
        )
        os.makedirs(dir_path, exist_ok=True)

        # Create file path: $MEALPLANPATH/YYYY/MM-MonthName/MM-DD-YYYY/meal_type.md
        file_name = f"{meal_type_str}.md"
        file_path = os.path.join(dir_path, file_name)

        cook = meal_plan.get("cook", "Unknown")

        # Create markdown task at the top
        task = f"- [ ] {title} ({meal_type_str},{cook}) #mealplan [scheduled:: {year}-{month_num}-{day}]\n\n"

        # Create content in Markdown format
        content = task
        content += f"# {title}\n\n"
        content += f"**Date:** {date_str}  \n"
        content += f"**Meal Type:** {meal_type_str}  \n"
        content += f"**Cook:** {cook}  \n\n"

        # Add dishes information
        dishes = meal_plan.get("dishes", [])
        content += f"## Dishes ({len(dishes)})\n\n"

        for i, dish in enumerate(dishes, 1):
            # Get dish name safely
            dish_name = dish.get("name", f"Dish {i}")
            content += f"### {i}. {dish_name}\n\n"

            # Add ingredients safely
            content += "#### Ingredients\n\n"
            ingredients = dish.get("ingredients", [])
            if not ingredients:
                content += "- None specified\n\n"
            else:
                for ingredient in ingredients:
                    ing_name = ingredient.get("name", "Unknown")
                    ing_amount = ingredient.get("amount", "Amount not specified")
                    content += f"- {ing_name}: {ing_amount}\n"
                content += "\n"

            # Add instructions safely
            instructions = dish.get("instructions", "No instructions provided")
            content += "#### Instructions\n\n"
            content += instructions.replace("\n", "\n\n")
            content += "\n\n"

            # Add nutrients if available
            nutrients = dish.get("nutrients", [])
            if nutrients:
                content += "#### Nutrients\n\n"
                for nutrient in nutrients:
                    nut_name = nutrient.get("name", "Unknown")
                    nut_amount = nutrient.get("amount", 0)
                    nut_unit = nutrient.get("unit", "")
                    content += f"- {nut_name}: {nut_amount} {nut_unit}\n"
                content += "\n"

        # Write the content to the file
        with open(file_path, "w") as f:
            f.write(content)

        # Generate console output
        result = f"Markdown Task: - [ ] {title} ({meal_type_str},{cook}) #mealplan [scheduled:: {year}-{month_num}-{day}]"
        result += (
            f"\n\nMeal Plan: {title} ({meal_type_str}) on {date_str} cooked by {cook}"
        )
        result += f"\n\nDishes ({len(dishes)}):"

        for i, dish in enumerate(dishes, 1):
            dish_name = dish.get("name", f"Dish {i}")
            result += f"\n\n{i}. {dish_name}"

            # Add ingredients
            result += "\n   Ingredients:"
            ingredients = dish.get("ingredients", [])
            if not ingredients:
                result += "\n   - None specified"
            else:
                for ingredient in ingredients:
                    ing_name = ingredient.get("name", "Unknown")
                    ing_amount = ingredient.get("amount", "Amount not specified")
                    result += f"\n   - {ing_name}: {ing_amount}"

            # Add instructions
            instructions = dish.get("instructions", "No instructions provided")
            result += f"\n\n   Instructions:\n   {instructions.replace('\n', '\n   ')}"

            # Add nutrients if available
            nutrients = dish.get("nutrients", [])
            if nutrients:
                result += "\n\n   Nutrients:"
                for nutrient in nutrients:
                    nut_name = nutrient.get("name", "Unknown")
                    nut_amount = nutrient.get("amount", 0)
                    nut_unit = nutrient.get("unit", "")
                    result += f"\n   - {nut_name}: {nut_amount} {nut_unit}"

        # Add the file path information
        result += f"\n\nMeal plan saved to: {file_path}"

        return result
    except Exception as e:
        # Log the error and return a friendly message
        print(f"Error creating meal plan: {e}")
        return f"Error creating meal plan: {str(e)}"


if __name__ == "__main__":
    app.run()
