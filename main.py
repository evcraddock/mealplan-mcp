import json
from mcp.server import FastMCP
from mealplan_mcp.models.meal_plan import MealPlan

# Import our services for ignored ingredients
from mealplan_mcp.services.ignored import (
    add_ingredient,
    get_ignored_ingredients as get_ignored_ingredients_service,
)

# Import dish services
from mealplan_mcp.services.dish import (
    store_dish as store_dish_service,
    list_dishes as list_dishes_service,
)
from mealplan_mcp.models.dish import Dish

# Import grocery services
from mealplan_mcp.services.grocery import (
    generate_grocery_list as generate_grocery_list_service,
)

# Import meal plan services
from mealplan_mcp.services.mealplan.list_service import (
    list_mealplans_by_date_range as list_mealplans_service,
)
from mealplan_mcp.services.mealplan.pdf_export_service import (
    export_mealplans_to_pdf as export_mealplans_service,
)

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


# Add dish tools
@app.tool()
async def store_dish(dish_data: dict) -> dict:
    """Store a dish and return a confirmation.

    Args:
        dish_data: Dictionary containing dish data

    Returns:
        Dictionary with a confirmation message including the path where the dish was stored
    """
    # Create a Dish object from the data
    dish = Dish(**dish_data)

    # Store the dish
    path = store_dish_service(dish)

    # Return a confirmation message
    return {"ok": str(path)}


@app.tool()
async def list_dishes() -> list:
    """List all dishes.

    Returns:
        List of dish objects converted to dictionaries
    """
    # Get the dishes
    dishes = list_dishes_service()

    # Convert to serializable format
    return [json.loads(dish.model_dump_json()) for dish in dishes]


# Add grocery list tool
@app.tool()
async def generate_grocery_list(date_range: dict) -> dict:
    """Generate a grocery list for a specified date range.

    Args:
        date_range: Dictionary containing start and end dates in format YYYY-MM-DD
            - start: Start date (required)
            - end: End date (required)

    Returns:
        Dictionary with the path to the generated grocery list
    """
    # Extract start and end dates
    start_date = date_range.get("start")
    end_date = date_range.get("end")

    # Validate input
    if not start_date or not end_date:
        return {"error": "Both start and end dates are required"}

    # Call the service to generate the grocery list
    relative_path = generate_grocery_list_service(start_date, end_date)

    # Return success response with the path
    return {"ok": relative_path}


@app.tool()
async def create_mealplan(meal_plan: MealPlan) -> str:
    """Create a meal plan entry with the specified parameters and save it to a file.

    Args:
        meal_plan: A meal plan object containing:
            - date: The date for the meal plan
            - meal_type: The type of meal (breakfast, lunch, dinner, snack)
            - title: The title of the meal
            - cook: The person who will cook the meal
            - dishes: List of dishes to be prepared

    Returns:
        str: A summary of the meal plan and the path where it was saved
    """
    # Store the meal plan using the service layer
    from mealplan_mcp.services.mealplan import store_mealplan
    from mealplan_mcp.renderers.mealplan import render_mealplan_summary

    markdown_path, json_path = store_mealplan(meal_plan)

    # Generate summary for return value
    summary = render_mealplan_summary(meal_plan)

    # Add the file path information
    result = (
        summary
        + f"\n\nMeal plan saved to:\n  Markdown: {markdown_path}\n  JSON: {json_path}"
    )

    return result


@app.tool()
async def list_mealplans_by_date_range(date_range: dict) -> str:
    """List meal plans within a specified date range.

    Args:
        date_range: Dictionary containing start and end dates in format YYYY-MM-DD
            - start: Start date (required)
            - end: End date (required)

    Returns:
        JSON string containing array of meal plan objects with:
        - title: Meal title (cleaned)
        - date: Date in YYYY-MM-DD format
        - meal_type: Type of meal (breakfast, lunch, dinner, snack)
        - cook: Person cooking the meal
        - dishes: Array of dish names
    """
    try:
        # Validate input
        if not date_range:
            return json.dumps(
                {
                    "error": "Missing date_range parameter",
                    "message": "Please provide a date_range object with start and end dates",
                }
            )

        start_date = date_range.get("start")
        end_date = date_range.get("end")

        if not start_date:
            return json.dumps(
                {
                    "error": "Missing start date",
                    "message": "Please provide a start date in YYYY-MM-DD format",
                }
            )

        if not end_date:
            return json.dumps(
                {
                    "error": "Missing end date",
                    "message": "Please provide an end date in YYYY-MM-DD format",
                }
            )

        # Call the service
        result = list_mealplans_service(start_date, end_date)

        # Return as JSON string
        return json.dumps(result, indent=2)

    except ValueError as e:
        return json.dumps(
            {
                "error": "Invalid date format",
                "message": f"Please use YYYY-MM-DD format for dates. Error: {str(e)}",
            }
        )
    except Exception as e:
        return json.dumps(
            {
                "error": "Internal error",
                "message": f"An unexpected error occurred: {str(e)}",
            }
        )


@app.tool()
async def export_mealplans_to_pdf(date_range: dict) -> str:
    """Export meal plans within a specified date range to a PDF file.

    Args:
        date_range: Dictionary containing start and end dates in format YYYY-MM-DD
            - start: Start date (required)
            - end: End date (required)

    Returns:
        JSON string containing either:
        - Success: {"ok": "path/to/generated.pdf"}
        - Error: {"error": "error_type", "message": "error_description"}
    """
    try:
        # Validate input
        if not date_range:
            return json.dumps(
                {
                    "error": "Missing date_range parameter",
                    "message": "Please provide a date_range object with start and end dates",
                }
            )

        start_date = date_range.get("start")
        end_date = date_range.get("end")

        if not start_date:
            return json.dumps(
                {
                    "error": "Missing start date",
                    "message": "Please provide a start date in YYYY-MM-DD format",
                }
            )

        if not end_date:
            return json.dumps(
                {
                    "error": "Missing end date",
                    "message": "Please provide an end date in YYYY-MM-DD format",
                }
            )

        # Call the service to export PDF
        pdf_path = export_mealplans_service(start_date, end_date)

        # Return success response with the path
        return json.dumps({"ok": str(pdf_path)})

    except ValueError as e:
        return json.dumps(
            {
                "error": "Invalid date format",
                "message": f"Please use YYYY-MM-DD format for dates. Error: {str(e)}",
            }
        )
    except Exception as e:
        return json.dumps(
            {
                "error": "Internal error",
                "message": f"An unexpected error occurred: {str(e)}",
            }
        )


if __name__ == "__main__":
    app.run()
