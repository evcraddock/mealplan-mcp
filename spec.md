# Meal Plan MCP Server - Developer Specification

## 1. Overview

The Meal Plan MCP Server is a Model Context Protocol (MCP) service implemented in Rust. It provides single-user meal planning capabilities via a set of MCP command handlers that read/write Markdown files with YAML frontmatter. This document covers functional requirements, architecture, data handling, error strategies, and a testing plan.

---

## 2. Functional Requirements

1. **Configuration**
   - Load `config.toml` from working directory or specified path.
   - Mandatory field: `rootFolder: String` (absolute or relative path).
   - On startup, validate that `rootFolder` is writable/accessible.

2. **Directory & File Management**
   - Auto-create directories: `rootFolder/YYYY/MM/MM-DD-YYYY/`.
   - File names: `{mealType}.md` for each meal-type (breakfast, lunch, dinner, snack).
   - Markdown files containing YAML frontmatter & body.

3. **Markdown Format**
   - YAML frontmatter (delimited by `---`):
     - `date`: ISO‑8601 datetime (UTC).
     - `mealType`: one of `breakfast`, `lunch`, `dinner`, `snack` (case‑insensitive).
     - `title`: string.
     - `cook`: string.
   - Body: for each dish:
     ```markdown
     ## Dish Name

     ### Ingredients
     - ingredient (amount)

     ### Instructions
     1. step 1

     ### Nutrients
     | Nutrient            | Amount | Unit |
     |---------------------|-------:|:----:|
     | Total Fat           |   12.5 |  g   |
     | ...                 |    ... | ...  |
     ```

4. **MCP Command Handlers**

   | Command                 | Payload                                                   | Response                                                | Errors                                                                                          |
   |-------------------------|-----------------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------------------------------------------------|
   | `createMealPlan`        | `{ date, mealType, title, cook, dishes: [dish] }`         | `{ success: bool, message: String }`                    | - `BadRequest` (invalid/missing fields)  
                                                                                                                                                - `BadRequest` (`mealType` invalid)  
                                                                                                                                                - `AlreadyExists` (file exists)          |
   | `listMealPlans`         | `{ startDate, endDate, mealTypes?, cook? }`               | `[ { date, mealType, title, cook } ]`                  | - `BadRequest` (invalid dates/types)                                                            |
   | `viewMealPlanMarkdown`  | `{ date, mealType }`                                      | `String` (raw Markdown)                                | - `BadRequest`  
                                                                                                                                                - `NotFound`  
                                                                                                                                                - `ParseError` (YAML malformed)           |
   | `viewMealPlanJSON`      | `{ date, mealType }`                                      | `{ date, mealType, title, cook, dishes: [dish] }`      | same as Markdown                                                                                |
   | `deleteMealPlan`        | `{ date, mealType }`                                      | `{ success: bool, message: String }`                   | - `BadRequest`  
                                                                                                                                                - `NotFound`                                |

5. **Validation Rules**
   - `date`: parseable as ISO‑8601.
   - `mealType`: match allowed list (case-insensitive).
   - `startDate` ≤ `endDate` in `listMealPlans`.
   - Ingredient amounts are non-empty strings.
   - Nutrient values are positive numbers, units non-empty.

---

## 3. Architecture & Implementation Details

- **Language & Framework**: Rust, using `modelcontextprotocol` Rust SDK crate.
- **Module Structure**:
  - `config` module: parse TOML, expose `root_folder: PathBuf`.
  - `storage` module: path helpers, directory creation, file I/O.
  - `parser` module: YAML frontmatter <-> Rust structs, Markdown body parsing (e.g. `yaml-rust`).
  - `handlers` module: MCP command implementations.
  - `errors` module: define MCP error mappings: `BadRequest`, `AlreadyExists`, `NotFound`, `ParseError`.
  - `main.rs`: initialize SDK, register handlers, load config.

- **Dependencies**:
  ```toml
  [dependencies]
  modelcontextprotocol = "^0.1"
  serde = { version = "*", features = ["derive"] }
  toml = "*"
  chrono = { version="*", features=["serde"] }
  yaml-rust = "*"
  anyhow = "*"
  thiserror = "*"
  ```

- **Handler Workflow** (`createMealPlan` example):
  1. Deserialize MCP payload to `CreateMealPlanRequest` struct.
  2. Validate fields (date parse, mealType match).
  3. Compute directory path & file path.
  4. Check existence: if exists, return `AlreadyExists`.
  5. Serialize struct to Markdown with YAML frontmatter.
  6. Ensure directories exist (`std::fs::create_dir_all`).
  7. Write file (`std::fs::write`).
  8. Return `McpResponse { success: true, message }`.

---

## 4. Error Handling Strategy

- **MCP Errors**: Use `Err(McpError::new(code, message))` in handlers.
- **Mapping**:
  - Validation → `BadRequest`
  - File exists → `AlreadyExists`
  - File missing → `NotFound`
  - YAML/body parse → `ParseError`
- **No silent failures**: all error conditions must return explicit MCP errors.

---

## 5. Testing Plan

1. **Unit Tests**
   - **Config parsing**: valid & invalid TOML.
   - **Path helpers**: correct folder/file paths for various dates.
   - **Markdown serialization**: struct → Markdown → parse back yields same struct.
   - **Validation logic**: invalid dates, mealTypes.

2. **Handler Tests** (integration-style using test harness)
   - **createMealPlan**:
     - Success: file created, correct content.
     - Duplicate: returns `AlreadyExists`.
     - Invalid payload: `BadRequest`.
   - **listMealPlans**:
     - Date range and filters.
     - Malformed file present → still lists entries.
   - **viewMealPlanMarkdown/JSON**:
     - Success: correct content.
     - Missing file: `NotFound`.
     - Malformed: `ParseError`.
   - **deleteMealPlan**:
     - Existing file: removed, return success.
     - Non-existing: `NotFound`.

3. **End-to-End Tests**
   - create → list → view → delete → list.

4. **Edge Cases**
   - MealType case variations.
   - Date timezone edge (use UTC).
   - Simulated FS errors (readonly).

5. **CI Integration**
   - `cargo test` on PRs.
   - `cargo fmt` check.
