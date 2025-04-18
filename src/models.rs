// Data models for the Meal Plan MCP server
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::str::FromStr;
use std::fmt;
use anyhow::Result;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum ValidationError {
    #[error("Invalid meal type: {0}")]
    InvalidMealType(String),
    
    #[error("Invalid date format: {0}")]
    InvalidDateFormat(String),
    
    #[error("Start date must be before or equal to end date")]
    StartDateAfterEndDate,
    
    #[error("Nutrient amount must be positive: {0}")]
    NegativeNutrientAmount(String),
    
    #[error("Ingredient amount cannot be empty")]
    EmptyIngredientAmount,
    
    #[error("Title cannot be empty")]
    EmptyTitle,
    
    #[error("Cook cannot be empty")]
    EmptyCook,
    
    #[error("Dish name cannot be empty")]
    EmptyDishName,
    
    #[error("Ingredient name cannot be empty")]
    EmptyIngredientName,
    
    #[error("Nutrient name cannot be empty")]
    EmptyNutrientName,
    
    #[error("Nutrient unit cannot be empty")]
    EmptyNutrientUnit,
}

/// Meal types supported by the system
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum MealType {
    Breakfast,
    Lunch,
    Dinner,
    Snack,
}

impl FromStr for MealType {
    type Err = ValidationError;
    
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "breakfast" => Ok(MealType::Breakfast),
            "lunch" => Ok(MealType::Lunch),
            "dinner" => Ok(MealType::Dinner),
            "snack" => Ok(MealType::Snack),
            _ => Err(ValidationError::InvalidMealType(s.to_string())),
        }
    }
}

impl fmt::Display for MealType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            MealType::Breakfast => write!(f, "breakfast"),
            MealType::Lunch => write!(f, "lunch"), 
            MealType::Dinner => write!(f, "dinner"),
            MealType::Snack => write!(f, "snack"),
        }
    }
}

/// Represents a nutrient with name, amount, and unit
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Nutrient {
    pub name: String,
    pub amount: f64,
    pub unit: String,
}

impl Nutrient {
    pub fn validate(&self) -> Result<(), ValidationError> {
        if self.name.trim().is_empty() {
            return Err(ValidationError::EmptyNutrientName);
        }
        
        if self.amount <= 0.0 {
            return Err(ValidationError::NegativeNutrientAmount(self.name.clone()));
        }
        
        if self.unit.trim().is_empty() {
            return Err(ValidationError::EmptyNutrientUnit);
        }
        
        Ok(())
    }
}

/// Represents an ingredient with name and amount
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Ingredient {
    pub name: String,
    pub amount: String,
}

impl Ingredient {
    pub fn validate(&self) -> Result<(), ValidationError> {
        if self.name.trim().is_empty() {
            return Err(ValidationError::EmptyIngredientName);
        }
        
        if self.amount.trim().is_empty() {
            return Err(ValidationError::EmptyIngredientAmount);
        }
        
        Ok(())
    }
}

/// Represents a dish with name, ingredients, instructions, and nutrients
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Dish {
    pub name: String,
    pub ingredients: Vec<Ingredient>,
    pub instructions: Vec<String>,
    pub nutrients: Vec<Nutrient>,
}

impl Dish {
    pub fn validate(&self) -> Result<(), ValidationError> {
        if self.name.trim().is_empty() {
            return Err(ValidationError::EmptyDishName);
        }
        
        // Validate all ingredients
        for ingredient in &self.ingredients {
            ingredient.validate()?;
        }
        
        // Validate all nutrients
        for nutrient in &self.nutrients {
            nutrient.validate()?;
        }
        
        Ok(())
    }
}

/// Represents a meal plan with date, meal type, title, cook, and dishes
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct MealPlan {
    pub date: DateTime<Utc>,
    pub meal_type: MealType,
    pub title: String,
    pub cook: String,
    pub dishes: Vec<Dish>,
}

impl MealPlan {
    pub fn validate(&self) -> Result<(), ValidationError> {
        if self.title.trim().is_empty() {
            return Err(ValidationError::EmptyTitle);
        }
        
        if self.cook.trim().is_empty() {
            return Err(ValidationError::EmptyCook);
        }
        
        // Validate all dishes
        for dish in &self.dishes {
            dish.validate()?;
        }
        
        Ok(())
    }
}

// Request and response structs for MCP commands

/// Request to create a new meal plan
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct CreateMealPlanRequest {
    pub date: DateTime<Utc>,
    pub meal_type: MealType,
    pub title: String,
    pub cook: String,
    pub dishes: Vec<Dish>,
}

impl CreateMealPlanRequest {
    pub fn validate(&self) -> Result<(), ValidationError> {
        if self.title.trim().is_empty() {
            return Err(ValidationError::EmptyTitle);
        }
        
        if self.cook.trim().is_empty() {
            return Err(ValidationError::EmptyCook);
        }
        
        // Validate all dishes
        for dish in &self.dishes {
            dish.validate()?;
        }
        
        Ok(())
    }
    
