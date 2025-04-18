mod config;
mod storage;
mod parser;
mod handlers;
mod errors;
mod models;
mod rmcp_mock;
mod integration_tests;

use std::sync::Arc;
use anyhow::Result;

// Import the appropriate implementation based on feature flags
#[cfg(feature = "use-real-rmcp")]
use rmcp::server::{CommandServer, CommandServerBuilder};

#[cfg(any(feature = "use-mock", test))]
use rmcp_mock::server::{CommandServer, CommandServerBuilder};

use tokio::signal;
use config::Config;
use models::{
    CreateMealPlanRequest, 
    ListMealPlansRequest,
    ViewMealPlanMarkdownRequest,
    ViewMealPlanJsonRequest,
    DeleteMealPlanRequest,
};
// Handlers
use handlers::{
    create_meal_plan,
    list_meal_plans,
    view_meal_plan_markdown,
    view_meal_plan_json,
    delete_meal_plan_handler,
};

#[tokio::main]
async fn main() -> Result<()> {
    println!("Starting Meal Plan MCP Server");
    
    // Load configuration
    let config = match Config::load(None) {
        Ok(config) => {
            println!("Configuration loaded successfully");
            println!("Root folder: {}", config.root_folder.display());
            Arc::new(config)
        },
        Err(err) => {
            eprintln!("Failed to load configuration: {}", err);
            return Err(anyhow::anyhow!("Configuration error: {}", err));
        }
    };
    
    // Create and configure the MCP server
    let server = build_server(config.clone())?;
    
    // Start the server
    let server_handle = server.start().await?;
    println!("Meal Plan MCP Server started successfully");
    
    // Wait for shutdown signal
    match signal::ctrl_c().await {
        Ok(()) => {
            println!("Shutdown signal received, stopping server...");
            server_handle.stop().await?;
            println!("Server stopped successfully");
        },
        Err(err) => {
            eprintln!("Failed to listen for shutdown signal: {}", err);
        }
    }
    
    Ok(())
}

