"""
Tests for the export_mealplans_to_pdf MCP tool.

These tests verify that the FastMCP tool correctly:
1. Accepts proper JSON input format
2. Validates date range parameters
3. Returns path to generated PDF file
4. Handles various error conditions
5. Integrates properly with the PDF export service
"""

import sys
import os
import tempfile
import pytest
import json
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mealplan_mcp.models.meal_plan import MealPlan
from mealplan_mcp.models.meal_type import MealType
from mealplan_mcp.models.dish import Dish
from mealplan_mcp.services.mealplan.store import store_mealplan


def _setup_test_environment(monkeypatch, temp_dir):
    """Set up the test environment with temporary directory."""
    # Mock the mealplan_root in list service
    monkeypatch.setattr(
        "mealplan_mcp.services.mealplan.list_service.mealplan_root", Path(temp_dir)
    )

    # Mock the pdf_export_path function to use temp directory
    def mock_pdf_export_path(start_date, end_date):
        start = datetime.strptime(start_date, "%Y-%m-%d")
        year = start.strftime("%Y")
        month_num = start.strftime("%m")
        month_name = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ][start.month]

        if start_date == end_date:
            filename = f"mealplans_{start_date}.pdf"
        else:
            filename = f"mealplans_{start_date}_to_{end_date}.pdf"

        return Path(temp_dir) / year / f"{month_num}-{month_name}" / filename

    monkeypatch.setattr(
        "mealplan_mcp.services.mealplan.pdf_export_service.pdf_export_path",
        mock_pdf_export_path,
    )

    # Mock mealplan_root for the new get_mealplan_files_with_content function
    monkeypatch.setattr(
        "mealplan_mcp.services.mealplan.pdf_export_service.mealplan_root",
        Path(temp_dir),
    )

    # Mock the path functions for store service
    def mock_mealplan_directory_path(date):
        year = date.strftime("%Y")
        month_num = date.strftime("%m")
        month_name = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ][date.month]
        day = date.strftime("%d")
        return (
            Path(temp_dir)
            / year
            / f"{month_num}-{month_name}"
            / f"{month_num}-{day}-{year}"
        )

    def mock_mealplan_path(date, meal_type):
        date_str = f"{date.strftime('%m')}-{date.strftime('%d')}-{date.strftime('%Y')}"
        return mock_mealplan_directory_path(date) / f"{date_str}-{meal_type}.md"

    monkeypatch.setattr(
        "mealplan_mcp.services.mealplan.store.mealplan_directory_path",
        mock_mealplan_directory_path,
    )
    monkeypatch.setattr(
        "mealplan_mcp.services.mealplan.store.mealplan_path",
        mock_mealplan_path,
    )


