# Meal Plan MCP Server Implementation Prompts

These prompts are designed to guide a code-generation LLM through implementing a Meal Plan MCP server in Rust, following test-driven development and incremental implementation principles.

## Prompt 1: Project Setup and Initial Structure

```
I'm building a Meal Plan MCP (Model Context Protocol) server in Rust. Let's start with the basic project setup.

Please:
1. Generate a `Cargo.toml` file with the necessary dependencies:
   - modelcontextprotocol = "^0.1"
   - serde with derive features
   - toml
   - chrono with serde feature
   - yaml-rust
   - anyhow
   - thiserror

2. Create a basic module structure with the following files (just empty module declarations for now):
   - src/main.rs (with module declarations)
   - src/config.rs
   - src/storage.rs
   - src/parser.rs
   - src/handlers.rs
   - src/errors.rs
   - src/models.rs

3. Implement a minimal `main.rs` that just prints "Starting Meal Plan MCP Server" and imports all the modules.

Make sure everything compiles with `cargo build`.
```

## Prompt 2: Configuration Module

```
Now, let's implement the configuration module for our Meal Plan MCP server. This module should:

1. Define a `Config` struct with a `root_folder` field (as PathBuf).

2. Implement a function to load configuration from a TOML file:
   - Load from `config.toml` in the working directory or a specified path.
   - Parse the TOML into the Config struct.
   - Validate that `root_folder` exists and is writable/accessible.
   - Return a Result with the Config or an appropriate error.

3. Write unit tests for:
   - Successful config parsing from valid TOML
   - Error handling for invalid TOML
   - Error handling for non-existent root folder
   - Error handling for non-writable root folder

Use test-driven development: write the tests first, then implement the functionality.

Here's a sample config.toml format:
```toml
root_folder = "/path/to/meal/plans"
```

## Prompt 3: Core Data Models

```
Let's implement the data models module for our Meal Plan MCP server. Based on the specification, we need to define structs that model:

1. A `MealPlan` with these fields:
   - `date`: DateTime<Utc> (using chrono)
   - `meal_type`: enum MealType (breakfast, lunch, dinner, snack - case insensitive)
   - `title`: String
   - `cook`: String
   - `dishes`: Vec<Dish>

2. A `Dish` with these fields:
   - `name`: String
   - `ingredients`: Vec<Ingredient>
   - `instructions`: Vec<String>
   - `nutrients`: Vec<Nutrient>

3. An `Ingredient` with:
   - `name`: String
   - `amount`: String

4. A `Nutrient` with:
   - `name`: String
   - `amount`: f64
   - `unit`: String

5. Request and response structs for all MCP commands:
   - `CreateMealPlanRequest` and `CreateMealPlanResponse`
   - `ListMealPlansRequest` and `ListMealPlansResponse`
   - `ViewMealPlanMarkdownRequest` and a String response
   - `ViewMealPlanJsonRequest` and a JSON response
   - `DeleteMealPlanRequest` and `DeleteMealPlanResponse`

6. Implement validation methods for these models, particularly:
   - Validate meal_type against allowed values
   - Validate date format
   - Validate that start_date ≤ end_date in list requests
   - Validate that nutrient amounts are positive
   - Validate that ingredient amounts are non-empty

7. Write unit tests for the validation methods.

Use Serde derive macros for serialization/deserialization.
```

## Prompt 4: Path and Directory Helpers

```
Now let's implement the storage module with path and directory helpers for our Meal Plan MCP server. This module should:

1. Implement a function to compute the directory path for a meal plan:
   - Format: `rootFolder/YYYY/MM/MM-DD-YYYY/`
   - Takes a DateTime<Utc> and the root folder path
   - Returns a PathBuf

2. Implement a function to compute the file path for a meal plan:
   - Format: `rootFolder/YYYY/MM/MM-DD-YYYY/{mealType}.md`
   - Takes a DateTime<Utc>, meal type, and the root folder path
   - Returns a PathBuf

3. Implement a function to ensure all required directories exist:
   - Creates any missing directories in the path
   - Returns Result with success or an error

4. Write unit tests for:
   - Correct directory path generation for various dates
   - Correct file path generation for various dates and meal types
   - Directory creation functionality

Remember to use the Config structure we defined earlier to get the root folder. Handle potential file system errors appropriately.

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 5: Basic File Operations

