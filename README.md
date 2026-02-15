# Meal Plan MCP Server

A Model Context Protocol (MCP) service implemented in Rust that provides single-user meal planning capabilities. This server allows you to create, view, list, and delete meal plans through a set of MCP command handlers, storing the data in Markdown files with YAML frontmatter.

## Features

- Create and manage meal plans for breakfast, lunch, dinner, and snacks
- Store meal plans in a structured directory hierarchy by date
- Rich meal plan format including:
  - Dish names and descriptions
  - Ingredient lists with amounts
  - Step-by-step cooking instructions
  - Nutritional information
- MCP command handlers for:
  - Creating new meal plans
  - Listing meal plans within a date range
  - Viewing meal plans in Markdown or JSON format
  - Deleting meal plans

## Directory Structure

Meal plans are organized in a hierarchical structure:

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

## Installation

### System-wide Installation

After building a release version with `cargo build --release`, you can install the application system-wide:

#### On macOS/Linux:

```bash
# Copy the binary to a directory in your PATH
sudo cp target/release/mealplan-mcp /usr/local/bin/

# Make it executable
sudo chmod +x /usr/local/bin/mealplan-mcp

# Create a default configuration directory
mkdir -p ~/.config/mealplan-mcp

# Create a default config file
cat > ~/.config/mealplan-mcp/config.toml << EOF
rootFolder = "$HOME/meal-plans"
EOF
```

#### On Windows:

```powershell
# Create a directory for the application
mkdir "$env:ProgramFiles\MealPlanMCP"

# Copy the binary
Copy-Item "target\release\mealplan-mcp.exe" "$env:ProgramFiles\MealPlanMCP\"

# Add to PATH (requires admin privileges)
$oldPath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
$newPath = $oldPath + ';' + "$env:ProgramFiles\MealPlanMCP"
[Environment]::SetEnvironmentVariable('Path', $newPath, 'Machine')

# Create a default configuration directory
mkdir "$env:APPDATA\MealPlanMCP"

# Create a default config file
@"
rootFolder = "$env:USERPROFILE\meal-plans"
"@ | Out-File -FilePath "$env:APPDATA\MealPlanMCP\config.toml" -Encoding utf8
```

### Running After Installation

After installation, you can run the application from anywhere by typing:

```bash
mealplan-mcp
```

The application will look for the configuration file in:
- macOS/Linux: `~/.config/mealplan-mcp/config.toml`
- Windows: `%APPDATA%\MealPlanMCP\config.toml`

You can override the config location by setting the `MEALPLAN_MCP_CONFIG` environment variable:

```bash
# macOS/Linux
export MEALPLAN_MCP_CONFIG=/path/to/custom/config.toml
mealplan-mcp

# Windows
set MEALPLAN_MCP_CONFIG=C:\path\to\custom\config.toml
mealplan-mcp
```

## Configuration

Create a `config.toml` file in the working directory with:

```toml
rootFolder = "/path/to/meal-plans"
```

The `rootFolder` path can be absolute or relative.

## Dependencies

- Rust 2024 edition
- Key dependencies:
  - rmcp: Model Context Protocol implementation
  - serde: Serialization/deserialization
  - config: Configuration management
  - chrono: Date/time handling
  - yaml-rust: YAML parsing
  - tokio: Async runtime

## Building

```bash
cargo build
```

## Running

```bash
cargo run
```

## Features

The project supports two feature flags:
- `use-mock` (default): Use mock MCP implementation
- `use-real-rmcp`: Use the real RMCP implementation

## License

[Add your license information here] 