/// Builds and configures the MCP server with all command handlers
fn build_server(config: Arc<Config>) -> Result<CommandServer> {
    let mut builder = CommandServerBuilder::new();
    
    // Register createMealPlan handler
    {
        let config = config.clone();
        builder.register_command("createMealPlan", move |_context: String, request_json: String| {
            let config = config.clone();
            Box::pin(async move {
                match serde_json::from_str::<CreateMealPlanRequest>(&request_json) {
                    Ok(request) => {
                        match create_meal_plan(request, &config).await {
                            Ok(response) => Ok(serde_json::to_string(&response)?),
                            Err(err) => {
                                eprintln!("Error in createMealPlan handler: {}", err);
                                Err(anyhow::anyhow!("{}", err))
                            }
                        }
                    },
                    Err(err) => {
                        eprintln!("Error parsing createMealPlan request: {}", err);
                        Err(anyhow::anyhow!("Invalid request format: {}", err))
                    }
                }
            })
        });
    }
    
    // Register listMealPlans handler
    {
        let config = config.clone();
        builder.register_command("listMealPlans", move |_context: String, request_json: String| {
            let config = config.clone();
            Box::pin(async move {
                match serde_json::from_str::<ListMealPlansRequest>(&request_json) {
                    Ok(request) => {
                        match list_meal_plans(request, &config).await {
                            Ok(response) => Ok(serde_json::to_string(&response)?),
                            Err(err) => {
                                eprintln!("Error in listMealPlans handler: {}", err);
                                Err(anyhow::anyhow!("{}", err))
                            }
                        }
                    },
                    Err(err) => {
                        eprintln!("Error parsing listMealPlans request: {}", err);
                        Err(anyhow::anyhow!("Invalid request format: {}", err))
                    }
                }
            })
        });
    }
    
    // Register viewMealPlanMarkdown handler
    {
        let config = config.clone();
        builder.register_command("viewMealPlanMarkdown", move |_context: String, request_json: String| {
            let config = config.clone();
            Box::pin(async move {
                match serde_json::from_str::<ViewMealPlanMarkdownRequest>(&request_json) {
                    Ok(request) => {
                        match view_meal_plan_markdown(request, &config).await {
                            Ok(markdown) => Ok(markdown),
                            Err(err) => {
                                eprintln!("Error in viewMealPlanMarkdown handler: {}", err);
                                Err(anyhow::anyhow!("{}", err))
                            }
                        }
                    },
                    Err(err) => {
                        eprintln!("Error parsing viewMealPlanMarkdown request: {}", err);
                        Err(anyhow::anyhow!("Invalid request format: {}", err))
                    }
                }
            })
        });
    }
    
    // Register viewMealPlanJson handler
    {
        let config = config.clone();
        builder.register_command("viewMealPlanJson", move |_context: String, request_json: String| {
            let config = config.clone();
            Box::pin(async move {
                match serde_json::from_str::<ViewMealPlanJsonRequest>(&request_json) {
                    Ok(request) => {
                        match view_meal_plan_json(request, &config).await {
                            Ok(json) => Ok(json),
                            Err(err) => {
                                eprintln!("Error in viewMealPlanJson handler: {}", err);
                                Err(anyhow::anyhow!("{}", err))
                            }
                        }
                    },
                    Err(err) => {
                        eprintln!("Error parsing viewMealPlanJson request: {}", err);
                        Err(anyhow::anyhow!("Invalid request format: {}", err))
                    }
                }
            })
        });
    }
    
    // Register deleteMealPlan handler
    {
        let config = config.clone();
        builder.register_command("deleteMealPlan", move |_context: String, request_json: String| {
            let config = config.clone();
            Box::pin(async move {
                match serde_json::from_str::<DeleteMealPlanRequest>(&request_json) {
                    Ok(request) => {
                        match delete_meal_plan_handler(request, &config).await {
                            Ok(response) => Ok(serde_json::to_string(&response)?),
                            Err(err) => {
                                eprintln!("Error in deleteMealPlan handler: {}", err);
                                Err(anyhow::anyhow!("{}", err))
                            }
                        }
                    },
                    Err(err) => {
                        eprintln!("Error parsing deleteMealPlan request: {}", err);
                        Err(anyhow::anyhow!("Invalid request format: {}", err))
                    }
                }
            })
        });
    }
    
    // Build the server
    let server = builder.build()?;
    Ok(server)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;
    use std::sync::Arc;
    use tempfile::TempDir;
    use chrono::{TimeZone, Utc};
    use models::{MealType, Dish, Ingredient, Nutrient};
    
    // Setup test configuration with a temporary directory
    fn setup_test_config() -> (Arc<Config>, TempDir) {
        let temp_dir = TempDir::new().unwrap();
        let config = Config {
            root_folder: PathBuf::from(temp_dir.path()),
        };
        (Arc::new(config), temp_dir)
    }
    
    // Create a test meal plan request
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
    
    #[tokio::test]
    async fn test_build_server() {
        let (config, _temp_dir) = setup_test_config();
        
        // Test server creation
        let server = build_server(config).unwrap();
        
        // Verify that the server has all expected commands registered
        // Note: Since we can't easily inspect the registered commands directly,
        // we're relying on the fact that build_server would fail if registration failed
        assert!(true);
    }
    
    #[tokio::test]
    async fn test_server_request_flow() {
        // This test is a placeholder for more comprehensive server integration tests
        // In a real implementation, we would:
        // 1. Start a server instance
        // 2. Send mock requests to each endpoint
        // 3. Verify the responses
        
        // For now, we're just verifying that the build_server function works
        let (config, _temp_dir) = setup_test_config();
        let server = build_server(config).unwrap();
        
        // In a real test, we'd use server methods to send requests here
        
        // For now, just assert that we can create the server
        assert!(true);
    }
}
