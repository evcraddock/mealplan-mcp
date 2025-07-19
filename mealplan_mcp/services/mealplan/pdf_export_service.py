"""
PDF export service for meal plans.

This service takes a date range, retrieves meal plans, and generates a consolidated PDF
document containing all meal plan details with proper formatting.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import re
import markdown
from html.parser import HTMLParser
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

from mealplan_mcp.utils.paths import pdf_export_path, mealplan_root


def get_mealplan_files_with_content(
    start_date: str, end_date: str
) -> List[Dict[str, Any]]:
    """
    Get meal plan files with their full markdown content within a date range.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        List of dictionaries with meal plan metadata and full markdown content
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Expected YYYY-MM-DD: {e}")

    if end_dt < start_dt:
        return []

    meal_plans = []
    current_mealplan_root = Path(mealplan_root)

    if not current_mealplan_root.exists():
        return []

    # Walk through the directory structure
    for year_dir in current_mealplan_root.iterdir():
        if not year_dir.is_dir() or not year_dir.name.isdigit():
            continue

        for month_dir in year_dir.iterdir():
            if not month_dir.is_dir():
                continue

            for date_dir in month_dir.iterdir():
                if not date_dir.is_dir():
                    continue

                # Extract date from directory name (MM-DD-YYYY)
                date_match = re.match(r"(\d{2})-(\d{2})-(\d{4})", date_dir.name)
                if not date_match:
                    continue

                month, day, year = date_match.groups()
                try:
                    file_date = datetime(int(year), int(month), int(day))
                except ValueError:
                    continue

                # Check if date is within our range
                if start_dt <= file_date <= end_dt:
                    # Find all .md files in this directory
                    for md_file in date_dir.glob("*.md"):
                        # Extract meal type from filename
                        filename_match = re.match(
                            r"\d{2}-\d{2}-\d{4}-(.+)\.md$", md_file.name
                        )
                        if filename_match:
                            meal_type = filename_match.group(1)

                            # Load the full markdown content
                            markdown_content = _load_meal_plan_markdown(md_file)

                            # Extract title from markdown content (first heading or filename)
                            title = _extract_title_from_markdown(
                                markdown_content, md_file.stem
                            )

                            meal_plans.append(
                                {
                                    "title": title,
                                    "date": file_date.strftime("%Y-%m-%d"),
                                    "meal_type": meal_type,
                                    "markdown_content": markdown_content,
                                    "file_path": str(md_file),
                                }
                            )

    # Define meal type order: breakfast -> lunch -> dinner -> snack
    meal_type_order = {"breakfast": 0, "lunch": 1, "dinner": 2, "snack": 3}

    # Sort by date, then by meal type order (not alphabetically), then by title
    meal_plans.sort(
        key=lambda x: (
            x["date"],
            meal_type_order.get(x["meal_type"], 99),  # Default to 99 for unknown types
            x["title"],
        )
    )
    return meal_plans


def _extract_title_from_markdown(content: str, fallback: str) -> str:
    """
    Extract title from markdown content, falling back to filename.

    Args:
        content: Markdown content
        fallback: Fallback title if none found

    Returns:
        Extracted or fallback title
    """
    if not content.strip():
        return fallback

    # Look for first heading (# Title)
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
            if title:
                return title

    # Look for front matter title
    if content.startswith("---"):
        front_matter_end = content.find("---", 3)
        if front_matter_end > 0:
            front_matter = content[3:front_matter_end]
            for line in front_matter.split("\n"):
                if line.strip().startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip("\"'")
                    if title:
                        return title

    return fallback


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

    # Get meal plans with full markdown content for the date range
    meal_plans = get_mealplan_files_with_content(start_date, end_date)

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
                    meta_text = (
                        f"<b>Date:</b> {formatted_date} | <b>Meal:</b> {meal_type}"
                    )
                    story.append(Paragraph(meta_text, meal_meta_style))

                    # Add the full markdown content
                    if meal.get("markdown_content"):
                        story.append(Spacer(1, 0.2 * inch))
                        # Convert markdown to HTML and then to PDF paragraphs
                        _add_markdown_content_to_story(
                            meal["markdown_content"], story, styles
                        )

                    story.append(Spacer(1, 0.5 * inch))

        # Build the PDF
        doc.build(story)

    except Exception as e:
        raise Exception(f"Failed to generate PDF: {e}")