    pub fn to_meal_plan(&self) -> MealPlan {
        MealPlan {
            date: self.date,
            meal_type: self.meal_type.clone(),
            title: self.title.clone(),
            cook: self.cook.clone(),
            dishes: self.dishes.clone(),
        }
    }
}

/// Response after creating a meal plan
#[derive(Debug, Clone, Serialize)]
pub struct CreateMealPlanResponse {
    pub success: bool,
    pub message: String,
}

/// Request to list meal plans within a date range
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ListMealPlansRequest {
    pub start_date: DateTime<Utc>,
    pub end_date: DateTime<Utc>,
    pub meal_types: Option<Vec<MealType>>,
    pub cook: Option<String>,
}

impl ListMealPlansRequest {
    pub fn validate(&self) -> Result<(), ValidationError> {
        if self.start_date > self.end_date {
            return Err(ValidationError::StartDateAfterEndDate);
        }
        
        Ok(())
    }
}

/// Summary of a meal plan used in listings
#[derive(Debug, Clone, Serialize)]
pub struct MealPlanSummary {
    pub date: DateTime<Utc>,
    pub meal_type: MealType,
    pub title: String,
    pub cook: String,
}

/// Response to a list meal plans request
#[derive(Debug, Clone, Serialize)]
pub struct ListMealPlansResponse {
    pub meal_plans: Vec<MealPlanSummary>,
}

/// Request to view a meal plan in Markdown format
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ViewMealPlanMarkdownRequest {
    pub date: DateTime<Utc>,
    pub meal_type: MealType,
}

/// Request to view a meal plan in JSON format
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct ViewMealPlanJsonRequest {
    pub date: DateTime<Utc>,
    pub meal_type: MealType,
}

/// Request to delete a meal plan
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct DeleteMealPlanRequest {
    pub date: DateTime<Utc>,
    pub meal_type: MealType,
}

/// Response after deleting a meal plan
#[derive(Debug, Clone, Serialize)]
pub struct DeleteMealPlanResponse {
    pub success: bool,
    pub message: String,
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::TimeZone;
    
    #[test]
    fn test_meal_type_from_str() {
        assert_eq!(MealType::from_str("breakfast").unwrap(), MealType::Breakfast);
        assert_eq!(MealType::from_str("Lunch").unwrap(), MealType::Lunch);
        assert_eq!(MealType::from_str("DINNER").unwrap(), MealType::Dinner);
        assert_eq!(MealType::from_str("Snack").unwrap(), MealType::Snack);
        
        assert!(MealType::from_str("brunch").is_err());
        assert!(MealType::from_str("").is_err());
    }
    
    #[test]
    fn test_nutrient_validation() {
        // Valid nutrient
        let valid = Nutrient {
            name: "Protein".to_string(),
            amount: 20.0,
            unit: "g".to_string(),
        };
        assert!(valid.validate().is_ok());
        
        // Empty name
        let empty_name = Nutrient {
            name: "".to_string(),
            amount: 20.0,
            unit: "g".to_string(),
        };
        assert!(empty_name.validate().is_err());
        
        // Empty unit
        let empty_unit = Nutrient {
            name: "Protein".to_string(),
            amount: 20.0,
            unit: "".to_string(),
        };
        assert!(empty_unit.validate().is_err());
        
        // Negative amount
        let negative = Nutrient {
            name: "Protein".to_string(),
            amount: -5.0,
            unit: "g".to_string(),
        };
        assert!(negative.validate().is_err());
        
        // Zero amount
        let zero = Nutrient {
            name: "Protein".to_string(),
            amount: 0.0,
            unit: "g".to_string(),
        };
        assert!(zero.validate().is_err());
    }
    
    #[test]
    fn test_ingredient_validation() {
        // Valid ingredient
        let valid = Ingredient {
            name: "Chicken".to_string(),
            amount: "500g".to_string(),
        };
        assert!(valid.validate().is_ok());
        
        // Empty name
        let empty_name = Ingredient {
            name: "".to_string(),
            amount: "500g".to_string(),
        };
        assert!(empty_name.validate().is_err());
        
        // Empty amount
        let empty_amount = Ingredient {
            name: "Chicken".to_string(),
            amount: "".to_string(),
        };
        assert!(empty_amount.validate().is_err());
    }
    
