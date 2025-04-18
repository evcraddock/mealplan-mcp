// Command handlers for the Meal Plan MCP server
use anyhow::Result;
use std::fs;
use std::path::Path;
use chrono::{Datelike, TimeZone, Utc};
use serde_json;

use crate::config::Config;
use crate::models::{CreateMealPlanRequest, CreateMealPlanResponse, ListMealPlansRequest, ListMealPlansResponse, MealPlanSummary, MealType, MealPlan, ViewMealPlanMarkdownRequest, ViewMealPlanJsonRequest, DeleteMealPlanRequest, DeleteMealPlanResponse};
use crate::storage::{compute_directory_path, compute_file_path, ensure_directories_exist, meal_plan_exists, write_meal_plan};
use crate::parser::{extract_frontmatter, parse_frontmatter, serialize_meal_plan_to_markdown, deserialize_markdown_to_meal_plan};
use crate::errors::{AlreadyExistsError, NotFoundError};

/// Handler for the createMealPlan command
pub async fn create_meal_plan(request: CreateMealPlanRequest, config: &Config) -> Result<CreateMealPlanResponse> {
    // Validate request fields
    request.validate()?;
    
    // Compute file path
    let file_path = compute_file_path(&request.date, &request.meal_type, &config.root_folder);
    
    // Check if file already exists
    if meal_plan_exists(&request.date, &request.meal_type, &config.root_folder) {
        return Err(AlreadyExistsError::MealPlanAlreadyExists(file_path.to_string_lossy().to_string()).into());
    }
    
    // Convert request to MealPlan
    let meal_plan = request.to_meal_plan();
    
    // Serialize MealPlan to Markdown
    let markdown = serialize_meal_plan_to_markdown(&meal_plan);
    
    // Ensure directories exist
    ensure_directories_exist(&file_path)?;
    
    // Write the file
    write_meal_plan(&markdown, &request.date, &request.meal_type, &config.root_folder)?;
    
    // Return success response
    Ok(CreateMealPlanResponse {
        success: true,
        message: format!("Successfully created meal plan for {} {}", 
            request.meal_type.to_string(), 
            request.date.format("%Y-%m-%d")),
    })
}

/// Handler for the listMealPlans command
pub async fn list_meal_plans(request: ListMealPlansRequest, config: &Config) -> Result<ListMealPlansResponse> {
    // Validate request fields
    request.validate()?;
    
    // Extract dates for easier access
    let start_date = request.start_date.date_naive();
    let end_date = request.end_date.date_naive();
    
    // Prepare collection for results
    let mut meal_plans = Vec::new();
    
    // Generate a date range to iterate through
    let mut current_date = start_date;
    while current_date <= end_date {
        // Convert the NaiveDate to DateTime<Utc> for directory path computation
        let year = current_date.year();
        let month = current_date.month();
        let day = current_date.day();
        let current_datetime = Utc.with_ymd_and_hms(year, month, day, 0, 0, 0).unwrap();
        
        // Get the directory path for this date
        let dir_path = compute_directory_path(&current_datetime, &config.root_folder);
        
        // If directory exists, scan for meal plans
        if dir_path.exists() {
            // Find all markdown files in the directory
            if let Ok(entries) = fs::read_dir(&dir_path) {
                for entry in entries.flatten() {
                    let path = entry.path();
                    
                    // Skip if not a file or not a markdown file
                    if !path.is_file() || path.extension().map_or(true, |ext| ext != "md") {
                        continue;
                    }
                    
                    // Try to parse meal plan from file
                    if let Some(meal_plan_summary) = extract_meal_plan_summary(&path, &request).ok().flatten() {
                        // Apply filters
                        let passes_filters = match_filters(&meal_plan_summary, &request);
                        
                        if passes_filters {
                            meal_plans.push(meal_plan_summary);
                        }
                    }
                }
            }
        }
        
        // Move to next day
        current_date = match current_date.succ_opt() {
            Some(next_date) => next_date,
            None => break, // Handle end of valid date range
        };
    }
    
    // Sort meal plans by date and meal type
    meal_plans.sort_by(|a, b| {
        if a.date != b.date {
            a.date.cmp(&b.date)
        } else {
            let a_order = meal_type_order(&a.meal_type);
            let b_order = meal_type_order(&b.meal_type);
            a_order.cmp(&b_order)
        }
    });
    
    Ok(ListMealPlansResponse { meal_plans })
}

