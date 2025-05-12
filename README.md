# Mealplan MCP

A MCP server for meal planning and grocery list generation.

![Coverage](./badges/coverage.svg)

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd mealplan-mcp

# Set up environment variable for meal plan storage
export MEALPLANPATH="/path/to/meal/plans"

# Install dependencies with uv
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run the server
python main.py
```

## Features

- Store and retrieve dish recipes with ingredients and instructions
- Create detailed meal plans for specific dates and meal types
- Manage ignored ingredients that should be excluded from grocery lists
- Generate grocery lists for date ranges with automatic checkboxes
- Full MCP (Model-Centric Programming) compatibility for AI-driven interfaces

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mealplan-mcp
   ```

2. Set up the environment variable for meal plan storage:
   ```bash
   # macOS/Linux
   export MEALPLANPATH="/path/to/meal/plans"

   # Windows Command Prompt
   set MEALPLANPATH=C:\path\to\meal\plans

   # Windows PowerShell
   $env:MEALPLANPATH = "C:\path\to\meal\plans"
   ```

3. Set up the virtual environment:
   ```bash
   # Using uv (recommended)
   uv venv
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\activate    # On Windows

   # Alternative: Using venv (built-in)
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\activate    # On Windows
   ```

4. Install dependencies:
   ```bash
   # Using uv (recommended)
   uv pip install -e ".[dev]"

   # Alternative: Using pip
   pip install -e ".[dev]"
   ```

### Running the Application

To start the MCP server:

```bash
python main.py
```

This starts the server using stdio transport, making it compatible with MCP client applications.

### Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=models --cov=mealplan_mcp

# Generate a coverage report
pytest --cov=models --cov=mealplan_mcp --cov-report=html
```

## MCP Examples

### Using the MCP CLI Tool

The MCP CLI tool allows you to interact with your server directly from the command line:

```bash
# In a separate terminal, run your server
python main.py

# In another terminal, start the MCP CLI
mcp dev main.py
```

### Using Python Client

```python
import asyncio
from mcp.client import Client

async def main():
    # Connect to your MCP server
    client = Client(transport="subprocess", command=["python", "main.py"])

    # Example 1: Store a dish
    dish_data = {
        "name": "Spaghetti Carbonara",
        "ingredients": [
            {"name": "spaghetti", "amount": "200g"},
            {"name": "eggs", "amount": "2"},
            {"name": "pecorino cheese", "amount": "50g"},
            {"name": "pancetta", "amount": "100g"},
            {"name": "black pepper", "amount": "to taste"}
        ],
        "instructions": "1. Cook pasta\n2. Fry pancetta\n3. Mix eggs and cheese\n4. Combine all ingredients"
    }
    result = await client.call("store_dish", {"dish_data": dish_data})
    print(f"Dish stored: {result}")

    # Example 2: Add ignored ingredient
    result = await client.call("add_ignored_ingredient", {"ingredient": "salt"})
    print(f"Ignored ingredient: {result}")

    # Example 3: Generate grocery list
    date_range = {"start": "2023-06-01", "end": "2023-06-07"}
    result = await client.call("generate_grocery_list", {"date_range": date_range})
    print(f"Grocery list: {result}")

    # Close the client
    await client.close()

# Run the async function
asyncio.run(main())
```

## Available Tools

| Tool | Description | Example Input |
|------|-------------|--------------|
| `create_mealplan` | Creates a meal plan | `{"meal_plan": {"date": "2023-05-01", "meal_type": "dinner", "title": "Italian Night", "cook": "Chef", "dishes": [...]}}` |
| `store_dish` | Stores a dish recipe | `{"dish_data": {"name": "Pasta", "ingredients": [...]}}` |
| `list_dishes` | Lists all stored dishes | `{}` |
| `add_ignored_ingredient` | Adds ingredient to ignore list | `{"ingredient": "salt"}` |
| `get_ignored_ingredients` | Gets all ignored ingredients | `{}` |
| `generate_grocery_list` | Creates a grocery list markdown | `{"date_range": {"start": "2023-06-01", "end": "2023-06-07"}}` |

## Project Structure

```
mealplan-mcp/
├── main.py                  # Entry point and MCP server definition
├── models/                  # Core data models
│   ├── dish.py              # Dish model
│   ├── ingredient.py        # Ingredient model
│   ├── meal_plan.py         # Meal plan model
│   ├── meal_type.py         # Meal type enumerations
│   └── nutrient.py          # Nutrient information model
├── mealplan_mcp/            # Main application code
│   ├── models/              # Extended models
│   │   └── ignored.py       # Ignored ingredients model
│   ├── renderers/           # Markdown renderers
│   │   └── grocery.py       # Grocery list markdown renderer
│   ├── services/            # Business logic services
│   │   ├── dish/            # Dish-related services
│   │   ├── grocery/         # Grocery list services
│   │   └── ignored/         # Ignored ingredients services
│   └── utils/               # Utility functions
│       ├── paths.py         # Path handling utilities
│       └── slugify.py       # String slugification
└── tests/                   # Test suite
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
