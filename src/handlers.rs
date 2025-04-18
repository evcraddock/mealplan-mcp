// Command handlers for the Meal Plan MCP server
use anyhow::Result;

use crate::config::Config;
use crate::models::{CreateMealPlanRequest, CreateMealPlanResponse};
use crate::storage::{compute_file_path, ensure_directories_exist, meal_plan_exists, write_meal_plan};
use crate::parser::serialize_meal_plan_to_markdown;
use crate::errors::AlreadyExistsError;

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
}