    #[test]
    fn test_dish_validation() {
        // Valid dish
        let valid = Dish {
            name: "Chicken Curry".to_string(),
            ingredients: vec![
                Ingredient {
                    name: "Chicken".to_string(),
                    amount: "500g".to_string(),
                },
                Ingredient {
                    name: "Curry Powder".to_string(),
                    amount: "2 tbsp".to_string(),
                },
            ],
            instructions: vec![
                "Dice chicken".to_string(),
                "Add curry powder".to_string(),
            ],
            nutrients: vec![
                Nutrient {
                    name: "Protein".to_string(),
                    amount: 25.0,
                    unit: "g".to_string(),
                },
            ],
        };
        assert!(valid.validate().is_ok());
        
        // Empty name
        let empty_name = Dish {
            name: "".to_string(),
            ingredients: vec![],
            instructions: vec![],
            nutrients: vec![],
        };
        assert!(empty_name.validate().is_err());
        
        // Invalid ingredient
        let invalid_ingredient = Dish {
            name: "Chicken Curry".to_string(),
            ingredients: vec![
                Ingredient {
                    name: "".to_string(),
                    amount: "500g".to_string(),
                },
            ],
            instructions: vec![],
            nutrients: vec![],
        };
        assert!(invalid_ingredient.validate().is_err());
        
        // Invalid nutrient
        let invalid_nutrient = Dish {
            name: "Chicken Curry".to_string(),
            ingredients: vec![],
            instructions: vec![],
            nutrients: vec![
                Nutrient {
                    name: "Protein".to_string(),
                    amount: -5.0,
                    unit: "g".to_string(),
                },
            ],
        };
        assert!(invalid_nutrient.validate().is_err());
    }
    
    #[test]
    fn test_meal_plan_validation() {
        let valid_dish = Dish {
            name: "Chicken Curry".to_string(),
            ingredients: vec![
                Ingredient {
                    name: "Chicken".to_string(),
                    amount: "500g".to_string(),
                },
            ],
            instructions: vec!["Cook it".to_string()],
            nutrients: vec![
                Nutrient {
                    name: "Protein".to_string(),
                    amount: 25.0,
                    unit: "g".to_string(),
                },
            ],
        };
        
        // Valid meal plan
        let valid = MealPlan {
            date: Utc::now(),
            meal_type: MealType::Dinner,
            title: "Delicious Dinner".to_string(),
            cook: "Chef John".to_string(),
            dishes: vec![valid_dish.clone()],
        };
        assert!(valid.validate().is_ok());
        
        // Empty title
        let empty_title = MealPlan {
            date: Utc::now(),
            meal_type: MealType::Dinner,
            title: "".to_string(),
            cook: "Chef John".to_string(),
            dishes: vec![valid_dish.clone()],
        };
        assert!(empty_title.validate().is_err());
        
        // Empty cook
        let empty_cook = MealPlan {
            date: Utc::now(),
            meal_type: MealType::Dinner,
            title: "Delicious Dinner".to_string(),
            cook: "".to_string(),
            dishes: vec![valid_dish.clone()],
        };
        assert!(empty_cook.validate().is_err());
        
        // Invalid dish
        let invalid_dish = Dish {
            name: "".to_string(),
            ingredients: vec![],
            instructions: vec![],
            nutrients: vec![],
        };
        let invalid_dishes = MealPlan {
            date: Utc::now(),
            meal_type: MealType::Dinner,
            title: "Delicious Dinner".to_string(),
            cook: "Chef John".to_string(),
            dishes: vec![invalid_dish],
        };
        assert!(invalid_dishes.validate().is_err());
    }
    
    #[test]
    fn test_list_meal_plans_request_validation() {
        // Valid request with start_date before end_date
        let valid = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 1, 1, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 1, 31, 23, 59, 59).unwrap(),
            meal_types: Some(vec![MealType::Dinner]),
            cook: Some("Chef John".to_string()),
        };
        assert!(valid.validate().is_ok());
        
        // Valid request with start_date equal to end_date
        let same_day = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 1, 1, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 1, 1, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: None,
        };
        assert!(same_day.validate().is_ok());
        
        // Invalid request with start_date after end_date
        let invalid = ListMealPlansRequest {
            start_date: Utc.with_ymd_and_hms(2023, 2, 1, 0, 0, 0).unwrap(),
            end_date: Utc.with_ymd_and_hms(2023, 1, 31, 23, 59, 59).unwrap(),
            meal_types: None,
            cook: None,
        };
        assert!(invalid.validate().is_err());
    }
    
    #[test]
    fn test_create_meal_plan_request_to_meal_plan() {
        let request = CreateMealPlanRequest {
            date: Utc::now(),
            meal_type: MealType::Lunch,
            title: "Tasty Lunch".to_string(),
            cook: "Chef Mary".to_string(),
            dishes: vec![
                Dish {
                    name: "Salad".to_string(),
                    ingredients: vec![
                        Ingredient {
                            name: "Lettuce".to_string(),
                            amount: "1 head".to_string(),
                        },
                    ],
                    instructions: vec!["Wash lettuce".to_string()],
                    nutrients: vec![
                        Nutrient {
                            name: "Vitamin C".to_string(),
                            amount: 5.0,
                            unit: "mg".to_string(),
                        },
                    ],
                },
            ],
        };
        
        let meal_plan = request.to_meal_plan();
        
        assert_eq!(meal_plan.date, request.date);
        assert_eq!(meal_plan.meal_type, request.meal_type);
        assert_eq!(meal_plan.title, request.title);
        assert_eq!(meal_plan.cook, request.cook);
        assert_eq!(meal_plan.dishes.len(), request.dishes.len());
        assert_eq!(meal_plan.dishes[0].name, request.dishes[0].name);
    }
}
