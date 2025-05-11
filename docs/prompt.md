# Mealplan MCP – Code‑Generation Prompt Pack

Below are **35 atomic prompts** you can feed one‑by‑one to your favourite code‑generation LLM.
Each is self‑contained, test‑driven, and ends with a green build.

---

### ✅ Prompt 1 – Project Scaffolding
```text
You are a senior Python dev.
Goal: create project skeleton for "mealplan-mcp".
Tasks:
1. Generate a pyproject.toml using uv.
2. Add deps: fastapi, pydantic, python-slugify, rich.
3. Dev-deps: pytest, pytest-cov, ruff, black, pyright, httpx, coverage-badger.
4. Create `.pre-commit-config.yaml` with black+ruff hooks.
Return ONLY the file tree (prefix paths with `📄`), and the contents of pyproject.toml and pre-commit file.
```

### ✅ Prompt 2 – CI Workflow
```text
Extend previous repo.
Add `.github/workflows/ci.yml` that:
- Runs on push + PR.
- Uses uv for dependency management.
- Installs deps, runs `ruff`, `black --check`, `pytest --cov`.
- Fails if coverage < 90 %.
Return the yaml file only.
```

### ✅ Prompt 3 – slugify() Unit Tests
```text
Add `tests/test_slugify.py` with pytest parametrized cases:
(" Chili  Con Carne! ", "chili-con-carne")
("Spätzle & Käse", "spatzle-kase")
("x"*120, "x"*100)
Ensure test fails (slugify not implemented). Output the test file only.
```

### ✅ Prompt 4 – slugify Implementation
```text
Implement `mealplan_mcp.utils.slugify`:
- Lowercase, trim, strip non-ASCII, collapse whitespace → dash.
- Collapse dashes. Trim to 100 chars.
- Provide suffix_if_exists(slug, existing_set) helper.
Return updated file. All tests must pass.
```

### ✅ Prompt 5 – Path Builders
```text
Create `mealplan_mcp.utils.paths` with:
- mealplan_root = Path(os.environ["MEALPLANPATH"])
- def dish_path(slug): return mealplan_root/"dishes"/f"{slug}.json"
- def grocery_path(start, end): ...
Write tests for each.
```

### ✅ Prompt 6 – Ignored Ingredients Model Tests
```text
Create `tests/ignored/test_model.py` covering:
- Loading empty / missing ignored_ingredients.json → []
- Loading file with ["salt","pepper"] → list[str]
- Saving persists lowercase unique list
Return test file only.
```

### ✅ Prompt 7 – Ignored Ingredients Model Impl
```text
Implement `mealplan_mcp.models.ignored` with:
- class IgnoredStore(Path): load(), save(), add(ingredient)
- Uses utils.paths.mealplan_root
All tests green.
```

### ✅ Prompt 8 – add_ignored_ingredient Service Tests
```text
Add `tests/ignored/test_add_service.py`:
- Blank string → ValueError
- " Salt " -> trimmed+lowercased saved once
- Duplicate ignored gracefully
```

### ✅ Prompt 9 – add_ignored_ingredient Service Impl
```text
Implement `mealplan_mcp.services.ignored.add_ingredient(name:str)`:
- Apply cleaning rules
- Persist via IgnoredStore
Return service file; tests pass.
```

### Prompt 10 – get_ignored_ingredients Service Tests
```text
Add tests ensuring get_ignored_ingredients returns sorted list of strings.
```

### Prompt 11 – get_ignored_ingredients Service Impl
```text
Implement service; reuse IgnoredStore.load(); tests pass.
```

### Prompt 12 – MCP Ignored Tools Contract Tests
```text
Using MCP test client, assert:
add_ignored_ingredient({"name":"salt"}) -> {"ok":"Saved"}
get_ignored_ingredients() -> ["salt"]
```

### Prompt 13 – MCP Ignored Tools Implementation
```text
Create `mealplan_mcp.tools.ignored` providing two MCP tools:
- add_ignored_ingredient
- get_ignored_ingredients
Both properly wired to their respective services.
```

### Prompt 14 – Dish Schema Unit Tests
```text
Add `tests/dish/test_schema.py`:
- Valid JSON passes
- Name cleaning / slug generation rules verified
- >100 char name truncated
```

### Prompt 15 – Dish Schema Impl
```text
Implement `mealplan_mcp.models.dish.Dish` Pydantic model with clean() + slug property.
```

### Prompt 16 – store_dish Service Tests
```text
Add happy‑path: new dish stored to dishes/{slug}.json
Add collision: second dish same slug gets -1 suffix.
```

### Prompt 17 – store_dish Service Impl
```text
Implement `mealplan_mcp.services.dish.store(dish_json)` returning file path. Use atomic write.
```

### Prompt 18 – list_dishes Service Tests
```text
Ensure alphabetical natural sort by internal name. Corrupt JSON skipped.
```

### Prompt 19 – list_dishes Service Impl
```text
Implement listing; reuse utils.paths; tests green.
```

### Prompt 20 – MCP Dish Tools Contract Tests
```text
Test:
store_dish({...}) -> {"ok":"dishes/chili.json"}
list_dishes()     -> [...]
```

### Prompt 21 – MCP Dish Tools Implementation
```text
Create `mealplan_mcp.tools.dish` providing two MCP tools:
- store_dish
- list_dishes
Both properly wired to their respective services.
```

### Prompt 22 – Markdown Renderer Skeleton Tests
```text
Add tests for `mealplan_mcp.renderers.grocery.header(date)` -> "## 2025-05-10"
```

### Prompt 23 – Renderer Ingredient Expansion Impl
```text
Implement per‑dish block respecting order and checkbox format.
```

### Prompt 24 – grocery_path Logic Tests
```text
Assert grocery_path("2025-05-10","2025-05-17") returns YYYY/MM-MonthName/2025-05-10_to_2025-05-17.md
```

### Prompt 25 – Grocery Generator Impl
```text
Service: generate_grocery_list(start,end):
- Reads meal plan JSONs
- Renders markdown
- Writes file, returns relative path
```

### Prompt 26 – MCP Grocery List Tool Test
```text
generate_grocery_list({"start":"2025-05-10","end":"2025-05-17"}) -> {"ok":".../to_...md"}
```

### Prompt 27 – MCP Grocery List Tool Implementation
```text
Create `mealplan_mcp.tools.grocery` providing:
- generate_grocery_list
Properly wired to its service.
```

### Prompt 28 – MCP Server Integration Tests
```text
tests/e2e/test_mcp.py verifies that:
- All 5 MCP tools are registered
- Tools can be called via the MCP protocol
```

### Prompt 29 – MCP Server Implementation
```text
Create `mealplan_mcp.server` with:
- MCP server configuration
- Registration of all 5 tools
- Export of a runnable MCP server instance
```

### Prompt 30 – MCP End-to-End Workflow Tests
```text
Run through full MCP tool workflow:
- store_dish with a sample dish
- add_ignored_ingredient with an ingredient
- generate_grocery_list using the dish and respecting ignored ingredients
```

### Prompt 31 – Coverage Badge Job
```text
Update CI to push coverage badge to README on main.
```

### Prompt 32 – README Update
```text
Generate quick‑start, API examples, local dev guide.
```

### Prompt 33 – CONTRIBUTING & Makefile
```text
Add CONTRIBUTING.md with commit style guide; Makefile with common tasks.
```

### Prompt 34 – Docs Site Build
```text
Add MkDocs config, gh-pages deploy workflow.
```

### Prompt 35 – Release Automation
```text
Add GitHub Action that tags semantic version on main if tests+coverage pass and pyproject version bumped.
```
