#!/usr/bin/env python

"""
Test script for calling the MCP meal plan tools.
"""

import asyncio
import json
from mcp.client import Client

async def test_hello():
    """Test the hello tool."""
    client = Client(transport="subprocess", command=["python", "../main.py"])
    result = await client.call("hello", {"message": "Chef"})
    print("Hello Tool Result:")
    print(result)
    print("\n" + "-" * 50 + "\n")

async def test_create_mealplan_from_file():
    """Test the create_mealplan tool using a JSON file."""
    # Load the meal plan from JSON file
    with open("sample_meal_plan.json", "r") as f:
        meal_plan_data = json.load(f)
    
    # Connect to the MCP server
    client = Client(transport="subprocess", command=["python", "../main.py"])
    
    # Call the create_mealplan tool
    result = await client.call("create_mealplan", {"meal_plan": meal_plan_data})
    
    print("Create Meal Plan Tool Result:")
    print(result)

async def main():
    """Run test functions."""
    await test_hello()
    await test_create_mealplan_from_file()

if __name__ == "__main__":
    asyncio.run(main())