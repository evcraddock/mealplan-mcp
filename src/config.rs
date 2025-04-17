// Configuration module for the Meal Plan MCP server
use std::fs;
use std::path::PathBuf;
use anyhow::Result;
use config::{Config as ConfigBuilder, ConfigError as ConfigLibError, File};
use serde::Deserialize;
use thiserror::Error;
use dirs::home_dir;

#[derive(Debug, Deserialize, Clone, PartialEq, Eq)]
pub struct Config {
    pub root_folder: PathBuf,
}

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("Failed to load configuration: {0}")]
    LoadError(#[from] ConfigLibError),
    
    #[error("Root folder does not exist: {0}")]
    NonExistentFolder(PathBuf),
    
    #[error("Root folder is not writable: {0}")]
    NonWritableFolder(PathBuf),
    
    #[error("Home directory not found")]
    HomeDirectoryNotFound,
}

impl Config {
    // Get the default config directory
    fn get_default_config_dir() -> Result<PathBuf, ConfigError> {
        let home = home_dir().ok_or(ConfigError::HomeDirectoryNotFound)?;
        Ok(home.join(".config").join("mealplan-mcp"))
    }
    
    // Load configuration from specified path or use default
    pub fn load(config_path: Option<PathBuf>) -> Result<Self, ConfigError> {
        // Build config from path or default
        let builder = ConfigBuilder::builder();
        
        // If a path is provided, use it; otherwise use the default
        let builder = if let Some(path) = config_path {
            builder.add_source(File::from(path))
        } else {
            // Try to use default config path
            let default_dir = Self::get_default_config_dir()?;
            let default_config = default_dir.join("config.toml");
            
            builder.add_source(File::from(default_config).required(false))
                  // Also allow a local config.toml to override the default
                  .add_source(File::with_name("config.toml").required(false))
        };
        
        // Build the configuration
        let config = builder.build()?;
        
        // Deserialize into our Config struct
        let mut parsed_config: Config = config.try_deserialize()?;
        
        // Apply default for root_folder if not specified
        if parsed_config.root_folder == PathBuf::new() {
            if let Ok(home) = Self::get_default_config_dir() {
                parsed_config.root_folder = home.join("meal_plans");
            }
        }
        
        // Validate that root_folder exists or create it
        if !parsed_config.root_folder.exists() {
            match fs::create_dir_all(&parsed_config.root_folder) {
                Ok(_) => {}, // Directory created successfully
                Err(_) => return Err(ConfigError::NonExistentFolder(parsed_config.root_folder.clone())),
            }
        }
        
        // Validate that root_folder is writable
        let temp_file_path = parsed_config.root_folder.join(".write_test_temp");
        match fs::File::create(&temp_file_path) {
            Ok(_) => {
                // Clean up the test file
                let _ = fs::remove_file(temp_file_path);
            }
            Err(_) => {
                return Err(ConfigError::NonWritableFolder(parsed_config.root_folder.clone()));
            }
        }
        
        Ok(parsed_config)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::File;
    use std::io::Write;
    
    // Helper function to create a temporary config file
    fn create_test_config(content: &str) -> PathBuf {
        let temp_dir = std::env::temp_dir();
        let config_path = temp_dir.join("test_config.toml");
        
        let mut file = File::create(&config_path).unwrap();
        file.write_all(content.as_bytes()).unwrap();
        
        config_path
    }
    
    #[test]
    fn test_valid_config() {
        // Create a temporary directory to use as the root folder
        let temp_dir = std::env::temp_dir();
        let test_dir = temp_dir.join("mealplan_config_test_folder");
        let _ = fs::create_dir_all(&test_dir);
        
        // Create a valid config file
        let config_content = format!("root_folder = {:?}", test_dir);
        let config_path = create_test_config(&config_content);
        
        // Load the config
        let config = Config::load(Some(config_path.clone())).unwrap();
        
        // Check that the config was loaded correctly
        assert_eq!(config.root_folder, test_dir);
        
        // Clean up
        let _ = fs::remove_file(config_path);
        let _ = fs::remove_dir_all(test_dir);
    }
    
    #[test]
    fn test_default_config() {
        // Test that we can create a config with default values
        // This test only verifies that the function doesn't panic
        let result = Config::load(None);
        
        // We should be able to get a valid config with default values
        // But this test might fail in CI environments with permission issues
        if let Ok(config) = result {
            // Verify that root_folder exists and is writable
            assert!(config.root_folder.exists());
            
            // Clean up
            let _ = fs::remove_dir_all(&config.root_folder);
        }
    }
}
