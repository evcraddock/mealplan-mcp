# Mealplan MCP

A Model-Centric Programming (MCP) server for meal planning.

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

2. Set up the virtual environment:
   ```bash
   # Option 1: Using venv (built-in)
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\activate    # On Windows

   # Option 2: Using uv
   uv venv
   source .venv/bin/activate  # On macOS/Linux
   # .venv\Scripts\activate    # On Windows
   ```

3. Install dependencies:
   ```bash
   # Using pip
   pip install -e .

   # Using uv
   uv pip install -e .
   ```

### Running the Application

To start the MCP server:

```bash
python main.py
```

This starts the server using stdio transport, making it compatible with MCP client applications.

### Testing the MCP Server Locally

There are several ways to test your MCP server:

#### 1. Using the MCP CLI Tool

The MCP CLI tool allows you to interact with your server directly from the command line:

```bash
# In a separate terminal, run your server
python main.py

```bash
mcp dev main.py
```

#### 2. In a Python Script

You can also test your MCP server from a Python script:

```python
from mcp.client import Client

# Connect to your MCP server
client = Client(transport="subprocess", command=["python", "main.py"])

# Call the hello tool
result = await client.call("hello", {"message": "World"})
print(result)

# Call the create_mealplan tool
meal_plan_data = {
    "date": "2023-05-01",
    "meal_type": "dinner",
    "title": "Test Meal",
    "cook": "Chef",
    "dishes": [{
        "name": "Test Dish",
        "ingredients": [{"name": "Ingredient", "amount": "1 cup"}],
        "instructions": "Mix and serve"
    }]
}
result = await client.call("create_mealplan", {"meal_plan": meal_plan_data})
print(result)
```

#### 3. Using HTTP Transport

For testing with HTTP transport:

```bash
# Start the server with HTTP transport
python -c "from mcp.server import FastMCP; app = FastMCP('mealplan', transport='http'); app.include_router_from_module('main'); app.run()"

# Test using curl
curl -X POST "http://localhost:8000/tools/hello" \
  -H "Content-Type: application/json" \
  -d '{"message": "World"}'
```

## Project Structure

- `main.py` - Entry point and MCP server definition
- `models/` - Data models for the meal planning system
  - `dish.py` - Dish model
  - `ingredient.py` - Ingredient model
  - `meal_plan.py` - Meal plan model
  - `meal_type.py` - Meal type enumerations
  - `nutrient.py` - Nutrient information model

## Available Tools

- `hello` - Simple test tool that returns a greeting message
- `create_mealplan` - Creates a meal plan with dishes, ingredients, and instructions
