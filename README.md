# Mealplan MCP

A Model Context Provider (MCP) server for meal planning and grocery list generation.

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
- Full MCP (Model Context Provider) compatibility for AI-driven interfaces

## Available Tools

| Tool | Description | Example Input |
|------|-------------|--------------|
| `create_mealplan` | Creates a meal plan | `{"meal_plan": {"date": "2023-05-01", "meal_type": "dinner", "title": "Italian Night", "cook": "Chef", "dishes": [...]}}` |
| `store_dish` | Stores a dish recipe | `{"dish_data": {"name": "Pasta", "ingredients": [...]}}` |
| `list_dishes` | Lists all stored dishes | `{}` |
| `list_mealplans_by_date_range` | Lists meal plans within a date range | `{"date_range": {"start": "2023-06-01", "end": "2023-06-07"}}` |
| `export_mealplans_to_pdf` | Exports meal plans to a PDF file | `{"date_range": {"start": "2023-06-01", "end": "2023-06-07"}}` |
| `add_ignored_ingredient` | Adds ingredient to ignore list | `{"ingredient": "salt"}` |
| `get_ignored_ingredients` | Gets all ignored ingredients | `{}` |
| `generate_grocery_list` | Creates a grocery list markdown | `{"date_range": {"start": "2023-06-01", "end": "2023-06-07"}}` |

## Claude Desktop Setup

To use this MCP server with Claude Desktop, add the following configuration to your `claude_desktop_config.json` file:

### macOS
```bash
# Edit the config file
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Windows
```bash
# Navigate to the config file location
%APPDATA%\Claude\claude_desktop_config.json
```

### Configuration

Add this server configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mealplan": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/mealplan-mcp",
        "run",
        "main.py"
      ],
      "env": {
        "MEALPLANPATH": "/path/to/your/meal/plans"
      }
    }
  }
}
```

**Important**:
- Replace `/path/to/your/mealplan-mcp/main.py` with the actual path to your `main.py` file
- Replace `/path/to/your/meal/plans` with your desired meal plan storage directory
- Restart Claude Desktop after making changes

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

The project includes comprehensive testing with automatic test isolation:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mealplan_mcp

# Generate a coverage report
pytest --cov=mealplan_mcp --cov-report=html

# Run specific test categories
pytest tests/mealplan/          # Meal plan tests
pytest tests/dish/              # Dish service tests
pytest tests/renderers/         # Renderer tests
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


## Project Structure

```
mealplan-mcp/
├── main.py                  # Entry point and MCP server definition
├── mealplan_mcp/            # Main application package
│   ├── models/              # Pydantic data models
│   │   ├── dish.py          # Dish model with ingredients and instructions
│   │   ├── ingredient.py    # Ingredient model with validation
│   │   ├── ignored.py       # Ignored ingredients model
│   │   ├── meal_plan.py     # Meal plan model with date validation
│   │   ├── meal_type.py     # Meal type enumerations
│   │   └── nutrient.py      # Nutrient information model
│   ├── renderers/           # Markdown rendering modules
│   │   ├── grocery.py       # Grocery list markdown renderer
│   │   └── mealplan.py      # Meal plan markdown renderer
│   ├── services/            # Business logic services
│   │   ├── dish/            # Dish-related services (store, list)
│   │   ├── grocery/         # Grocery list generation services
│   │   ├── ignored/         # Ignored ingredients services
│   │   └── mealplan/        # Meal plan storage services
│   └── utils/               # Utility functions
│       ├── paths.py         # Path handling with test isolation
│       └── slugify.py       # String slugification utilities
├── tests/                   # Comprehensive test suite (113 tests)
└── docs/                    # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
