# Mealplan MCP – Developer Specification

## Overview
This system extends the Mealplan Model Context Protocol (MCP) server with utilities for managing grocery lists, ignored ingredients, and dish metadata. It is file-based, with predictable behavior and minimal runtime dependencies.

---

## Functional Requirements

### 1. `generate_grocery_list`
- **Inputs**: `start_date`, `end_date` (inclusive), format: `YYYY-MM-DD`
- **Output**: Markdown file grouped by date and dish
- **File path**: `$MEALPLANPATH/YYYY/MM-MonthName/startdate_to_enddate.md`
- **Behavior**:
  - Heading structure:
    - `##` = date
    - `###` = dish name
  - Ingredients listed as checkboxes (`- [ ]`) with quantities + units
  - Ingredient order preserved from dish definition
  - Ingredient names lowercased for display
  - Ignores missing files silently
  - Overwrites existing files without warning
  - Outputs only the relative file path

### 2. `add_ignored_ingredient`
- **Input**: Ingredient name (single string)
- **Behavior**:
  - Input is lowercased, whitespace trimmed
  - Rejects blank or duplicate entries (case-insensitive)
  - Appends to `$MEALPLANPATH/ignored_ingredients.json`
  - Creates file if missing

### 3. `get_ignored_ingredients`
- **Output**: Plain list of lowercase strings from the JSON file

### 4. `store_dish`
- **Input**: JSON object with:
  - `name` (required)
  - `ingredients`, `instructions`, `nutrition` (optional)
- **File Path**: `$MEALPLANPATH/dishes/{slug}.json`
- **Slug Rules**:
  - Based on cleaned, lowercased, ASCII-only name
  - Converted to slug: alphanumeric + dashes only
  - Truncated to 100 characters
  - Appends `-1`, `-2`, etc. if duplicate
- **Cleaning**:
  - Strip invalid fields
  - Normalize whitespace, strip non-printables
  - Lowercase and trim strings
  - Store numbers as strings
  - Reject if fully empty after cleanup
- **Adds**: `created_at` in ISO 8601, local time
- **Output Format**: Pretty-printed JSON (4-space indent, UTF-8, trailing newline)

### 5. `list_dishes`
- **Output**: List of dish JSONs
- **Behavior**:
  - Reads from `dishes/` folder
  - Sorts alphabetically by `name` (case-insensitive)
  - Skips invalid/corrupt files
  - Includes full contents of each valid dish

---

## Architecture Overview

- **Platform**: Local-first, file-based backend
- **Directory Layout**:
  ```
  $MEALPLANPATH/
  ├── YYYY/
  │   └── MM-MonthName/
  │       └── MM-DD-YYYY/
  │           └── meal_type.md
  ├── dishes/
  │   └── {slug}.json
  └── ignored_ingredients.json
  ```

---

## Data Handling

- **Date Handling**: Assumes local system time
- **Encoding**: UTF-8 everywhere
- **Formatting**:
  - Markdown for grocery lists
  - JSON for data records
- **Normalization**:
  - Ingredient and nutrient names are lowercase
  - Whitespace collapsed
  - Non-printable and non-ASCII stripped as needed

---

## Error Handling Strategy

- **Silent Failures**:
  - Missing dish files in grocery list generation
- **Validation Errors**:
  - Reject duplicate ignored ingredients
  - Reject blank or whitespace-only fields
  - Reject malformed or empty dish definitions
- **Corrupt Files**:
  - `list_dishes` skips unreadable or invalid JSON files

---

## Testing Plan

### Unit Tests
- Slug generation (normal, edge, duplicate handling)
- Ingredient addition (trimming, deduplication)
- Dish JSON validation and normalization
- Markdown file generation from valid input ranges

### Integration Tests
- Full end-to-end generation of grocery list using dish files
- Persistence and loading of ignored ingredients
- Store + retrieve dish consistency

### Negative Testing
- Malformed JSONs
- Empty ingredient or instruction fields
- Overlong or non-ASCII dish names
