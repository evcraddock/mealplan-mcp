# Mealplan MCP - Architecture Document

## Overview

Mealplan MCP is a Model-Centric Programming (MCP) server designed for meal planning. It provides a standardized interface for creating and managing meal plans with detailed information about dishes, ingredients, and nutritional content. The application uses the MCP architecture to expose its functionality as tools that can be consumed by various clients.

## System Architecture

### MCP Server

The application implements a FastMCP server that exposes meal planning functionality through defined tools. The server can run with different transport mechanisms:
- **stdio**: Default transport used for CLI interaction
- **HTTP**: Optional transport for web-based clients

### Data Models

The application uses a well-structured data model with TypedDict classes:

1. **MealPlan**
   - Core entity containing date, meal type, title, cook, and a list of dishes
   - Represents a complete meal plan for a specific date and meal type

2. **MealType**
   - Enum representing different types of meals (breakfast, lunch, dinner, snack)

3. **Dish**
   - Represents a food dish with name, ingredients list, preparation instructions, and optional nutritional information

4. **Ingredient**
   - Represents a food ingredient with name and amount

5. **Nutrient**
   - Represents nutritional information with name, amount, and unit of measurement

### File Storage

The application stores meal plans as Markdown files in a structured directory hierarchy:
```
$MEALPLANPATH/
├── YYYY/
│   └── MM-MonthName/
│       └── MM-DD-YYYY/
│           └── meal_type.md
```

Where:
- `$MEALPLANPATH`: Environment variable specifying the root directory (defaults to current working directory)
- `YYYY`: Year folder
- `MM-MonthName`: Month folder (e.g., "05-May")
- `MM-DD-YYYY`: Date folder (e.g., "05-15-2023")
- `meal_type.md`: Markdown file named after the meal type (e.g., "breakfast.md", "dinner.md")

### Exposed Tools

The application exposes the following MCP tools:

1. **hello**
   - Simple test tool that returns a greeting message
   - Used for verifying that the MCP server is running correctly

2. **create_mealplan**
   - Creates a meal plan with dishes, ingredients, and instructions
   - Accepts a MealPlan object containing all necessary data
   - Generates a structured Markdown file and saves it to the appropriate directory
   - Returns a formatted summary of the created meal plan

## Workflow

1. **Client Connection**
   - Clients connect to the MCP server using various transport mechanisms
   - For CLI: subprocess transport with direct invocation of `main.py`
   - For web: HTTP transport with FastAPI

2. **Tool Invocation**
   - Clients call MCP tools with appropriate parameters
   - For example, calling `create_mealplan` with a meal plan data structure

3. **Data Processing**
   - The server processes the received data
   - Validates and transforms the input data as needed
   - For meal plans, this includes date formatting, directory creation, and markdown generation

4. **File Storage**
   - For `create_mealplan`, the resulting data is saved as a markdown file
   - The file includes a task item, meal details, dishes, ingredients, instructions, and nutritional information
   - Files are organized in a hierarchical directory structure by date

5. **Response Generation**
   - The server generates a formatted response
   - For `create_mealplan`, this includes a summary of the created meal plan and file path information

## Technical Implementation

- **Language**: Python 3.12+
- **Dependencies**:
  - mcp[cli]: Core MCP framework
  - httpx: For HTTP client functionality
- **Development Tools**:
  - uv: Recommended for dependency management

## Testing

The application can be tested through multiple approaches:

1. **Direct MCP CLI Tool**
   - Using the `mcp dev` command to interact with the server

2. **Python Testing Script**
   - Using the MCP client library to call tools programmatically
   - Example script available in `hack/test_meal_plans.py`

3. **HTTP Transport Testing**
   - Using curl or other HTTP clients to interact with the server when running in HTTP mode