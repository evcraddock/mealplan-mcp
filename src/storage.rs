// Storage module for the Meal Plan MCP server
use std::fs;
use std::io::{Read, Write};
use std::path::{Path, PathBuf};
use chrono::{DateTime, Datelike, Utc};
use anyhow::Result;
use thiserror::Error;

use crate::models::MealType;

#[derive(Error, Debug)]
pub enum StorageError {
    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),
    
    #[error("Path does not exist: {0}")]
    NonExistentPath(String),
    
    #[error("File not found: {0}")]
    FileNotFound(PathBuf),
}

/// Computes the directory path for a meal plan
/// Format: rootFolder/YYYY/MM/MM-DD-YYYY/
pub fn compute_directory_path(date: &DateTime<Utc>, root_folder: &Path) -> PathBuf {
    let year = date.year();
    let month = date.month();
    let day = date.day();
    
    let year_str = format!("{}", year);
    let month_str = format!("{:02}", month);
    let day_str = format!("{:02}", day);
    
    let dir_name = format!("{}-{}-{}", month_str, day_str, year);
    
    root_folder
        .join(year_str)
        .join(month_str)
        .join(dir_name)
}

/// Computes the file path for a meal plan
/// Format: rootFolder/YYYY/MM/MM-DD-YYYY/{mealType}.md
pub fn compute_file_path(date: &DateTime<Utc>, meal_type: &MealType, root_folder: &Path) -> PathBuf {
    let dir_path = compute_directory_path(date, root_folder);
    let filename = format!("{}.md", meal_type.to_string());
    
    dir_path.join(filename)
}

/// Ensures all required directories exist for the given path
/// Creates any missing directories in the path
pub fn ensure_directories_exist(path: &Path) -> Result<(), StorageError> {
    // Get the parent directory of the path
    let parent = match path.parent() {
        Some(p) => p,
        None => return Ok(()), // No parent means it's already at root
    };
    
    // Create all directories in the path
    fs::create_dir_all(parent)?;
    
    Ok(())
}

/// Writes content to a meal plan file
/// Creates necessary directories if they don't exist
pub fn write_meal_plan(content: &str, date: &DateTime<Utc>, meal_type: &MealType, root_folder: &Path) -> Result<(), StorageError> {
    let file_path = compute_file_path(date, meal_type, root_folder);
    
    // Ensure directories exist
    ensure_directories_exist(&file_path)?;
    
    // Write content to file
    let mut file = fs::File::create(&file_path)?;
    file.write_all(content.as_bytes())?;
    
    Ok(())
}

/// Reads content from a meal plan file
/// Returns an error if the file doesn't exist
pub fn read_meal_plan(date: &DateTime<Utc>, meal_type: &MealType, root_folder: &Path) -> Result<String, StorageError> {
    let file_path = compute_file_path(date, meal_type, root_folder);
    
    // Check if file exists
    if !file_path.exists() {
        return Err(StorageError::FileNotFound(file_path));
    }
    
    // Read file content
    let mut file = fs::File::open(&file_path)?;
    let mut content = String::new();
    file.read_to_string(&mut content)?;
    
    Ok(content)
}

/// Checks if a meal plan file exists
pub fn meal_plan_exists(date: &DateTime<Utc>, meal_type: &MealType, root_folder: &Path) -> bool {
    let file_path = compute_file_path(date, meal_type, root_folder);
    file_path.exists()
}