```
Let's continue building the storage module by implementing file operations for our Meal Plan MCP server. This module should:

1. Implement a function to write a meal plan to a file:
   - Takes a MealPlan struct and root folder path
   - Computes the correct file path using our path helpers
   - Ensures directories exist using our directory helper
   - Writes the content to the file
   - Returns Result with success or an error

2. Implement a function to read a meal plan from a file:
   - Takes a date, meal type, and root folder path
   - Computes the correct file path
   - Reads the file content
   - Returns Result with the file content as a String or an error

3. Implement a function to check if a meal plan file exists:
   - Takes a date, meal type, and root folder path
   - Computes the correct file path
   - Returns a boolean indicating existence

4. Implement a function to delete a meal plan file:
   - Takes a date, meal type, and root folder path
   - Computes the correct file path
   - Deletes the file if it exists
   - Returns Result with success or an error

5. Write unit tests for all these functions:
   - Test successful write and read operations
   - Test handling of non-existent files for read
   - Test file existence checking
   - Test file deletion

Don't worry about parsing the file content yet - we'll handle that in the parser module. For now, just focus on the raw file operations.

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 6: YAML Frontmatter Parsing

```
Now let's implement the parser module for handling YAML frontmatter in our Meal Plan MCP server. This module should:

1. Implement a function to extract YAML frontmatter from Markdown:
   - Takes a String containing Markdown with YAML frontmatter (delimited by `---`)
   - Returns a tuple of (String, String) containing (frontmatter, body)
   - Handle error cases (missing delimiters, etc.)

2. Implement a function to parse YAML frontmatter into a MealPlan struct:
   - Takes a String containing YAML
   - Uses the yaml-rust crate to parse it
   - Converts the YAML to a MealPlan struct (just the header fields, not dishes yet)
   - Returns Result with the MealPlan or an error

3. Implement a function to generate YAML frontmatter from a MealPlan:
   - Takes a MealPlan struct
   - Generates YAML frontmatter for the header fields
   - Returns a String

4. Implement a function to combine YAML frontmatter and Markdown body:
   - Takes YAML frontmatter string and Markdown body string
   - Combines them with proper delimiters
   - Returns the complete Markdown string

5. Write unit tests for all these functions:
   - Test extraction of frontmatter from valid Markdown
   - Test handling of malformed Markdown
   - Test parsing valid YAML into MealPlan
   - Test generating YAML from MealPlan
   - Test combining frontmatter and body

This module should focus solely on handling the YAML frontmatter, not the Markdown body structure (dishes, ingredients, etc.) - we'll handle that separately.

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 7: Markdown Generation and Parsing

```
Let's continue with the parser module by implementing Markdown body parsing and generation for our Meal Plan MCP server. This module should extend our previous YAML frontmatter handling with:

1. Implement a function to generate Markdown body from dishes:
   - Takes a Vec<Dish>
   - Generates Markdown with proper sections for each dish
   - Format as per specification with:
     * `## Dish Name` for dish headers
     * `### Ingredients` section with bullet points
     * `### Instructions` section with numbered steps
     * `### Nutrients` section with a table
   - Returns a String with the formatted Markdown

2. Implement a function to parse dishes from Markdown body:
   - Takes a String containing the Markdown body
   - Parses it to extract dishes, ingredients, instructions, and nutrients
   - Returns Result with Vec<Dish> or an error

3. Implement a complete function to serialize a MealPlan to Markdown:
   - Takes a MealPlan struct
   - Generates YAML frontmatter
   - Generates Markdown body for dishes
   - Combines them
   - Returns the complete Markdown string

4. Implement a complete function to deserialize Markdown to a MealPlan:
   - Takes a String containing Markdown with YAML frontmatter
   - Extracts and parses the frontmatter
   - Extracts and parses the body
   - Combines into a complete MealPlan
   - Returns Result with the MealPlan or an error

5. Write unit tests for all these functions:
   - Test generating Markdown from dishes
   - Test parsing dishes from valid Markdown
   - Test handling malformed Markdown
   - Test complete serialization/deserialization
   - Test round-trip conversion (MealPlan → Markdown → MealPlan)

Focus on robust parsing that can handle slight variations in format while still maintaining the core structure.

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 8: Error Handling Framework

