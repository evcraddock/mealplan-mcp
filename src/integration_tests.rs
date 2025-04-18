#[cfg(test)]
mod integration_tests {
    use crate::config::Config;
    use crate::models::{
        CreateMealPlanRequest, 
        ListMealPlansRequest,
        ViewMealPlanMarkdownRequest,
        ViewMealPlanJsonRequest,
        DeleteMealPlanRequest,
        MealType, 
        Dish, 
        Ingredient, 
        Nutrient
    };
    use crate::build_server;
    use std::path::PathBuf;
    use std::sync::Arc;
    use tempfile::TempDir;
    use chrono::{TimeZone, Utc, Duration};
    use crate::rmcp_mock::server::CommandServer;
    use serde_json::json;
    use anyhow::Result;

    // Helper function to create a test server with temporary directory
    async fn setup_test_server() -> Result<(CommandServer, TempDir)> {
        // Create temporary directory for the test
        let temp_dir = TempDir::new()?;
        let config = Config {
            root_folder: PathBuf::from(temp_dir.path()),
        };
        
        // Create and configure the server
        let server = build_server(Arc::new(config))?;
        
        Ok((server, temp_dir))
    }
    
    // Helper function to create a test meal plan request
    fn create_test_meal_plan_request() -> CreateMealPlanRequest {
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
    
    // Helper function for creating breakfast with different cook
    fn create_breakfast_request() -> CreateMealPlanRequest {
        CreateMealPlanRequest {
            date: Utc.with_ymd_and_hms(2023, 5, 15, 8, 0, 0).unwrap(),
            meal_type: MealType::Breakfast,
            title: "Test Breakfast".to_string(),
            cook: "Another Chef".to_string(),
            dishes: vec![
                Dish {
                    name: "Oatmeal".to_string(),
                    ingredients: vec![
                        Ingredient {
                            name: "Oats".to_string(),
                            amount: "50g".to_string(),
                        },
                        Ingredient {
                            name: "Milk".to_string(),
                            amount: "200ml".to_string(),
                        },
                    ],
                    instructions: vec!["Mix oats and milk".to_string(), "Cook for 3 minutes".to_string()],
                    nutrients: vec![
                        Nutrient {
                            name: "Carbs".to_string(),
                            amount: 30.0,
                            unit: "g".to_string(),
                        },
                    ],
                },
            ],
        }
    }
    
    #[tokio::test]
    async fn test_server_create_meal_plan() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Create a test meal plan request
        let request = create_test_meal_plan_request();
        let request_json = serde_json::to_string(&request)?;
        
        // Send the request to the server
        let response = server.handle_command("createMealPlan", "test-context", &request_json).await?;
        
        // Parse and validate response
        let response_json: serde_json::Value = serde_json::from_str(&response)?;
        assert_eq!(response_json["success"], json!(true));
        assert!(response_json["message"].as_str().unwrap().contains("Successfully created"));
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_list_meal_plans() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Create two meal plans first
        let lunch_request = create_test_meal_plan_request();
        let lunch_json = serde_json::to_string(&lunch_request)?;
        server.handle_command("createMealPlan", "test-context", &lunch_json).await?;
        
        let breakfast_request = create_breakfast_request();
        let breakfast_json = serde_json::to_string(&breakfast_request)?;
        server.handle_command("createMealPlan", "test-context", &breakfast_json).await?;
        
        // Create a list request
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 15, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: None,
        };
        let list_json = serde_json::to_string(&list_request)?;
        
        // Send the list request
        let response = server.handle_command("listMealPlans", "test-context", &list_json).await?;
        
        // Parse and validate response
        let response_json: serde_json::Value = serde_json::from_str(&response)?;
        let meal_plans = response_json["meal_plans"].as_array().unwrap();
        
        // Should have both meal plans
        assert_eq!(meal_plans.len(), 2);
        
        // First should be breakfast (they're sorted by meal type)
        assert_eq!(meal_plans[0]["meal_type"], json!("breakfast"));
        assert_eq!(meal_plans[0]["title"], json!("Test Breakfast"));
        assert_eq!(meal_plans[0]["cook"], json!("Another Chef"));
        
        // Second should be lunch
        assert_eq!(meal_plans[1]["meal_type"], json!("lunch"));
        assert_eq!(meal_plans[1]["title"], json!("Test Lunch"));
        assert_eq!(meal_plans[1]["cook"], json!("Test Chef"));
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_list_meal_plans_with_filters() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Create two meal plans first
        let lunch_request = create_test_meal_plan_request();
        let lunch_json = serde_json::to_string(&lunch_request)?;
        server.handle_command("createMealPlan", "test-context", &lunch_json).await?;
        
        let breakfast_request = create_breakfast_request();
        let breakfast_json = serde_json::to_string(&breakfast_request)?;
        server.handle_command("createMealPlan", "test-context", &breakfast_json).await?;
        
