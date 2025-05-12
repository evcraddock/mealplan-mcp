"""
Grocery list generator service.

This module provides the generate_grocery_list service that creates
grocery lists based on meal plans for a given date range.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from mealplan_mcp.utils.paths import grocery_path
from mealplan_mcp.renderers.grocery import header, render_dish_ingredients
from mealplan_mcp.services.dish import list_dishes
from mealplan_mcp.services.ignored import get_ignored_ingredients


def _find_meal_plans_in_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    Find all meal plans within the given date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of meal plan data dictionaries
    """
    # Get the current mealplan root path from environment
    mealplan_root = Path(os.environ.get("MEALPLANPATH", os.getcwd()))

    # Parse dates
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    # Initialize result
    meal_plans = []

    # Find all meal plan files in the date range
    # The structure is MEALPLANPATH/YYYY/MM-MonthName/MM-DD-YYYY/*.md

    # Iterate through all possible days in the range
    current = start
    while current <= end:
        # Format the date components
        year = current.strftime("%Y")
        month_num = current.strftime("%m")
        month_name = current.strftime("%B")
        day = current.strftime("%d")

        # Construct the path for this day
        day_path = (
            mealplan_root
            / year
            / f"{month_num}-{month_name}"
            / f"{month_num}-{day}-{year}"
        )

        # If the directory exists, find all .md files (meal plans)
        if day_path.exists() and day_path.is_dir():
            meal_plan_files = list(day_path.glob("*.md"))

            for meal_plan_file in meal_plan_files:
                # Extract meal type from filename (e.g., "dinner.md" -> "dinner")
                meal_type = meal_plan_file.stem

                # Extract dish name from file content (first H1 heading)
                content = meal_plan_file.read_text()
                dish_name_match = re.search(r"# (.*?)(\n|$)", content)
                dish_name = (
                    dish_name_match.group(1) if dish_name_match else "Unknown Dish"
                )

                # Create a meal plan entry
                meal_plan = {
                    "date": current.strftime("%Y-%m-%d"),
                    "meal_type": meal_type,
                    "dish": dish_name,
                    "file_path": str(meal_plan_file),
                }

                meal_plans.append(meal_plan)

        # Move to next day
        current = datetime(
            current.year,
            current.month,
            current.day + 1,  # Simple way to increment by one day
            current.hour,
            current.minute,
            current.second,
        )

    return meal_plans


def generate_grocery_list(start_date: str, end_date: str) -> str:
    """
    Generate a grocery list for the given date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        The relative path to the generated grocery list file
    """
    # Get the current mealplan root path from environment
    mealplan_root = Path(os.environ.get("MEALPLANPATH", os.getcwd()))

    # Find all meal plans in the date range
    meal_plans = _find_meal_plans_in_range(start_date, end_date)

    # Get all dishes from the database
    dishes = list_dishes()

    # Create a mapping of dish names to dish objects for easy lookup
    dish_map = {dish.name: dish for dish in dishes}

    # Get ignored ingredients
    ignored_ingredients = set(get_ignored_ingredients())

    # Track which dishes we need for the grocery list
    needed_dishes = []
    for meal_plan in meal_plans:
        dish_name = meal_plan["dish"]
        if dish_name in dish_map:
            needed_dishes.append(dish_map[dish_name])

    # Generate the markdown content
    markdown_lines = []

    # Add header with date range
    date_range_header = (
        f"{start_date} to {end_date}" if start_date != end_date else start_date
    )
    markdown_lines.append(header(date_range_header))
    markdown_lines.append("")  # Empty line after header

    # If no meal plans found, add a message
    if not meal_plans:
        markdown_lines.append("No meal plans found for this period.")
        markdown_lines.append("")
    else:
        # Add section for meal plans
        markdown_lines.append("## Meal Plans")

        # Group by date
        current_date = None
        for meal_plan in sorted(
            meal_plans, key=lambda mp: (mp["date"], mp["meal_type"])
        ):
            if meal_plan["date"] != current_date:
                current_date = meal_plan["date"]
                markdown_lines.append(f"### {current_date}")

            markdown_lines.append(f"- {meal_plan['meal_type']}: {meal_plan['dish']}")

        markdown_lines.append("")  # Empty line

    # Add section for ingredients
    markdown_lines.append("## Grocery List")

    # If no dishes found, add a message
    if not needed_dishes:
        markdown_lines.append("No ingredients needed for this period.")
    else:
        # Track all unique ingredients
        all_ingredients = {}  # name -> {amount, dishes}

        # Process each dish
        for dish in needed_dishes:
            if hasattr(dish, "ingredients") and dish.ingredients:
                for ingredient in dish.ingredients:
                    # Get ingredient name and amount
                    if hasattr(ingredient, "name") and hasattr(ingredient, "amount"):
                        name = ingredient.name
                        amount = ingredient.amount
                    elif isinstance(ingredient, dict):
                        name = ingredient.get("name", "")
                        amount = ingredient.get("amount", "")
                    else:
                        continue

                    # Skip empty ingredients
                    if not name:
                        continue

                    # Add to all_ingredients
                    if name not in all_ingredients:
                        all_ingredients[name] = {
                            "amount": [amount],
                            "dishes": [dish.name],
                        }
                    else:
                        all_ingredients[name]["amount"].append(amount)
                        all_ingredients[name]["dishes"].append(dish.name)

        # Sort ingredients alphabetically
        sorted_ingredients = sorted(all_ingredients.items())

        # Add each ingredient to the markdown
        for name, info in sorted_ingredients:
            if name.lower() in ignored_ingredients:
                # Mark ignored ingredients
                markdown_lines.append(f"- [ ] ~~{name}~~ (IGNORED)")
            else:
                # Combine amounts if they're the same
                unique_amounts = set(info["amount"])
                if len(unique_amounts) == 1 and list(unique_amounts)[0]:
                    amount_str = f"({list(unique_amounts)[0]})"
                else:
                    # Otherwise list all amounts
                    amount_str = ", ".join(
                        f"{amount}" for amount in info["amount"] if amount
                    )
                    if amount_str:
                        amount_str = f"({amount_str})"

                # Add the ingredient line
                markdown_lines.append(f"- [ ] {name} {amount_str}".strip())

        markdown_lines.append("")  # Empty line

    # Add section for dishes with their ingredients
    if needed_dishes:
        markdown_lines.append("## Dish Details")

        for dish in needed_dishes:
            # Convert to dict if it's a model object
            if hasattr(dish, "model_dump"):
                dish_dict = dish.model_dump()
            else:
                dish_dict = {"name": dish.name, "ingredients": dish.ingredients}

            # Render the dish ingredients
            dish_block = render_dish_ingredients(dish_dict)
            markdown_lines.append(dish_block)
            markdown_lines.append("")  # Empty line

    # Combine all lines into a single string
    markdown_content = "\n".join(markdown_lines)

    # Get the path for the grocery list
    path = grocery_path(start_date, end_date)

    # Debug info - print the path we're writing to
    print(f"Writing grocery list to: {path}")
    print(f"Path exists: {path.parent.exists()}")

    # Ensure the parent directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write the file
    try:
        path.write_text(markdown_content)
        print(f"Successfully wrote to {path}")
        print(f"File exists after write: {path.exists()}")
    except Exception as e:
        print(f"Error writing to {path}: {e}")

    # Return the relative path from the mealplan root
    try:
        relative_path = str(path.relative_to(mealplan_root))
    except ValueError:
        # Handle the case where the path is not relative to mealplan_root
        print(f"Warning: {path} is not relative to {mealplan_root}")
        relative_path = str(path)

    return relative_path