class TestExportMealplansToPdfTool:
    """Test cases for the export_mealplans_to_pdf MCP tool."""

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_valid_date_range_returns_pdf_path(self, monkeypatch):
        """Test the tool with a valid date range returns the PDF file path."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create and store a test meal plan
            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.DINNER,
                title="Test PDF Export",
                cook="Test Cook",
                dishes=[Dish(name="Test Dish")],
            )
            store_mealplan(meal_plan)

            # Call the tool
            result = await export_mealplans_to_pdf(
                {"start": "2023-06-10", "end": "2023-06-20"}
            )

            # Parse the result as JSON
            response = json.loads(result)
            assert "ok" in response

            # Verify the returned path exists and is a PDF
            pdf_path = Path(response["ok"])
            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_empty_date_range_still_creates_pdf(self, monkeypatch):
        """Test the tool with no meal plans in range still creates a PDF."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Call the tool with date range that has no meal plans
            result = await export_mealplans_to_pdf(
                {"start": "2023-01-01", "end": "2023-01-07"}
            )

            # Parse the result as JSON
            response = json.loads(result)
            assert "ok" in response

            # Verify PDF was still created (with "no content" message)
            pdf_path = Path(response["ok"])
            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_multiple_meal_plans_creates_consolidated_pdf(
        self, monkeypatch
    ):
        """Test the tool with multiple meal plans creates a consolidated PDF."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create multiple meal plans
            meal_plans = [
                MealPlan(
                    date=datetime(2023, 6, 15),
                    meal_type=MealType.BREAKFAST,
                    title="Morning Meal",
                    cook="Alice",
                    dishes=[Dish(name="Eggs"), Dish(name="Toast")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 16),
                    meal_type=MealType.LUNCH,
                    title="Afternoon Meal",
                    cook="Bob",
                    dishes=[Dish(name="Sandwich")],
                ),
            ]

            for meal_plan in meal_plans:
                store_mealplan(meal_plan)

            # Call the tool
            result = await export_mealplans_to_pdf(
                {"start": "2023-06-15", "end": "2023-06-16"}
            )

            # Parse the result as JSON
            response = json.loads(result)
            assert "ok" in response

            # Verify PDF was created
            pdf_path = Path(response["ok"])
            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"
            # File should be larger for multiple meal plans
            assert pdf_path.stat().st_size > 0

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_missing_date_range_returns_error(self, monkeypatch):
        """Test the tool with missing date_range parameter returns an error."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await export_mealplans_to_pdf({})

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "date_range" in error_response["message"]

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_missing_start_date_returns_error(self, monkeypatch):
        """Test the tool with missing start date returns an error."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await export_mealplans_to_pdf({"end": "2023-06-20"})

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "start date" in error_response["message"]

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_missing_end_date_returns_error(self, monkeypatch):
        """Test the tool with missing end date returns an error."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await export_mealplans_to_pdf({"start": "2023-06-10"})

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "end date" in error_response["message"]

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_invalid_date_format_returns_error(self, monkeypatch):
        """Test the tool with invalid date format returns an error."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await export_mealplans_to_pdf(
                {"start": "invalid-date", "end": "2023-06-20"}
            )

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "date format" in error_response["message"]

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_end_before_start_still_works(self, monkeypatch):
        """Test the tool with end date before start date (should return empty PDF)."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await export_mealplans_to_pdf(
                {"start": "2023-06-20", "end": "2023-06-10"}
            )

            # Should still succeed but return empty PDF
            response = json.loads(result)
            assert "ok" in response

            pdf_path = Path(response["ok"])
            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_with_same_start_and_end_date(self, monkeypatch):
        """Test the tool with same start and end date."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create a meal plan on the target date
            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.LUNCH,
                title="Single Day Meal",
                cook="Chef",
                dishes=[Dish(name="Soup")],
            )
            store_mealplan(meal_plan)

            result = await export_mealplans_to_pdf(
                {"start": "2023-06-15", "end": "2023-06-15"}
            )

            # Parse the result as JSON
            response = json.loads(result)
            assert "ok" in response

            pdf_path = Path(response["ok"])
            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_pdf_filename_contains_date_range(self, monkeypatch):
        """Test that the generated PDF filename contains the date range."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await export_mealplans_to_pdf(
                {"start": "2023-06-01", "end": "2023-06-07"}
            )

            # Parse the result as JSON
            response = json.loads(result)
            assert "ok" in response

            pdf_path = Path(response["ok"])
            filename = pdf_path.name

            # Verify filename includes date range
            assert "2023-06-01" in filename
            assert "2023-06-07" in filename
            assert filename.endswith(".pdf")

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_handles_pdf_generation_errors_gracefully(self, monkeypatch):
        """Test that the tool handles PDF generation errors gracefully."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Mock the PDF export service to raise an exception
            def mock_export_mealplans_to_pdf(start_date, end_date):
                raise Exception("PDF generation failed")

            monkeypatch.setattr(
                "main.export_mealplans_service",
                mock_export_mealplans_to_pdf,
            )

            result = await export_mealplans_to_pdf(
                {"start": "2023-06-01", "end": "2023-06-07"}
            )

            # Parse the error response
            error_response = json.loads(result)
            assert "error" in error_response
            assert "Internal error" in error_response.get("error", "")

    @pytest.mark.anyio
    @pytest.mark.parametrize("anyio_backend", ["asyncio"])
    async def test_tool_response_format_is_consistent(self, monkeypatch):
        """Test that the tool response format is consistent with other tools."""
        from main import export_mealplans_to_pdf

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            result = await export_mealplans_to_pdf(
                {"start": "2023-06-01", "end": "2023-06-07"}
            )

            # Parse the response
            response = json.loads(result)

            # Should follow the same pattern as other tools ({"ok": "path"})
            assert isinstance(response, dict)
            assert "ok" in response
            assert isinstance(response["ok"], str)

            # The path should be a valid path string
            pdf_path = Path(response["ok"])
            assert pdf_path.exists()
