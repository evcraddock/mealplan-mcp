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
- [ ] Implement YAML frontmatter extraction/generation
- [ ] Create Markdown body parsing/generation for dishes
- [ ] Add complete serialization/deserialization functions
- [ ] Write unit tests for parsing functions

## Error Handling
- [ ] Define custom error types using thiserror
- [ ] Implement conversions from library errors
- [ ] Add conversion to MCP errors
- [ ] Write unit tests for error handling

## MCP Command Handlers
- [ ] Implement createMealPlan handler
- [ ] Add listMealPlans handler with filtering
- [ ] Create viewMealPlanMarkdown and viewMealPlanJSON handlers
- [ ] Implement deleteMealPlan handler
- [ ] Write integration tests for all handlers

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