```
Let's implement the error handling framework for our Meal Plan MCP server. This module should:

1. Define a custom error enum using thiserror:
   - Include variants for all error types we'll need:
     * ConfigError (invalid config, path issues)
     * StorageError (file I/O, directory creation)
     * ParseError (YAML parsing, Markdown parsing)
     * ValidationError (invalid dates, meal types, etc.)
     * NotFoundError (file not found)
     * AlreadyExistsError (file already exists)
     * GeneralError (catch-all for other issues)

2. Implement conversions from library errors to our custom errors:
   - std::io::Error → StorageError
   - yaml_rust::ScanError → ParseError
   - chrono::ParseError → ValidationError
   - etc.

3. Implement a function to convert our custom errors to MCP errors:
   - Map ValidationError → McpError::BadRequest
   - Map NotFoundError → McpError::NotFound
   - Map AlreadyExistsError → McpError::AlreadyExists
   - Map ParseError → McpError::ParseError
   - Map others to appropriate MCP error types

4. Write unit tests for:
   - Error conversions from library errors
   - Conversion to MCP errors
   - Error messages and formatting

This error framework will be used throughout all modules to ensure consistent error handling and user-friendly error messages.

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 9: Create Meal Plan Handler

```
Now let's implement our first MCP command handler: the createMealPlan handler. This handler should:

1. Define a function that takes a CreateMealPlanRequest and returns an MCP response:
   - Input: JSON payload with date, mealType, title, cook, and dishes
   - Output: McpResponse with success flag and message (or an error)

2. Implement the handler workflow:
   - Deserialize request payload to CreateMealPlanRequest struct
   - Validate all fields (date parsing, meal type validation)
   - Compute directory and file paths
   - Check if file already exists - return AlreadyExists error if it does
   - Convert the request to a MealPlan struct
   - Serialize the MealPlan to Markdown with YAML frontmatter
   - Ensure directories exist
   - Write the file
   - Return success response or appropriate error

3. Write integration tests for:
   - Successful creation of a meal plan
   - Handling duplicate creation attempts
   - Validation of request fields
   - Error cases (invalid meal type, etc.)

This handler should use our previously implemented modules for:
- Path computation (storage module)
- Directory creation (storage module)
- File writing (storage module)
- YAML/Markdown generation (parser module)
- Error handling (errors module)

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 10: List Meal Plans Handler

```
Let's implement the listMealPlans handler for our Meal Plan MCP server. This handler should:

1. Define a function that takes a ListMealPlansRequest and returns an MCP response:
   - Input: JSON payload with startDate, endDate, optional mealTypes, and optional cook
   - Output: Array of MealPlan summary objects (date, mealType, title, cook)

2. Implement the handler workflow:
   - Deserialize request payload to ListMealPlansRequest struct
   - Validate fields (date parsing, start ≤ end)
   - Compute date range and generate list of paths to check
   - Scan directories for matching files
   - For each file:
     * Extract and parse YAML frontmatter (ignore body)
     * Apply filters (mealTypes, cook)
     * Add matching plans to result list
   - Return list of meal plan summaries

3. Implement logic to scan directories efficiently:
   - Generate paths for each day in the date range
   - Check if directories exist before scanning
   - Handle potential file system errors gracefully

4. Write integration tests for:
   - Listing meal plans in a date range
   - Filtering by meal type
   - Filtering by cook
   - Empty results (no matching plans)
   - Error cases (invalid date range)

This handler should handle cases where some files in the directory might be malformed - it should skip those and continue listing valid ones.

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 11: View Meal Plan Handlers

```
Let's implement the view handlers for our Meal Plan MCP server:

1. First, implement the viewMealPlanMarkdown handler:
   - Input: JSON payload with date and mealType
   - Output: Raw Markdown string
   - Workflow:
     * Deserialize request payload
     * Validate fields
     * Compute file path
     * Check if file exists - return NotFound if it doesn't
     * Read file content
     * Return the raw Markdown string

2. Then implement the viewMealPlanJSON handler:
   - Input: JSON payload with date and mealType
   - Output: JSON representation of the MealPlan
   - Workflow:
     * Deserialize request payload
     * Validate fields
     * Compute file path
     * Check if file exists - return NotFound if it doesn't
     * Read file content
     * Parse Markdown into MealPlan struct
     * Return the MealPlan as JSON

3. Write integration tests for both handlers:
   - Successful retrieval of existing meal plans
   - Handling of non-existent meal plans
   - Handling of malformed Markdown files
   - Error cases (invalid date, meal type)

