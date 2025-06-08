"""
PDF export service for meal plans.

This service takes a date range, retrieves meal plans, and generates a consolidated PDF
document containing all meal plan details with proper formatting.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

from mealplan_mcp.services.mealplan.list_service import list_mealplans_by_date_range
from mealplan_mcp.utils.paths import pdf_export_path


def export_mealplans_to_pdf(start_date: str, end_date: str) -> Path:
    """
    Export meal plans within a date range to a PDF file.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        Path: Path to the generated PDF file

    Raises:
        ValueError: If date format is invalid
    """
    # Validate date format
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Please use YYYY-MM-DD format: {e}")

    # Get meal plans for the date range
    meal_plans = list_mealplans_by_date_range(start_date, end_date)

    # Generate PDF path using the same directory structure as meal plans
    pdf_path = pdf_export_path(start_date, end_date)

    # Ensure directory exists
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate PDF
    _generate_pdf_with_reportlab(meal_plans, start_date, end_date, pdf_path)

    return pdf_path


def _generate_pdf_with_reportlab(
    meal_plans: List[Dict[str, Any]], start_date: str, end_date: str, output_path: Path
) -> None:
    """
    Generate PDF using ReportLab.

    Args:
        meal_plans: List of meal plan dictionaries
        start_date: Start date for the range
        end_date: End date for the range
        output_path: Path where PDF should be saved
    """
    try:
        # Create the PDF document
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []

        # Get styles
        styles = getSampleStyleSheet()

        # Create custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#007acc"),
            alignment=1,  # Center alignment
            spaceAfter=20,
        )

        subtitle_style = ParagraphStyle(
            "CustomSubtitle",
            parent=styles["Normal"],
            fontSize=14,
            textColor=colors.grey,
            alignment=1,  # Center alignment
            spaceAfter=30,
        )

        meal_title_style = ParagraphStyle(
            "MealTitle",
            parent=styles["Heading2"],
            fontSize=16,
            textColor=colors.HexColor("#007acc"),
            spaceAfter=10,
        )

        meal_meta_style = ParagraphStyle(
            "MealMeta",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=15,
        )

        # Add title and date range
        story.append(Paragraph("Meal Plans Export", title_style))
        story.append(Paragraph(f"{start_date} to {end_date}", subtitle_style))

        # Add content based on whether we have meal plans
        if not meal_plans:
            no_content_style = ParagraphStyle(
                "NoContent",
                parent=styles["Normal"],
                fontSize=14,
                textColor=colors.grey,
                alignment=1,  # Center alignment
                spaceAfter=20,
            )
            story.append(Spacer(1, 2 * inch))
            story.append(Paragraph("No meal plans found", meal_title_style))
            story.append(
                Paragraph(
                    "No meal plans were found for the specified date range.",
                    no_content_style,
                )
            )
        else:
            # Group meal plans by date
            meals_by_date = {}
            for meal in meal_plans:
                date = meal["date"]
                if date not in meals_by_date:
                    meals_by_date[date] = []
                meals_by_date[date].append(meal)

            # Add each meal plan
            for i, (date, date_meals) in enumerate(meals_by_date.items()):
                if i > 0:
                    story.append(PageBreak())

                for meal in date_meals:
                    # Format date nicely
                    try:
                        date_obj = datetime.strptime(meal["date"], "%Y-%m-%d")
                        formatted_date = date_obj.strftime("%A, %B %d, %Y")
                    except ValueError:
                        formatted_date = meal["date"]

                    # Add meal title
                    story.append(Paragraph(meal["title"], meal_title_style))

                    # Add meal metadata
                    meal_type = meal["meal_type"].title()
                    meta_text = f"<b>Date:</b> {formatted_date} | <b>Meal:</b> {meal_type} | <b>Cook:</b> {meal['cook']}"
                    story.append(Paragraph(meta_text, meal_meta_style))

                    # Add dishes
                    if meal["dishes"]:
                        story.append(Paragraph("<b>Dishes:</b>", styles["Heading3"]))
                        for dish in meal["dishes"]:
                            dish_text = f"• {dish}"
                            story.append(Paragraph(dish_text, styles["Normal"]))
                        story.append(Spacer(1, 0.3 * inch))

                    story.append(Spacer(1, 0.5 * inch))

        # Build the PDF
        doc.build(story)

    except Exception as e:
        raise Exception(f"Failed to generate PDF: {e}")


def _load_meal_plan_markdown(meal_plan_path: Path) -> str:
    """
    Load the full markdown content of a meal plan file.

    Args:
        meal_plan_path: Path to the meal plan markdown file

    Returns:
        str: Markdown content of the meal plan
    """
    try:
        with open(meal_plan_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception as e:
        raise Exception(f"Failed to load meal plan markdown from {meal_plan_path}: {e}")
