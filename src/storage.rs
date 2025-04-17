// Storage module for the Meal Plan MCP server
use std::fs;
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
    
    #[error("Path is not a directory: {0}")]
    NotADirectory(String),
    
    #[error("Path is not writable: {0}")]
    NotWritable(String),
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
}