def _add_markdown_content_to_story(
    markdown_content: str, story: list, styles: Any
) -> None:
    """
    Convert markdown content to PDF elements using proper markdown rendering.

    Args:
        markdown_content: Raw markdown content
        story: ReportLab story list to append to
        styles: ReportLab styles dictionary
    """
    if not markdown_content.strip():
        return

    # Remove YAML front matter if present
    content = markdown_content
    if content.startswith("---"):
        end_frontmatter = content.find("---", 3)
        if end_frontmatter > 0:
            content = content[end_frontmatter + 3 :].lstrip("\n")

    # Convert markdown to HTML
    html_content = markdown.markdown(content, extensions=["nl2br"])

    # Parse HTML and convert to PDF elements
    parser = HTMLToPDFParser(story, styles)
    parser.feed(html_content)
    parser.close()


class HTMLToPDFParser(HTMLParser):
    """Convert HTML to ReportLab PDF elements."""

    def __init__(self, story, styles):
        super().__init__()
        self.story = story
        self.styles = styles
        self.current_text = ""
        self.current_tags = []
        self.list_level = 0
        self.in_list = False

        # Define custom styles for additional heading levels
        self.h4_style = ParagraphStyle(
            "Heading4",
            parent=styles["Heading3"],
            fontSize=12,
            spaceAfter=8,
            fontName="Helvetica-Bold",
        )

        self.h5_style = ParagraphStyle(
            "Heading5",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        )

    def handle_starttag(self, tag, attrs):
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self._flush_text()
            self.current_tags.append(tag)
        elif tag in ["p", "div"]:
            self._flush_text()
            self.current_tags.append(tag)
        elif tag == "strong" or tag == "b":
            self.current_text += "<b>"
            self.current_tags.append("b")
        elif tag == "em" or tag == "i":
            self.current_text += "<i>"
            self.current_tags.append("i")
        elif tag == "code":
            self.current_text += '<font face="Courier">'
            self.current_tags.append("code")
        elif tag == "ul" or tag == "ol":
            self._flush_text()
            self.in_list = True
            self.list_level += 1
        elif tag == "li":
            self._flush_text()
            self.current_text = "• "
            self.current_tags.append("li")
        elif tag == "blockquote":
            self._flush_text()
            self.current_tags.append("blockquote")
        elif tag == "hr":
            self._flush_text()
            self.story.append(Spacer(1, 12))
        elif tag == "br":
            self.current_text += "<br/>"

    def handle_endtag(self, tag):
        if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            self._flush_text(tag)
            if tag in self.current_tags:
                self.current_tags.remove(tag)
        elif tag in ["p", "div"]:
            self._flush_text()
            if tag in self.current_tags:
                self.current_tags.remove(tag)
        elif tag == "strong" or tag == "b":
            self.current_text += "</b>"
            if "b" in self.current_tags:
                self.current_tags.remove("b")
        elif tag == "em" or tag == "i":
            self.current_text += "</i>"
            if "i" in self.current_tags:
                self.current_tags.remove("i")
        elif tag == "code":
            self.current_text += "</font>"
            if "code" in self.current_tags:
                self.current_tags.remove("code")
        elif tag == "ul" or tag == "ol":
            self._flush_text()
            self.in_list = False
            self.list_level = max(0, self.list_level - 1)
        elif tag == "li":
            self._flush_text()
            if "li" in self.current_tags:
                self.current_tags.remove("li")
        elif tag == "blockquote":
            self._flush_text("blockquote")
            if "blockquote" in self.current_tags:
                self.current_tags.remove("blockquote")

    def handle_data(self, data):
        self.current_text += data

    def _flush_text(self, element_type=None):
        if not self.current_text.strip():
            return

        text = self.current_text.strip()

        if element_type in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # Map heading levels to styles
            if element_type == "h1":
                style = self.styles["Heading1"]
            elif element_type == "h2":
                style = self.styles["Heading2"]
            elif element_type == "h3":
                style = self.styles["Heading3"]
            elif element_type == "h4":
                style = self.h4_style
            else:  # h5, h6
                style = self.h5_style
            self.story.append(Paragraph(text, style))
        elif element_type == "blockquote":
            blockquote_style = ParagraphStyle(
                "Blockquote",
                parent=self.styles["Normal"],
                leftIndent=20,
                rightIndent=20,
                fontName="Helvetica-Oblique",
                fontSize=10,
                textColor=colors.grey,
            )
            self.story.append(Paragraph(text, blockquote_style))
        elif "li" in self.current_tags:
            # List item
            self.story.append(Paragraph(text, self.styles["Normal"]))
        else:
            # Regular paragraph
            if text:
                self.story.append(Paragraph(text, self.styles["Normal"]))

        self.current_text = ""

    def close(self):
        self._flush_text()
        super().close()


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