Both handlers should use our previously implemented modules for:
- Path computation (storage module)
- File reading (storage module)
- Markdown parsing (parser module)
- Error handling (errors module)

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 12: Delete Meal Plan Handler

```
Let's implement the deleteMealPlan handler for our Meal Plan MCP server. This handler should:

1. Define a function that takes a DeleteMealPlanRequest and returns an MCP response:
   - Input: JSON payload with date and mealType
   - Output: McpResponse with success flag and message (or an error)

2. Implement the handler workflow:
   - Deserialize request payload to DeleteMealPlanRequest struct
   - Validate fields (date parsing, meal type validation)
   - Compute file path
   - Check if file exists - return NotFound if it doesn't
   - Delete the file
   - Return success response

3. Write integration tests for:
   - Successful deletion of an existing meal plan
   - Handling deletion of non-existent meal plans
   - Error cases (invalid date, meal type)

This handler should use our previously implemented modules for:
- Path computation (storage module)
- File operations (storage module)
- Error handling (errors module)

Ensure the handler provides appropriate feedback on success and meaningful error messages on failure.

Use test-driven development: write the tests first, then implement the functionality.
```

## Prompt 13: MCP Integration

```
Now let's integrate everything with the MCP SDK to create a working server. This involves:

1. Update the main.rs file to:
   - Initialize the MCP SDK
   - Load configuration
   - Register all command handlers
   - Start the MCP server
   - Handle shutdown gracefully

2. Implement a handler registry function that:
   - Takes an MCP server instance
   - Registers all our command handlers:
     * createMealPlan
     * listMealPlans
     * viewMealPlanMarkdown
     * viewMealPlanJSON
     * deleteMealPlan
   - Returns the configured server

3. Implement command routing logic:
   - Parse incoming commands
   - Dispatch to appropriate handlers
   - Convert handler responses to MCP responses
   - Handle errors consistently

4. Write integration tests that:
   - Test the entire server with mock requests
   - Verify correct command routing
   - Test error handling at the server level

The main.rs file should be clean and focused on initialization and wiring, with the actual handler implementations in their respective modules.

Use test-driven development where possible, but recognize that some aspects of server initialization may be difficult to test in isolation.
```

## Prompt 14: End-to-End Testing

```
Let's create comprehensive end-to-end tests for our Meal Plan MCP server. These tests should:

1. Set up a test environment with:
   - Temporary directory for meal plans
   - Configured server instance
   - Helper functions for sending commands and checking responses

2. Implement a complete flow test that:
   - Creates several meal plans
   - Lists them with various filters
   - Views them in both Markdown and JSON formats
   - Deletes some of them
   - Verifies the listing is updated
   - Tests edge cases like case sensitivity in meal types

3. Implement error condition tests:
   - Attempt to create duplicate meal plans
   - Try to view or delete non-existent plans
   - Use invalid dates and meal types
   - Test boundary conditions for date ranges

4. Implement concurrency tests (if applicable):
   - Test multiple simultaneous requests
   - Verify data consistency

These tests should verify that the entire system works correctly together and handles all specified requirements and error conditions properly.

The tests should be clear, self-contained, and provide good diagnostic information on failure.
```

## Prompt 15: Documentation and Cleanup

```
Finally, let's add documentation and clean up our Meal Plan MCP server code:

1. Add comprehensive documentation:
   - Module-level documentation explaining purpose and structure
   - Function-level documentation with parameters, returns, and examples
   - Error documentation explaining when each error occurs
   - README.md with:
     * Project overview
     * Setup instructions
     * Configuration options
     * Example usage

2. Clean up error messages:
   - Ensure all errors have clear, user-friendly messages
   - Include context where helpful (file paths, field names)
   - Consistent formatting across all errors

3. Perform code cleanup:
   - Remove any debug code or TODOs
   - Ensure consistent coding style
   - Check for any remaining edge cases
   - Verify error handling completeness

4. Add runtime logging:
   - Add structured logging throughout the application
   - Log important events (startup, commands, errors)
   - Configure log levels

5. Final review:
   - Verify all requirements are met
   - Check test coverage
   - Ensure documentation is complete

This final polish will make the codebase maintainable, user-friendly, and production-ready.
```

## Conclusion

These prompts provide a step-by-step guide to implementing a Meal Plan MCP server in Rust, following test-driven development principles and gradually building up functionality in manageable, testable increments.

Each prompt builds on the previous ones, and together they cover the entire implementation from initial setup to final polish.