        // Filter by meal type
        let list_by_type_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 15, 23, 59, 59).unwrap(),
            meal_types: Some(vec![MealType::Lunch]),
            cook: None,
        };
        let list_type_json = serde_json::to_string(&list_by_type_request)?;
        
        let type_response = server.handle_command("listMealPlans", "test-context", &list_type_json).await?;
        let type_json: serde_json::Value = serde_json::from_str(&type_response)?;
        let type_results = type_json["meal_plans"].as_array().unwrap();
        
        // Should only have lunch
        assert_eq!(type_results.len(), 1);
        assert_eq!(type_results[0]["meal_type"], json!("lunch"));
        
        // Filter by cook
        let list_by_cook_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 15, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: Some("Another".to_string()),
        };
        let list_cook_json = serde_json::to_string(&list_by_cook_request)?;
        
        let cook_response = server.handle_command("listMealPlans", "test-context", &list_cook_json).await?;
        let cook_json: serde_json::Value = serde_json::from_str(&cook_response)?;
        let cook_results = cook_json["meal_plans"].as_array().unwrap();
        
        // Should only have breakfast (by Another Chef)
        assert_eq!(cook_results.len(), 1);
        assert_eq!(cook_results[0]["meal_type"], json!("breakfast"));
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_view_meal_plan_markdown() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Create a meal plan first
        let create_request = create_test_meal_plan_request();
        let create_json = serde_json::to_string(&create_request)?;
        server.handle_command("createMealPlan", "test-context", &create_json).await?;
        
        // Create a view markdown request
        let view_request = ViewMealPlanMarkdownRequest {
            date: create_request.date,
            meal_type: create_request.meal_type,
        };
        let view_json = serde_json::to_string(&view_request)?;
        
        // Send the view request
        let response = server.handle_command("viewMealPlanMarkdown", "test-context", &view_json).await?;
        
        // Validate markdown content
        assert!(response.contains("---"));  // Frontmatter delimiter
        assert!(response.contains("date:"));
        assert!(response.contains("meal_type: lunch"));
        assert!(response.contains("title: Test Lunch"));
        assert!(response.contains("cook: Test Chef"));
        assert!(response.contains("## Test Dish"));  // Dish name
        assert!(response.contains("### Ingredients"));
        assert!(response.contains("Test Ingredient"));
        assert!(response.contains("### Instructions"));
        assert!(response.contains("Test instruction"));
        assert!(response.contains("### Nutrients"));
        assert!(response.contains("Protein"));
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_view_meal_plan_json() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Create a meal plan first
        let create_request = create_test_meal_plan_request();
        let create_json = serde_json::to_string(&create_request)?;
        server.handle_command("createMealPlan", "test-context", &create_json).await?;
        
        // Create a view JSON request
        let view_request = ViewMealPlanJsonRequest {
            date: create_request.date,
            meal_type: create_request.meal_type,
        };
        let view_json = serde_json::to_string(&view_request)?;
        
        // Send the view request
        let response = server.handle_command("viewMealPlanJson", "test-context", &view_json).await?;
        
        // Parse and validate JSON content
        let json_response: serde_json::Value = serde_json::from_str(&response)?;
        
        assert_eq!(json_response["title"], json!("Test Lunch"));
        assert_eq!(json_response["cook"], json!("Test Chef"));
        assert_eq!(json_response["meal_type"], json!("lunch"));
        
        let dishes = json_response["dishes"].as_array().unwrap();
        assert_eq!(dishes.len(), 1);
        assert_eq!(dishes[0]["name"], json!("Test Dish"));
        
        let ingredients = dishes[0]["ingredients"].as_array().unwrap();
        assert_eq!(ingredients.len(), 1);
        assert_eq!(ingredients[0]["name"], json!("Test Ingredient"));
        assert_eq!(ingredients[0]["amount"], json!("100g"));
        
        let nutrients = dishes[0]["nutrients"].as_array().unwrap();
        assert_eq!(nutrients.len(), 1);
        assert_eq!(nutrients[0]["name"], json!("Protein"));
        assert_eq!(nutrients[0]["amount"], json!(20.0));
        assert_eq!(nutrients[0]["unit"], json!("g"));
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_delete_meal_plan() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Create a meal plan first
        let create_request = create_test_meal_plan_request();
        let create_json = serde_json::to_string(&create_request)?;
        server.handle_command("createMealPlan", "test-context", &create_json).await?;
        
        // Create a delete request
        let delete_request = DeleteMealPlanRequest {
            date: create_request.date,
            meal_type: create_request.meal_type,
        };
        let delete_json = serde_json::to_string(&delete_request)?;
        
        // Send the delete request
        let response = server.handle_command("deleteMealPlan", "test-context", &delete_json).await?;
        
        // Parse and validate response
        let response_json: serde_json::Value = serde_json::from_str(&response)?;
        assert_eq!(response_json["success"], json!(true));
        assert!(response_json["message"].as_str().unwrap().contains("Successfully deleted"));
        
        // Try to view the deleted meal plan - should fail
        let view_request = ViewMealPlanMarkdownRequest {
            date: create_request.date,
            meal_type: create_request.meal_type,
        };
        let view_json = serde_json::to_string(&view_request)?;
        
        let view_result = server.handle_command("viewMealPlanMarkdown", "test-context", &view_json).await;
        assert!(view_result.is_err());
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_not_found_error() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Try to view a non-existent meal plan
        let view_request = ViewMealPlanMarkdownRequest {
            date: Utc.with_ymd_and_hms(2025, 1, 1, 12, 0, 0).unwrap(),
            meal_type: MealType::Lunch,
        };
        let view_json = serde_json::to_string(&view_request)?;
        
        let view_result = server.handle_command("viewMealPlanMarkdown", "test-context", &view_json).await;
        assert!(view_result.is_err());
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_validation_error() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Create a meal plan with invalid dates
        let list_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 14, 0, 0, 0).unwrap(),  // End before start
            meal_types: None,
            cook: None,
        };
        let list_json = serde_json::to_string(&list_request)?;
        
        let list_result = server.handle_command("listMealPlans", "test-context", &list_json).await;
        assert!(list_result.is_err());
        
        // Create a meal plan with empty title
        let mut request = create_test_meal_plan_request();
        request.title = "".to_string();
        let invalid_json = serde_json::to_string(&request)?;
        
        let create_result = server.handle_command("createMealPlan", "test-context", &invalid_json).await;
        assert!(create_result.is_err());
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_duplicate_error() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // Create a meal plan
        let request = create_test_meal_plan_request();
        let request_json = serde_json::to_string(&request)?;
        
        // First creation should succeed
        server.handle_command("createMealPlan", "test-context", &request_json).await?;
        
        // Second creation with same parameters should fail
        let dup_result = server.handle_command("createMealPlan", "test-context", &request_json).await;
        assert!(dup_result.is_err());
        
        Ok(())
    }
    
    #[tokio::test]
    async fn test_server_end_to_end_workflow() -> Result<()> {
        // Setup test server
        let (server, _temp_dir) = setup_test_server().await?;
        
        // 1. Create multiple meal plans
        let lunch = create_test_meal_plan_request();
        let lunch_json = serde_json::to_string(&lunch)?;
        server.handle_command("createMealPlan", "test-context", &lunch_json).await?;
        
        let breakfast = create_breakfast_request();
        let breakfast_json = serde_json::to_string(&breakfast)?;
        server.handle_command("createMealPlan", "test-context", &breakfast_json).await?;
        
        // Create another meal plan for tomorrow
        let mut tomorrow_lunch = create_test_meal_plan_request();
        tomorrow_lunch.date = tomorrow_lunch.date + Duration::days(1);
        tomorrow_lunch.title = "Tomorrow's Lunch".to_string();
        let tomorrow_json = serde_json::to_string(&tomorrow_lunch)?;
        server.handle_command("createMealPlan", "test-context", &tomorrow_json).await?;
        
        // 2. List all meal plans
        let list_all_request = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 5, 16, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: None,
        };
        let list_all_json = serde_json::to_string(&list_all_request)?;
        
        let list_all_response = server.handle_command("listMealPlans", "test-context", &list_all_json).await?;
        let list_all_result: serde_json::Value = serde_json::from_str(&list_all_response)?;
        let all_meal_plans = list_all_result["meal_plans"].as_array().unwrap();
        
        // Should have all three meal plans
        assert_eq!(all_meal_plans.len(), 3);
        
        // 3. View one meal plan in markdown
        let view_md_request = ViewMealPlanMarkdownRequest {
            date: lunch.date,
            meal_type: lunch.meal_type.clone(),
        };
        let view_md_json = serde_json::to_string(&view_md_request)?;
        
        let md_response = server.handle_command("viewMealPlanMarkdown", "test-context", &view_md_json).await?;
        assert!(md_response.contains("Test Lunch"));
        
        // 4. View same meal plan in JSON
        let view_json_request = ViewMealPlanJsonRequest {
            date: lunch.date,
            meal_type: lunch.meal_type.clone(),
        };
        let view_json_json = serde_json::to_string(&view_json_request)?;
        
        let json_response = server.handle_command("viewMealPlanJson", "test-context", &view_json_json).await?;
        let json_content: serde_json::Value = serde_json::from_str(&json_response)?;
        assert_eq!(json_content["title"], json!("Test Lunch"));
        
        // 5. Delete one meal plan
        let delete_request = DeleteMealPlanRequest {
            date: breakfast.date,
            meal_type: breakfast.meal_type.clone(),
        };
        let delete_json = serde_json::to_string(&delete_request)?;
        
        server.handle_command("deleteMealPlan", "test-context", &delete_json).await?;
        
        // 6. List meal plans again to confirm deletion
        let list_after_delete = server.handle_command("listMealPlans", "test-context", &list_all_json.to_string()).await?;
        let after_delete_json: serde_json::Value = serde_json::from_str(&list_after_delete)?;
        let remaining_meal_plans = after_delete_json["meal_plans"].as_array().unwrap();
        
        // Should have two meal plans now
        assert_eq!(remaining_meal_plans.len(), 2);
        
        // None should be breakfast
        for meal_plan in remaining_meal_plans {
            assert_ne!(meal_plan["meal_type"], json!("breakfast"));
        }
        
        Ok(())
    }
}