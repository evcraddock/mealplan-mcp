# Mealplan MCP – Brainstorm results

## Overview

This document expands the existing Mealplan MCP (Model Context Protocol) Server with additional tools and functionality, defined through an iterative Q\&A process.

---

## Tools

### 1. `generate_grocery_list`

* **Input**: Start date and end date (inclusive) in `YYYY-MM-DD` format
* **Behavior**:

  * Generates a Markdown grocery list grouped by date and dish
  * Includes checkboxes (`- [ ]`) and quantities with units
  * Ingredients are listed per dish, not aggregated
  * Omits meal type, includes dish name as Markdown subheading (`###`), date as heading (`##`)
  * Preserves ingredient order from dish definitions
  * Ingredient names lowercased, but keep original casing in meal plan files
  * Ignores missing files silently
  * Output includes only a confirmation with the relative file path
* **Output File**: `$MEALPLANPATH/YYYY/MM-MonthName/startdate_to_enddate.md`
* **File Behavior**: Overwrites existing file if present

### 2. `add_ignored_ingredient`

* **Input**: Single string ingredient name
* **Behavior**:

  * Converts input to lowercase and trims whitespace
  * Ignores blank or whitespace-only input
  * Rejects duplicates (case-insensitive check against `$MEALPLANPATH/ignored_ingredients.json`)
  * Appends to file, which is auto-created if missing

### 3. `get_ignored_ingredients`

* **Behavior**:

  * Returns a list of ignored ingredients as a plain list of lowercase strings

### 4. `store_dish`

* **Input**: Full dish definition in JSON
* **Fields Accepted**: `name`, `ingredients`, `instructions`, `nutrition`
* **Behavior**:

  * Dish name is required and cleaned:

    * Trimmed of whitespace and punctuation
    * Lowercased, non-ASCII characters stripped
    * Converted to a slug (alphanumeric + dashes only, multiple dashes collapsed, leading/trailing dashes removed)
    * Slug used as filename `$MEALPLANPATH/dishes/{slug}.json`
    * Filename limit: 100 characters (slug only)
    * If slug already exists, append `-1`, `-2`, etc.
  * Adds `created_at` field in ISO 8601 format with system local time
  * Strips extra fields not defined in schema
  * Cleans fields:

    * Lowercase and trim ingredient and nutrition names/units
    * Strip non-printable characters, collapse multiple whitespace
    * Remove empty or unnamed ingredients/nutrients
    * Store numeric fields as strings, including fractions or text
    * Reject whitespace-only instructions
    * Reject fully empty dishes (after cleanup)
  * Pretty-printed JSON, 4-space indent, system line endings, UTF-8 encoded, with trailing newline

### 5. `list_dishes`

* **Behavior**:

  * Returns all dish JSON files under `dishes/`
  * Alphabetically sorted by internal `name` field (case-insensitive natural order)
  * Includes full contents of each file, excluding invalid/corrupt ones

---

## File Structure

```
$MEALPLANPATH/
├── YYYY/
│   └── MM-MonthName/
│       └── MM-DD-YYYY/
│           └── meal_type.md
├── dishes/
│   └── {slug}.json
├── ignored_ingredients.json
└── YYYY/MM-MonthName/{start}_to_{end}.md
```

---

## General Behavior

* All file paths are relative to `$MEALPLANPATH`
* Tools return minimal plain string success messages (e.g., "Saved to dishes/chili.json")
* Error responses are structured with keys like `error`, `message`, and `hint`, LLM-friendly
* No auth, logging, or filtering support
* All JSON read/write operations are synchronous and local
* Markdown files omit metadata or comments
* No support for symbolic links or cross-platform filename sanitation

---

This document finalizes the expanded architecture and behavior for the Mealplan MCP toolset. It’s ready for implementation as specified.
