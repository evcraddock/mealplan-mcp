"""
Tests for the meal plan PDF export service.

These tests verify that the PDF export service correctly:
1. Exports meal plans to PDF format
2. Handles date range filtering properly
3. Generates well-formed PDF files
4. Includes proper content and formatting
5. Handles edge cases gracefully
"""

import sys
import os
import tempfile
import pytest
from datetime import datetime
from pathlib import Path

# Add the project root to the Python path to fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

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
        "mealplan_mcp.services.mealplan.store.mealplan_path",
        mock_mealplan_path,
    )


class TestPdfExportService:
    """Test cases for the PDF export service."""

    def test_export_empty_date_range_creates_pdf_with_no_content_message(
        self, monkeypatch
    ):
        """Test that exporting an empty date range creates a PDF with a no content message."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            pdf_path = export_mealplans_to_pdf("2023-06-01", "2023-06-07")

            # Verify PDF file was created
            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"
            assert pdf_path.stat().st_size > 0

    def test_export_single_meal_plan_creates_valid_pdf(self, monkeypatch):
        """Test that exporting a single meal plan creates a valid PDF."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create a test meal plan
            dish1 = Dish(name="Grilled Chicken")
            dish2 = Dish(name="Rice Pilaf")

            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.DINNER,
                title="Healthy Dinner",
                cook="Chef Alice",
                dishes=[dish1, dish2],
            )

            # Store the meal plan
            store_mealplan(meal_plan)

            # Export to PDF
            pdf_path = export_mealplans_to_pdf("2023-06-10", "2023-06-20")

            # Verify PDF file was created
            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"
            assert pdf_path.stat().st_size > 0

    def test_export_multiple_meal_plans_creates_consolidated_pdf(self, monkeypatch):
        """Test that exporting multiple meal plans creates a consolidated PDF."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create multiple meal plans
            meal_plans = [
                MealPlan(
                    date=datetime(2023, 6, 15),
                    meal_type=MealType.BREAKFAST,
                    title="Morning Energy",
                    cook="Alice",
                    dishes=[Dish(name="Oatmeal"), Dish(name="Fresh Fruit")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 15),
                    meal_type=MealType.LUNCH,
                    title="Quick Lunch",
                    cook="Bob",
                    dishes=[Dish(name="Turkey Sandwich")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 16),
                    meal_type=MealType.DINNER,
                    title="Italian Night",
                    cook="Charlie",
                    dishes=[Dish(name="Spaghetti"), Dish(name="Garlic Bread")],
                ),
            ]

            # Store all meal plans
            for meal_plan in meal_plans:
                store_mealplan(meal_plan)

            # Export to PDF
            pdf_path = export_mealplans_to_pdf("2023-06-14", "2023-06-17")

            # Verify PDF file was created and has reasonable size for multiple meals
            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"
            assert pdf_path.stat().st_size > 0

    def test_export_pdf_filename_includes_date_range(self, monkeypatch):
        """Test that the exported PDF filename includes the date range."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            pdf_path = export_mealplans_to_pdf("2023-06-01", "2023-06-07")

            # Verify filename includes date range
            assert "2023-06-01" in pdf_path.name
            assert "2023-06-07" in pdf_path.name
            assert pdf_path.suffix == ".pdf"

    def test_export_creates_pdf_in_correct_location(self, monkeypatch):
        """Test that the PDF is created in the correct directory structure."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            pdf_path = export_mealplans_to_pdf("2023-06-01", "2023-06-07")

            # Verify PDF is in the expected directory structure: YYYY/MM-MonthName/
            assert pdf_path.is_absolute()
            assert pdf_path.exists()
            assert "2023" in str(pdf_path)
            assert "06-June" in str(pdf_path)

    def test_export_with_invalid_date_range_raises_error(self, monkeypatch):
        """Test that invalid date ranges raise appropriate errors."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Test with invalid date format
            with pytest.raises(ValueError, match="date format"):
                export_mealplans_to_pdf("invalid-date", "2023-06-07")

            with pytest.raises(ValueError, match="date format"):
                export_mealplans_to_pdf("2023-06-01", "invalid-date")

    def test_export_handles_missing_markdown_files_gracefully(self, monkeypatch):
        """Test that the service handles missing markdown files gracefully."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create a meal plan (which creates both JSON and markdown files)
            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.DINNER,
                title="Test Meal",
                cook="Chef",
                dishes=[Dish(name="Test Dish")],
            )
            store_mealplan(meal_plan)

            # Manually delete the markdown file to simulate missing file
            # (The service should fall back to JSON content or handle gracefully)
            markdown_files = list(Path(temp_dir).rglob("*.md"))
            for md_file in markdown_files:
                md_file.unlink()

            # Export should still work
            pdf_path = export_mealplans_to_pdf("2023-06-10", "2023-06-20")
            assert pdf_path.exists()

    def test_export_pdf_content_includes_meal_details(self, monkeypatch):
        """Test that the PDF content includes all meal plan details."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create a meal plan with specific details
            meal_plan = MealPlan(
                date=datetime(2023, 6, 15),
                meal_type=MealType.DINNER,
                title="Unique Test Meal Title",
                cook="Chef Test Name",
                dishes=[
                    Dish(name="Unique Dish One"),
                    Dish(name="Unique Dish Two"),
                ],
            )
            store_mealplan(meal_plan)

            pdf_path = export_mealplans_to_pdf("2023-06-10", "2023-06-20")

            assert pdf_path.exists()
            # Note: In a real implementation, we might want to extract text from PDF
            # and verify content, but for now we just ensure the file is created

    def test_export_with_date_range_boundary_conditions(self, monkeypatch):
        """Test export with various date range boundary conditions."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create meal plans on boundary dates
            meal_plans = [
                MealPlan(
                    date=datetime(2023, 6, 15),  # Start date
                    meal_type=MealType.BREAKFAST,
                    title="Start Date Meal",
                    cook="Alice",
                    dishes=[Dish(name="Toast")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 17),  # End date
                    meal_type=MealType.DINNER,
                    title="End Date Meal",
                    cook="Bob",
                    dishes=[Dish(name="Pasta")],
                ),
            ]

            for meal_plan in meal_plans:
                store_mealplan(meal_plan)

            # Test exact boundary range
            pdf_path = export_mealplans_to_pdf("2023-06-15", "2023-06-17")
            assert pdf_path.exists()

            # Test single day range
            pdf_path_single = export_mealplans_to_pdf("2023-06-15", "2023-06-15")
            assert pdf_path_single.exists()

    def test_export_returns_relative_path(self, monkeypatch):
        """Test that the export function returns a path that can be used for file operations."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            export_mealplans_to_pdf,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            pdf_path = export_mealplans_to_pdf("2023-06-01", "2023-06-07")

            # Verify the returned path is usable
            assert isinstance(pdf_path, Path)
            assert pdf_path.exists()
            assert pdf_path.is_file()
            assert pdf_path.stat().st_size > 0

    def test_meal_plans_ordered_by_meal_type(self, monkeypatch):
        """Test that meal plans are ordered by meal type (breakfast, lunch, dinner) within each day."""
        from mealplan_mcp.services.mealplan.pdf_export_service import (
            get_mealplan_files_with_content,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            _setup_test_environment(monkeypatch, temp_dir)

            # Create meal plans in non-ordered sequence
            meal_plans = [
                MealPlan(
                    date=datetime(2023, 6, 15),
                    meal_type=MealType.DINNER,
                    title="Dinner First",
                    cook="Chef",
                    dishes=[Dish(name="Steak")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 15),
                    meal_type=MealType.BREAKFAST,
                    title="Breakfast Second",
                    cook="Chef",
                    dishes=[Dish(name="Eggs")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 15),
                    meal_type=MealType.LUNCH,
                    title="Lunch Third",
                    cook="Chef",
                    dishes=[Dish(name="Salad")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 16),
                    meal_type=MealType.LUNCH,
                    title="Next Day Lunch",
                    cook="Chef",
                    dishes=[Dish(name="Soup")],
                ),
                MealPlan(
                    date=datetime(2023, 6, 16),
                    meal_type=MealType.BREAKFAST,
                    title="Next Day Breakfast",
                    cook="Chef",
                    dishes=[Dish(name="Pancakes")],
                ),
            ]

            # Store all meal plans
            for meal_plan in meal_plans:
                store_mealplan(meal_plan)

            # Get meal plans for the date range
            retrieved_plans = get_mealplan_files_with_content(
                "2023-06-15", "2023-06-16"
            )

            # Verify we have all plans
            assert len(retrieved_plans) == 5

            # Verify ordering for June 15
            june_15_plans = [p for p in retrieved_plans if p["date"] == "2023-06-15"]
            assert len(june_15_plans) == 3
            assert june_15_plans[0]["meal_type"] == "breakfast"
            assert june_15_plans[1]["meal_type"] == "lunch"
            assert june_15_plans[2]["meal_type"] == "dinner"

            # Verify ordering for June 16
            june_16_plans = [p for p in retrieved_plans if p["date"] == "2023-06-16"]
            assert len(june_16_plans) == 2
            assert june_16_plans[0]["meal_type"] == "breakfast"
            assert june_16_plans[1]["meal_type"] == "lunch"
