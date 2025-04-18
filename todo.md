# Meal Plan MCP Server Implementation Todo List

## Project Setup
- [x] Create Cargo.toml with dependencies
- [x] Set up module structure
- [x] Implement minimal main.rs

## Configuration Module
- [x] Define Config struct
- [x] Implement config loading from TOML
- [x] Write config validation functions
- [x] Add unit tests for config loading/validation

## Core Data Models
- [x] Implement MealPlan struct and enum types
- [x] Create Dish, Ingredient, and Nutrient structs
- [x] Define request/response structs for MCP commands
- [x] Add validation methods for all models
- [x] Write unit tests for validation

## Storage Module
- [x] Create path and directory helper functions
- [x] Implement file path generation for meal plans 
- [x] Add directory creation functionality
- [x] Implement basic file operations (read/write/check/delete)
- [x] Write unit tests for path generation and file operations

## Parser Module
- [x] Implement YAML frontmatter extraction/generation
- [x] Create Markdown body parsing/generation for dishes
- [x] Add complete serialization/deserialization functions
- [x] Write unit tests for YAML frontmatter parsing

## Error Handling
- [x] Define custom error types using thiserror
- [x] Implement conversions from library errors
- [x] Add conversion to MCP errors
- [x] Write unit tests for error handling

## MCP Command Handlers
- [x] Implement createMealPlan handler
- [x] Add listMealPlans handler with filtering
- [x] Create viewMealPlanMarkdown and viewMealPlanJSON handlers
- [x] Implement deleteMealPlan handler
- [x] Write integration tests for createMealPlan handler
- [x] Write integration tests for listMealPlans handler
- [x] Write integration tests for viewMealPlan handlers
- [x] Write integration tests for deleteMealPlan handler

## Server Integration
- [ ] Update main.rs with MCP SDK initialization
- [ ] Register all command handlers
- [ ] Implement command routing logic
- [ ] Add server-level integration tests

## Testing & Documentation
- [ ] Create end-to-end tests with complete workflows
- [ ] Test error conditions and edge cases
- [ ] Add comprehensive documentation
- [ ] Create README.md with setup instructions
- [ ] Perform final code cleanup and review