/// Handler for the viewMealPlanMarkdown command
pub async fn view_meal_plan_markdown(request: ViewMealPlanMarkdownRequest, config: &Config) -> Result<String> {
    // Compute file path
    let file_path = compute_file_path(&request.date, &request.meal_type, &config.root_folder);
    
    // Check if the file exists
    if !file_path.exists() {
        return Err(NotFoundError::MealPlanNotFound(file_path.to_string_lossy().to_string()).into());
    }
    
    // Read the file content
    match fs::read_to_string(&file_path) {
        Ok(content) => Ok(content),
        Err(e) => Err(anyhow::anyhow!("Failed to read meal plan markdown: {}", e)),
    }
}

/// Handler for the viewMealPlanJson command
pub async fn view_meal_plan_json(request: ViewMealPlanJsonRequest, config: &Config) -> Result<String> {
    // Compute file path
    let file_path = compute_file_path(&request.date, &request.meal_type, &config.root_folder);
    
    // Check if the file exists
    if !file_path.exists() {
        return Err(NotFoundError::MealPlanNotFound(file_path.to_string_lossy().to_string()).into());
    }
    
    // Read the file content
    let content = fs::read_to_string(&file_path)?;
    
    // Parse the markdown into a MealPlan struct
    let meal_plan = deserialize_markdown_to_meal_plan(&content)?;
    
    // Serialize the MealPlan to JSON
    match serde_json::to_string_pretty(&meal_plan) {
        Ok(json) => Ok(json),
        Err(e) => Err(anyhow::anyhow!("Failed to serialize meal plan to JSON: {}", e)),
    }
}

/// Handler for the deleteMealPlan command
pub async fn delete_meal_plan_handler(request: DeleteMealPlanRequest, config: &Config) -> Result<DeleteMealPlanResponse> {
    // Compute file path
    let file_path = compute_file_path(&request.date, &request.meal_type, &config.root_folder);
    
    // Check if the file exists
    if !file_path.exists() {
        return Err(NotFoundError::MealPlanNotFound(file_path.to_string_lossy().to_string()).into());
    }
    
    // Delete the meal plan file
    crate::storage::delete_meal_plan(&request.date, &request.meal_type, &config.root_folder)?;
    
    // Return success response
    Ok(DeleteMealPlanResponse {
        success: true,
        message: format!("Successfully deleted meal plan for {} {}", 
            request.meal_type.to_string(), 
            request.date.format("%Y-%m-%d")),
    })
}

/// Extracts meal plan summary from a file, returns None if file is malformed or doesn't exist
fn extract_meal_plan_summary(path: &Path, request: &ListMealPlansRequest) -> Result<Option<MealPlanSummary>> {
    // Read the file content
    let content = match fs::read_to_string(path) {
        Ok(content) => content,
        Err(_) => return Ok(None), // Skip if file can't be read
    };
    
    // Extract frontmatter
    let (frontmatter, _) = match extract_frontmatter(&content) {
        Ok(result) => result,
        Err(_) => return Ok(None), // Skip if frontmatter can't be extracted
    };
    
    // Parse frontmatter
    let meal_plan = match parse_frontmatter(&frontmatter) {
        Ok(meal_plan) => meal_plan,
        Err(_) => return Ok(None), // Skip if frontmatter can't be parsed
    };
    
    // Check if meal plan date is within requested range
    if meal_plan.date < request.start_date || meal_plan.date > request.end_date {
        return Ok(None);
    }
    
    // Create summary
    let summary = MealPlanSummary {
        date: meal_plan.date,
        meal_type: meal_plan.meal_type,
        title: meal_plan.title,
        cook: meal_plan.cook,
    };
    
    Ok(Some(summary))
}

/// Check if a meal plan summary passes the filters in the request
fn match_filters(summary: &MealPlanSummary, request: &ListMealPlansRequest) -> bool {
    // Check meal_types filter
    if let Some(meal_types) = &request.meal_types {
        if !meal_types.contains(&summary.meal_type) {
            return false;
        }
    }
    
    // Check cook filter
    if let Some(cook) = &request.cook {
        if !summary.cook.to_lowercase().contains(&cook.to_lowercase()) {
            return false;
        }
    }
    
    true
}

