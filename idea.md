# Meal Plan Model Context Protocol Server Idea

## 1. Configuration

- **Format:** TOML  
- **File:** `config.toml`  
- **Fields:**
```toml
rootFolder = "/path/to/meal-plans"
```

## 2. Directory Structure & File Naming

Under `rootFolder`, organize by year/month:

```
rootFolder/
└── YYYY/
    └── MM/
        └── MM-DD-YYYY/
            ├── breakfast.md
            ├── lunch.md
            ├── dinner.md
            └── snack.md
```

Directories are **created automatically** if they don’t exist.

## 3. Markdown File Format

- **Syntax:** Markdown with YAML frontmatter  
- **Frontmatter fields** (all required):
```yaml
---
date: 2025-04-17T12:00:00Z        # ISO‑8601 datetime
mealType: "lunch"                # one of: breakfast, lunch, dinner, snack (case‑insensitive)
title: "Chicken Enchiladas"      # string
cook: "Everyone"                 # string
---
```
- **Body**: for each dish in the meal, in order:
```markdown
## Dish Name

### Ingredients
- 1 chicken breast
- ½ cup rice
- …

### Instructions
1. Preheat oven to 350°F.
2. …

### Nutrients
| Nutrient            | Amount | Unit |
|---------------------|-------:|:----:|
| Total Fat           |   12.5 |  g   |
| Saturated Fat       |    2.3 |  g   |
| Cholesterol         |    85  | mg   |
| Sodium              |   320  | mg   |
| Total Carbohydrates |    30  |  g   |
| Dietary Fiber       |     4  |  g   |
| Sugars              |     3  |  g   |
| Protein             |    25  |  g   |
```

## 4. MCP Command Handlers

### 4.1 `createMealPlan`
- **Payload** (JSON):
```json
{
  "date": "2025-04-17T12:00:00Z",
  "mealType": "lunch",
  "title": "Chicken Enchiladas",
  "cook": "Everyone",
  "dishes": [
    {
      "dishName": "Chicken Enchiladas",
      "ingredients": [
        { "ingredient": "Chicken breast", "amount": "1" },
        { "ingredient": "Enchilada sauce", "amount": "½ cup" }
      ],
      "instructions": "Assemble enchiladas and bake at 350°F for 20 minutes.",
      "nutrients": [
        { "name": "Total Fat", "value": 12.5, "unit": "g" },
        { "name": "Saturated Fat", "value": 2.3, "unit": "g" }
      ]
    }
  ]
}
```
- **Response**:
```rust
McpResponse<{ success: bool, message: String }>
```
- **Errors**:
  - `BadRequest` for invalid/missing fields  
  - `BadRequest` if `mealType` not one of breakfast/lunch/dinner/snack  
  - `AlreadyExists` if file exists for date+mealType  

### 4.2 `listMealPlans`
- **Payload**:
```json
{
  "startDate": "2025-04-01T00:00:00Z",
  "endDate": "2025-04-30T23:59:59Z",
  "mealTypes": ["breakfast","dinner"],   // optional
  "cook":      "Alice"                   // optional
}
```
- **Response**:
```json
[
  {
    "date": "2025-04-17T12:00:00Z",
    "mealType": "lunch",
    "title": "Chicken Enchiladas",
    "cook": "Everyone"
  }
]
```
- **Behavior**: Inclusive of start/end dates. Malformed frontmatter only errors on view.

### 4.3 `viewMealPlanMarkdown`
- **Payload**:
```json
{
  "date": "2025-04-17T12:00:00Z",
  "mealType": "lunch"
}
```
- **Response**: raw Markdown string (full frontmatter + body)  
- **Errors**:
  - `BadRequest` for invalid fields  
  - `NotFound` if no file found  
  - `ParseError` if YAML parse fails  

### 4.4 `viewMealPlanJSON`
- **Payload**: same as `viewMealPlanMarkdown`  
- **Response**:
```json
{
  "date": "2025-04-17T12:00:00Z",
  "mealType": "lunch",
  "title": "Chicken Enchiladas",
  "cook": "Everyone",
  "dishes": [ /* same structure as create payload */ ]
}
```
- **Errors**: same as `viewMealPlanMarkdown`

### 4.5 `deleteMealPlan`
- **Payload**:
```json
{
  "date": "2025-04-17T12:00:00Z",
  "mealType": "lunch"
}
```
- **Response**:
```json
{ "success": true, "message": "Meal plan deleted" }
```
- **Errors**:
  - `BadRequest` for invalid fields  
  - `NotFound` if no file found  

## 5. Validation Rules
- `date`: ISO‑8601 string  
- `mealType`: breakfast, lunch, dinner, snack (case‑insensitive)  
- Invalid inputs → MCP `BadRequest`  