/// Deletes a meal plan file if it exists
pub fn delete_meal_plan(date: &DateTime<Utc>, meal_type: &MealType, root_folder: &Path) -> Result<(), StorageError> {
    let file_path = compute_file_path(date, meal_type, root_folder);
    
    // Check if file exists
    if !file_path.exists() {
        return Err(StorageError::FileNotFound(file_path));
    }
    
    // Delete the file
    fs::remove_file(&file_path)?;
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::TimeZone;
    use std::fs;
    use std::io::Write;
    use tempfile::tempdir;
    
    #[test]
    fn test_compute_directory_path() {
        let root = PathBuf::from("/tmp/mealplans");
        
        // Test for January 1, 2023
        let date1 = Utc.with_ymd_and_hms(2023, 1, 1, 0, 0, 0).unwrap();
        let expected1 = PathBuf::from("/tmp/mealplans/2023/01/01-01-2023");
        assert_eq!(compute_directory_path(&date1, &root), expected1);
        
        // Test for December 25, 2023
        let date2 = Utc.with_ymd_and_hms(2023, 12, 25, 0, 0, 0).unwrap();
        let expected2 = PathBuf::from("/tmp/mealplans/2023/12/12-25-2023");
        assert_eq!(compute_directory_path(&date2, &root), expected2);
        
        // Test for February 29, 2024 (leap year)
        let date3 = Utc.with_ymd_and_hms(2024, 2, 29, 0, 0, 0).unwrap();
        let expected3 = PathBuf::from("/tmp/mealplans/2024/02/02-29-2024");
        assert_eq!(compute_directory_path(&date3, &root), expected3);
    }
    
    #[test]
    fn test_compute_file_path() {
        let root = PathBuf::from("/tmp/mealplans");
        
        // Test for breakfast on January 1, 2023
        let date1 = Utc.with_ymd_and_hms(2023, 1, 1, 0, 0, 0).unwrap();
        let expected1 = PathBuf::from("/tmp/mealplans/2023/01/01-01-2023/breakfast.md");
        assert_eq!(compute_file_path(&date1, &MealType::Breakfast, &root), expected1);
        
        // Test for dinner on December 25, 2023
        let date2 = Utc.with_ymd_and_hms(2023, 12, 25, 0, 0, 0).unwrap();
        let expected2 = PathBuf::from("/tmp/mealplans/2023/12/12-25-2023/dinner.md");
        assert_eq!(compute_file_path(&date2, &MealType::Dinner, &root), expected2);
        
        // Test for lunch on February 29, 2024 (leap year)
        let date3 = Utc.with_ymd_and_hms(2024, 2, 29, 0, 0, 0).unwrap();
        let expected3 = PathBuf::from("/tmp/mealplans/2024/02/02-29-2024/lunch.md");
        assert_eq!(compute_file_path(&date3, &MealType::Lunch, &root), expected3);
        
        // Test for snack
        let date4 = Utc.with_ymd_and_hms(2023, 7, 4, 0, 0, 0).unwrap();
        let expected4 = PathBuf::from("/tmp/mealplans/2023/07/07-04-2023/snack.md");
        assert_eq!(compute_file_path(&date4, &MealType::Snack, &root), expected4);
    }
    
    #[test]
    fn test_ensure_directories_exist() {
        // Create a temporary directory for testing
        let temp_dir = tempdir().unwrap();
        let temp_path = temp_dir.path();
        
        // Define a file path within several nested directories
        let nested_path = temp_path.join("a/b/c/test.md");
        
        // Ensure the directories exist
        ensure_directories_exist(&nested_path).unwrap();
        
        // Verify that the directories were created
        assert!(temp_path.join("a").exists());
        assert!(temp_path.join("a/b").exists());
        assert!(temp_path.join("a/b/c").exists());
        
        // Verify that the file doesn't exist yet (we only create directories)
        assert!(!nested_path.exists());
        
        // Create the file to test everything works properly
        let mut file = fs::File::create(&nested_path).unwrap();
        writeln!(file, "Test content").unwrap();
        
        // Verify the file exists now
        assert!(nested_path.exists());
    }
    
    #[test]
    fn test_write_and_read_meal_plan() {
        // Create a temporary directory for testing
        let temp_dir = tempdir().unwrap();
        let root_folder = temp_dir.path();
        
        // Create test data
        let date = Utc.with_ymd_and_hms(2023, 5, 15, 0, 0, 0).unwrap();
        let meal_type = MealType::Lunch;
        let content = "This is a test meal plan content";
        
        // Write meal plan
        write_meal_plan(content, &date, &meal_type, root_folder).unwrap();
        
        // Verify the file exists
        let file_path = compute_file_path(&date, &meal_type, root_folder);
        assert!(file_path.exists());
        
        // Read meal plan
        let read_content = read_meal_plan(&date, &meal_type, root_folder).unwrap();
        
        // Verify content
        assert_eq!(read_content, content);
    }
    
    #[test]
    fn test_read_nonexistent_meal_plan() {
        // Create a temporary directory for testing
        let temp_dir = tempdir().unwrap();
        let root_folder = temp_dir.path();
        
        // Create test data for a file that doesn't exist
        let date = Utc.with_ymd_and_hms(2023, 6, 20, 0, 0, 0).unwrap();
        let meal_type = MealType::Dinner;
        
        // Attempt to read non-existent meal plan
        let result = read_meal_plan(&date, &meal_type, root_folder);
        
        // Verify the error
        assert!(result.is_err());
        match result {
            Err(StorageError::FileNotFound(_)) => (),
            _ => panic!("Expected FileNotFound error"),
        }
    }
    
    #[test]
    fn test_meal_plan_exists() {
        // Create a temporary directory for testing
        let temp_dir = tempdir().unwrap();
        let root_folder = temp_dir.path();
        
        // Create test data
        let date = Utc.with_ymd_and_hms(2023, 7, 10, 0, 0, 0).unwrap();
        let meal_type = MealType::Breakfast;
        let content = "Test breakfast content";
        
        // Initially the meal plan should not exist
        assert!(!meal_plan_exists(&date, &meal_type, root_folder));
        
        // Write the meal plan
        write_meal_plan(content, &date, &meal_type, root_folder).unwrap();
        
        // Now the meal plan should exist
        assert!(meal_plan_exists(&date, &meal_type, root_folder));
    }
    
    #[test]
    fn test_delete_meal_plan() {
        // Create a temporary directory for testing
        let temp_dir = tempdir().unwrap();
        let root_folder = temp_dir.path();
        
        // Create test data
        let date = Utc.with_ymd_and_hms(2023, 8, 5, 0, 0, 0).unwrap();
        let meal_type = MealType::Snack;
        let content = "Test snack content";
        
        // Write the meal plan
        write_meal_plan(content, &date, &meal_type, root_folder).unwrap();
        
        // Verify the file exists
        assert!(meal_plan_exists(&date, &meal_type, root_folder));
        
        // Delete the meal plan
        delete_meal_plan(&date, &meal_type, root_folder).unwrap();
        
        // Verify the file no longer exists
        assert!(!meal_plan_exists(&date, &meal_type, root_folder));
    }
    
    #[test]
    fn test_delete_nonexistent_meal_plan() {
        // Create a temporary directory for testing
        let temp_dir = tempdir().unwrap();
        let root_folder = temp_dir.path();
        
        // Create test data for a file that doesn't exist
        let date = Utc.with_ymd_and_hms(2023, 9, 15, 0, 0, 0).unwrap();
        let meal_type = MealType::Lunch;
        
        // Attempt to delete non-existent meal plan
        let result = delete_meal_plan(&date, &meal_type, root_folder);
        
        // Verify the error
        assert!(result.is_err());
        match result {
            Err(StorageError::FileNotFound(_)) => (),
            _ => panic!("Expected FileNotFound error"),
        }
    }
}