/// Get sort order for meal types
fn meal_type_order(meal_type: &MealType) -> u8 {
    match meal_type {
        MealType::Breakfast => 0,
        MealType::Lunch => 1,
        MealType::Dinner => 2,
        MealType::Snack => 3,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;
    use tempfile::TempDir;
    use chrono::{TimeZone, Utc};
    use crate::models::{Dish, Ingredient, Nutrient, MealType};
    
    fn setup_test_config() -> (Config, TempDir) {
        let temp_dir = TempDir::new().unwrap();
        let config = Config {
            root_folder: PathBuf::from(temp_dir.path()),
        };
        (config, temp_dir)
    }
    
    fn create_test_request() -> CreateMealPlanRequest {
        CreateMealPlanRequest {
            date: Utc.with_ymd_and_hms(2023, 5, 15, 12, 0, 0).unwrap(),
            meal_type: MealType::Lunch,
            title: "Test Lunch".to_string(),
            cook: "Test Chef".to_string(),
            dishes: vec![
                Dish {
                    name: "Test Dish".to_string(),
                    ingredients: vec![
                        Ingredient {
                            name: "Test Ingredient".to_string(),
                            amount: "100g".to_string(),
                        },
                    ],
                    instructions: vec!["Test instruction".to_string()],
                    nutrients: vec![
                        Nutrient {
                            name: "Protein".to_string(),
                            amount: 20.0,
                            unit: "g".to_string(),
                        },
                    ],
                },
            ],
        }
    }
    
    #[tokio::test]
    async fn test_create_meal_plan_success() {
        let (config, _temp_dir) = setup_test_config();
        let request = create_test_request();
        
        let response = create_meal_plan(request.clone(), &config).await.unwrap();
        
        assert!(response.success);
        assert!(response.message.contains("Successfully created"));
        
        // Verify file exists
        let file_path = compute_file_path(&request.date, &request.meal_type, &config.root_folder);
        assert!(file_path.exists());
    }
    
    #[tokio::test]
    async fn test_create_meal_plan_already_exists() {
        let (config, _temp_dir) = setup_test_config();
        let request = create_test_request();
        
        // Create first time - should succeed
        let _ = create_meal_plan(request.clone(), &config).await.unwrap();
        
        // Create second time - should fail with AlreadyExists
        let result = create_meal_plan(request, &config).await;
        assert!(result.is_err());
        
        // Check error type
        let err = result.unwrap_err();
        let downcast_err = err.downcast::<AlreadyExistsError>();
        assert!(downcast_err.is_ok());
    }
    
    #[tokio::test]
    async fn test_create_meal_plan_validation() {
        let (config, _temp_dir) = setup_test_config();
        
        // Create request with empty title
        let mut invalid_request = create_test_request();
        invalid_request.title = "".to_string();
        
        let result = create_meal_plan(invalid_request, &config).await;
        assert!(result.is_err());
    }
    
    #[tokio::test]
    async fn test_create_meal_plan_dish_validation() {
        let (config, _temp_dir) = setup_test_config();
        
        // Create request with invalid dish (empty name)
        let mut invalid_request = create_test_request();
        invalid_request.dishes[0].name = "".to_string();
        
        let result = create_meal_plan(invalid_request, &config).await;
        assert!(result.is_err());
    }
    
    // Tests for list_meal_plans
    
    async fn create_meal_plans_for_testing(config: &Config) -> Vec<CreateMealPlanRequest> {
        // Create sample meal plans for testing
        let breakfast = CreateMealPlanRequest {
            date: Utc.with_ymd_and_hms(2023, 5, 15, 8, 0, 0).unwrap(),
            meal_type: MealType::Breakfast,
            title: "Test Breakfast".to_string(),
            cook: "Alice".to_string(),
            dishes: vec![
                Dish {
                    name: "Oatmeal".to_string(),
                    ingredients: vec![
                        Ingredient {
                            name: "Oats".to_string(),
                            amount: "100g".to_string(),
                        },
                    ],
                    instructions: vec!["Cook oats".to_string()],
                    nutrients: vec![],
                },
            ],
        };
        
        let lunch = CreateMealPlanRequest {
            date: Utc.with_ymd_and_hms(2023, 5, 15, 12, 0, 0).unwrap(),
            meal_type: MealType::Lunch,
            title: "Test Lunch".to_string(),
            cook: "Bob".to_string(),
            dishes: vec![
                Dish {
                    name: "Sandwich".to_string(),
                    ingredients: vec![
                        Ingredient {
                            name: "Bread".to_string(),
                            amount: "2 slices".to_string(),
                        },
                    ],
                    instructions: vec!["Make sandwich".to_string()],
                    nutrients: vec![],
                },
            ],
        };
        
        let dinner = CreateMealPlanRequest {
            date: Utc.with_ymd_and_hms(2023, 5, 15, 18, 0, 0).unwrap(),
            meal_type: MealType::Dinner,
            title: "Test Dinner".to_string(),
            cook: "Alice".to_string(),
            dishes: vec![
                Dish {
                    name: "Pasta".to_string(),
                    ingredients: vec![
                        Ingredient {
                            name: "Pasta".to_string(),
                            amount: "200g".to_string(),
                        },
                    ],
                    instructions: vec!["Cook pasta".to_string()],
                    nutrients: vec![],
                },
            ],
        };
        
        let next_day_breakfast = CreateMealPlanRequest {
            date: Utc.with_ymd_and_hms(2023, 5, 16, 8, 0, 0).unwrap(),
            meal_type: MealType::Breakfast,
            title: "Next Day Breakfast".to_string(),
            cook: "Charlie".to_string(),
            dishes: vec![
                Dish {
                    name: "Eggs".to_string(),
                    ingredients: vec![
                        Ingredient {
                            name: "Eggs".to_string(),
                            amount: "2".to_string(),
                        },
                    ],
                    instructions: vec!["Cook eggs".to_string()],
                    nutrients: vec![],
                },
            ],
        };
        
        let requests = vec![breakfast, lunch, dinner, next_day_breakfast];
        
        // Create all the meal plans
        for request in &requests {
            let _ = create_meal_plan(request.clone(), config).await.unwrap();
        }
        
        requests
    }
    
    #[tokio::test]
    async fn test_list_meal_plans_all() {
        let (config, _temp_dir) = setup_test_config();
        let _requests = create_meal_plans_for_testing(&config).await;
        
        // Create a request for all meal plans in the date range
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 16, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: None,
        };
        
        // List meal plans
        let response = list_meal_plans(list_request, &config).await.unwrap();
        
        // Verify all meal plans are returned
        assert_eq!(response.meal_plans.len(), 4);
        
        // Verify they are in correct order (by date, then meal type)
        assert_eq!(response.meal_plans[0].meal_type, MealType::Breakfast);
        assert_eq!(response.meal_plans[0].date.date_naive().day(), 15);
        
        assert_eq!(response.meal_plans[1].meal_type, MealType::Lunch);
        assert_eq!(response.meal_plans[1].date.date_naive().day(), 15);
        
        assert_eq!(response.meal_plans[2].meal_type, MealType::Dinner);
        assert_eq!(response.meal_plans[2].date.date_naive().day(), 15);
        
        assert_eq!(response.meal_plans[3].meal_type, MealType::Breakfast);
        assert_eq!(response.meal_plans[3].date.date_naive().day(), 16);
    }
    
    #[tokio::test]
    async fn test_list_meal_plans_by_date() {
        let (config, _temp_dir) = setup_test_config();
        let _ = create_meal_plans_for_testing(&config).await;
        
        // Create a request for just the first day
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 15, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: None,
        };
        
        // List meal plans
        let response = list_meal_plans(list_request, &config).await.unwrap();
        
        // Verify only the first day meal plans are returned
        assert_eq!(response.meal_plans.len(), 3);
        
        // All should be from the 15th
        for meal_plan in &response.meal_plans {
            assert_eq!(meal_plan.date.date_naive().day(), 15);
        }
    }
    
    #[tokio::test]
    async fn test_list_meal_plans_by_meal_type() {
        let (config, _temp_dir) = setup_test_config();
        let _ = create_meal_plans_for_testing(&config).await;
        
        // Create a request for breakfast meals only
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 16, 23, 59, 59).unwrap(),
            meal_types: Some(vec![MealType::Breakfast]),
            cook: None,
        };
        
        // List meal plans
        let response = list_meal_plans(list_request, &config).await.unwrap();
        
        // Verify only breakfast meal plans are returned
        assert_eq!(response.meal_plans.len(), 2);
        
        // All should be breakfast
        for meal_plan in &response.meal_plans {
            assert_eq!(meal_plan.meal_type, MealType::Breakfast);
        }
    }
    
    #[tokio::test]
    async fn test_list_meal_plans_by_cook() {
        let (config, _temp_dir) = setup_test_config();
        let _ = create_meal_plans_for_testing(&config).await;
        
        // Create a request for Alice's meals only
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 16, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: Some("Alice".to_string()),
        };
        
        // List meal plans
        let response = list_meal_plans(list_request, &config).await.unwrap();
        
        // Verify only Alice's meal plans are returned
        assert_eq!(response.meal_plans.len(), 2);
        
        // All should be by Alice
        for meal_plan in &response.meal_plans {
            assert_eq!(meal_plan.cook, "Alice");
        }
    }
    
    #[tokio::test]
    async fn test_list_meal_plans_empty_result() {
        let (config, _temp_dir) = setup_test_config();
        let _ = create_meal_plans_for_testing(&config).await;
        
        // Create a request for a date range with no meal plans
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 6, 1, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 6, 30, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: None,
        };
        
        // List meal plans
        let response = list_meal_plans(list_request, &config).await.unwrap();
        
        // Verify no meal plans are returned
        assert_eq!(response.meal_plans.len(), 0);
    }
    
    #[tokio::test]
    async fn test_list_meal_plans_invalid_date_range() {
        let (config, _temp_dir) = setup_test_config();
        
        // Create a request with end date before start date
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 16, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 15, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: None,
        };
        
        // List meal plans should return error
        let result = list_meal_plans(list_request, &config).await;
        assert!(result.is_err());
    }
    
    #[tokio::test]
    async fn test_list_meal_plans_combined_filters() {
        let (config, _temp_dir) = setup_test_config();
        let _ = create_meal_plans_for_testing(&config).await;
        
        // Create a request with both meal type and cook filters
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 16, 23, 59, 59).unwrap(),
            meal_types: Some(vec![MealType::Breakfast]),
            cook: Some("Alice".to_string()),
        };
        
        // List meal plans
        let response = list_meal_plans(list_request, &config).await.unwrap();
        
        // Verify only Alice's breakfast is returned
        assert_eq!(response.meal_plans.len(), 1);
        assert_eq!(response.meal_plans[0].meal_type, MealType::Breakfast);
        assert_eq!(response.meal_plans[0].cook, "Alice");
    }
    
    // Tests for view_meal_plan_markdown
    
    #[tokio::test]
    async fn test_view_meal_plan_markdown_success() {
        let (config, _temp_dir) = setup_test_config();
        let request = create_test_request();
        
        // First create a meal plan
        let _ = create_meal_plan(request.clone(), &config).await.unwrap();
        
        // Create a view request for the same meal plan
        let view_request = ViewMealPlanMarkdownRequest {
            date: request.date,
            meal_type: request.meal_type.clone(),
        };
        
        // View meal plan markdown
        let markdown = view_meal_plan_markdown(view_request, &config).await.unwrap();
        
        // Verify the markdown contains expected content
        assert!(markdown.contains("---"));  // Frontmatter delimiter
        assert!(markdown.contains("date:"));
        assert!(markdown.contains("meal_type: lunch"));
        assert!(markdown.contains("title: Test Lunch"));
        assert!(markdown.contains("cook: Test Chef"));
        assert!(markdown.contains("## Test Dish"));  // Dish name
        assert!(markdown.contains("### Ingredients"));
        assert!(markdown.contains("Test Ingredient"));
        assert!(markdown.contains("### Instructions"));
        assert!(markdown.contains("Test instruction"));
        assert!(markdown.contains("### Nutrients"));
        assert!(markdown.contains("Protein"));
    }
    
    #[tokio::test]
    async fn test_view_meal_plan_markdown_not_found() {
        let (config, _temp_dir) = setup_test_config();
        
        // Create a view request for a non-existent meal plan
        let view_request = ViewMealPlanMarkdownRequest {
            date: Utc.with_ymd_and_hms(2023, 6, 1, 12, 0, 0).unwrap(),
            meal_type: MealType::Lunch,
        };
        
        // View meal plan markdown should return NotFound error
        let result = view_meal_plan_markdown(view_request, &config).await;
        assert!(result.is_err());
        
        // Check error type
        let err = result.unwrap_err();
        let downcast_err = err.downcast::<NotFoundError>();
        assert!(downcast_err.is_ok());
    }
    
    // Tests for view_meal_plan_json
    
    #[tokio::test]
    async fn test_view_meal_plan_json_success() {
        let (config, _temp_dir) = setup_test_config();
        let request = create_test_request();
        
        // First create a meal plan
        let _ = create_meal_plan(request.clone(), &config).await.unwrap();
        
        // Create a view request for the same meal plan
        let view_request = ViewMealPlanJsonRequest {
            date: request.date,
            meal_type: request.meal_type.clone(),
        };
        
        // View meal plan as JSON
        let meal_plan_json = view_meal_plan_json(view_request, &config).await.unwrap();
        
        // Deserialize back to MealPlan to verify structure
        let meal_plan: MealPlan = serde_json::from_str(&meal_plan_json).unwrap();
        
        // Verify the contents match the original request
        assert_eq!(meal_plan.title, request.title);
        assert_eq!(meal_plan.cook, request.cook);
        assert_eq!(meal_plan.dishes.len(), 1);
        assert_eq!(meal_plan.dishes[0].name, "Test Dish");
        assert_eq!(meal_plan.dishes[0].ingredients.len(), 1);
        assert_eq!(meal_plan.dishes[0].ingredients[0].name, "Test Ingredient");
        assert_eq!(meal_plan.dishes[0].nutrients.len(), 1);
        assert_eq!(meal_plan.dishes[0].nutrients[0].name, "Protein");
    }
    
    #[tokio::test]
    async fn test_view_meal_plan_json_not_found() {
        let (config, _temp_dir) = setup_test_config();
        
        // Create a view request for a non-existent meal plan
        let view_request = ViewMealPlanJsonRequest {
            date: Utc.with_ymd_and_hms(2023, 6, 1, 12, 0, 0).unwrap(),
            meal_type: MealType::Lunch,
        };
        
        // View meal plan JSON should return NotFound error
        let result = view_meal_plan_json(view_request, &config).await;
        assert!(result.is_err());
        
        // Check error type
        let err = result.unwrap_err();
        let downcast_err = err.downcast::<NotFoundError>();
        assert!(downcast_err.is_ok());
    }
    
    // Test for malformed markdown file
    
    #[tokio::test]
    async fn test_view_meal_plan_json_malformed_file() {
        let (config, _temp_dir) = setup_test_config();
        let request = create_test_request();
        
        // First create the meal plan
        let _ = create_meal_plan(request.clone(), &config).await.unwrap();
        
        // Get the file path
        let file_path = compute_file_path(&request.date, &request.meal_type, &config.root_folder);
        
        // Overwrite with invalid content (no frontmatter)
        fs::write(&file_path, "This is not a valid markdown file with frontmatter").unwrap();
        
        // Create a view request for the same meal plan
        let view_request = ViewMealPlanJsonRequest {
            date: request.date,
            meal_type: request.meal_type.clone(),
        };
        
        // View meal plan JSON should return an error
        let result = view_meal_plan_json(view_request, &config).await;
        assert!(result.is_err());
    }
    
    // Tests for delete_meal_plan
    
    #[tokio::test]
    async fn test_delete_meal_plan_success() {
        let (config, _temp_dir) = setup_test_config();
        let request = create_test_request();
        
        // First create a meal plan
        let _ = create_meal_plan(request.clone(), &config).await.unwrap();
        
        // Verify the meal plan file exists
        let file_path = compute_file_path(&request.date, &request.meal_type, &config.root_folder);
        assert!(file_path.exists());
        
        // Create a delete request for the same meal plan
        let delete_request = DeleteMealPlanRequest {
            date: request.date,
            meal_type: request.meal_type.clone(),
        };
        
        // Delete the meal plan
        let response = delete_meal_plan_handler(delete_request, &config).await.unwrap();
        
        // Verify the success response
        assert!(response.success);
        assert!(response.message.contains("Successfully deleted"));
        
        // Verify the file no longer exists
        assert!(!file_path.exists());
    }
    
    #[tokio::test]
    async fn test_delete_meal_plan_not_found() {
        let (config, _temp_dir) = setup_test_config();
        
        // Create a delete request for a non-existent meal plan
        let delete_request = DeleteMealPlanRequest {
            date: Utc.with_ymd_and_hms(2023, 6, 1, 12, 0, 0).unwrap(),
            meal_type: MealType::Lunch,
        };
        
        // Delete the meal plan should return a NotFound error
        let result = delete_meal_plan_handler(delete_request, &config).await;
        assert!(result.is_err());
        
        // Check error type
        let err = result.unwrap_err();
        let downcast_err = err.downcast::<NotFoundError>();
        assert!(downcast_err.is_ok());
    }
}
